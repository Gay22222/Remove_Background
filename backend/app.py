import os
from flask import Flask, render_template, send_from_directory, request, jsonify
from models.yolov8 import load_yolov8_model, detect_objects
from models.mask_rcnn import load_mask_rcnn_model
from models.deepFill import Generator
from utils.image_utils import draw_boxes, expand_bounding_boxes
from utils.object_utils import create_mask, apply_mask
import numpy as np
from PIL import Image
import shutil

# Khởi tạo ứng dụng Flask, định nghĩa thư mục chứa tệp giao diện và tài nguyên
app = Flask(
    __name__,
    static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/public')),
    template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/public'))
)

# Cấu hình thư mục uploads (lưu ảnh tải lên) và processed (lưu ảnh kết quả)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, '../uploads')
PROCESSED_FOLDER = os.path.join(BASE_DIR, '../processed')

# Tạo các thư mục nếu chưa tồn tại
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

# Tải các mô hình YOLO, Mask-RCNN, và DeepFill
yolo_model = load_yolov8_model()
mask_rcnn_model, mask_rcnn_transforms = load_mask_rcnn_model()
deepfill = Generator(checkpoint="backend/models/states_pt_places2.pth")

@app.route('/')
def index():
    # Trả về giao diện chính
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    """
    Xử lý tải ảnh lên từ người dùng, nhận diện vật thể, và trả về bounding boxes.
    """
    try:
        # Lấy tệp tin từ yêu cầu POST
        file = request.files['file']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Nhận diện vật thể bằng YOLO
        detections, classes, _ = detect_objects(file_path, yolo_model)

        # Kiểm tra nếu không có vật thể nào được nhận diện
        if len(detections) == 0:
            raise Exception("No objects detected in the image.")

        # Lấy kích thước ảnh và mở rộng bounding boxes
        image_shape = Image.open(file_path).size[::-1]  # Định dạng (height, width)
        expanded_boxes = expand_bounding_boxes(detections, image_shape, scale=0.1)

        # Chuẩn bị danh sách đối tượng để gửi về client
        objects = []
        for idx, (box, expanded_box) in enumerate(zip(detections, expanded_boxes)):
            objects.append({
                "id": str(idx + 1),
                "name": yolo_model.names[int(classes[idx])],
                "box": expanded_box
            })

        # Vẽ bounding boxes trên ảnh và lưu kết quả
        result_path = draw_boxes(file_path, expanded_boxes, classes, yolo_model, PROCESSED_FOLDER)
        result_url = f"/processed/{os.path.basename(result_path)}"

        # Trả về danh sách đối tượng và đường dẫn ảnh kết quả
        return jsonify({"objects": objects, "image_url": result_url})

    except Exception as e:
        # Trả về lỗi nếu quá trình nhận diện thất bại
        return jsonify({'error': str(e)}), 500

@app.route('/remove_object', methods=['POST'])
def remove_object():
    """
    Xóa các đối tượng đã chọn trong ảnh bằng Mask-RCNN và DeepFill.
    """
    try:
        # Lấy thông tin từ yêu cầu POST
        data = request.get_json()
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], data['filename'])
        selected_ids = list(map(int, data['objects']))
        bounding_boxes = data['bounding_boxes']

        # Kiểm tra bounding boxes có hợp lệ không
        if not bounding_boxes or len(bounding_boxes) != len(selected_ids):
            raise ValueError("Bounding boxes không khớp với danh sách ID được chọn.")

        # Tạo mặt nạ kết hợp từ bounding boxes
        combined_mask = create_mask(file_path, bounding_boxes, mask_rcnn_model, mask_rcnn_transforms)
        if combined_mask is None:
            raise ValueError("Failed to create a valid mask for the selected objects.")

        # Lưu mặt nạ để kiểm tra
        mask_path = os.path.join(PROCESSED_FOLDER, 'mask.png')
        Image.fromarray((combined_mask * 255).astype(np.uint8)).save(mask_path)

        # Đọc ảnh gốc và chuẩn bị dữ liệu cho DeepFill
        original_image = np.array(Image.open(file_path).convert("RGB"))
        mask_image = np.array(Image.open(mask_path)) / 255.0
        masked_image = apply_mask(original_image, mask_image)

        # Chuyển dữ liệu sang torch.Tensor
        import torch
        image_tensor = torch.tensor(masked_image / 255.0, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0)
        mask_tensor = torch.tensor(mask_image, dtype=torch.float32).unsqueeze(0).unsqueeze(0)

        # Sử dụng DeepFill để điền vào vùng bị xóa
        result = deepfill.infer(image=image_tensor[0], mask=mask_tensor[0], return_vals=['inpainted'])
        result_path = os.path.join(PROCESSED_FOLDER, 'removed.jpg')

        # Lưu ảnh kết quả
        Image.fromarray(result[0]).save(result_path)

        # Trả về đường dẫn ảnh đã xóa đối tượng
        return jsonify({'image_url': '/processed/removed.jpg'}), 200

    except Exception as e:
        # Trả về lỗi nếu có sự cố trong quá trình xóa
        print(f"Error in /remove_object: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/processed/<path:filename>')
def processed_file(filename):
    """
    Cung cấp tệp đã xử lý từ thư mục processed.
    """
    try:
        return send_from_directory(PROCESSED_FOLDER, filename)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

@app.route('/reset', methods=['POST'])
def reset():
    """
    Xóa tất cả tệp trong thư mục processed và uploads.
    """
    try:
        # Xóa tệp trong thư mục processed
        if os.path.exists(PROCESSED_FOLDER):
            for file in os.listdir(PROCESSED_FOLDER):
                file_path = os.path.join(PROCESSED_FOLDER, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

        # Xóa tệp trong thư mục uploads
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            for file in os.listdir(app.config['UPLOAD_FOLDER']):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

        # Trả về thông báo hoàn thành
        return jsonify({'message': 'Reset completed successfully.'}), 200
    except Exception as e:
        # Trả về lỗi nếu reset thất bại
        print(f"Error in /reset: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    # Chạy ứng dụng Flask
    app.run(debug=True)
