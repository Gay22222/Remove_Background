import os
import torch
from flask import Flask, render_template, send_from_directory, request, jsonify
from models.yolov8 import load_yolov8_model, detect_objects  # Chuyển sang yolov8.py
from models.mask_rcnn import load_mask_rcnn_model, detect_mask  # Cập nhật từ mask_rcnn.py
from models.deepFill import Generator
from utils.image_utils import draw_boxes  # Giữ lại draw_boxes từ image_utils
from utils.object_utils import create_mask, apply_mask
import numpy as np
from PIL import Image
# Khởi tạo ứng dụng Flask
app = Flask(
    __name__,
    static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/public')),
    template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/public'))
)

# Cấu hình thư mục
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, '../uploads')
PROCESSED_FOLDER = os.path.join(BASE_DIR, '../processed')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

# Tải các mô hình YOLOv8, Mask-RCNN và DeepFill
yolo_model = load_yolov8_model()  # Tải YOLOv8
mask_rcnn_model, mask_rcnn_transforms = load_mask_rcnn_model()  # Tải Mask-RCNN và transform
deepfill = Generator(checkpoint="backend/models/states_pt_places2.pth")  # Tải DeepFill

@app.route('/')
def index():
    # Trang chủ
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    """
    Nhận ảnh tải lên, nhận diện vật thể bằng YOLOv8 và vẽ bounding boxes.
    """
    try:
        file = request.files['file']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Nhận diện vật thể bằng YOLOv8
        detections, classes, _ = detect_objects(file_path, yolo_model)

        # Nếu detections và classes đã là list, không cần gọi .tolist()
        class_ids = classes  # Sử dụng trực tiếp
        class_names = [yolo_model.names[int(cls_id)] for cls_id in class_ids]  # Lấy tên lớp

        # Vẽ bounding boxes và lưu ảnh kết quả
        result_path = draw_boxes(file_path, detections, class_ids, yolo_model, PROCESSED_FOLDER)
        result_url = f"/processed/result.jpg"
        print("Detected objects:", class_names)
        print("Image URL:", result_url)

        
        return jsonify({
            'objects': class_names,  # Danh sách tên các vật thể
            'image_url': result_url  # Đường dẫn ảnh kết quả
        })

    except Exception as e:
        # Xử lý lỗi
        return jsonify({'error': str(e)}), 500


@app.route('/remove_object', methods=['POST'])
def remove_object():
    """
    Xóa vật thể trong ảnh sử dụng Mask-RCNN và DeepFill.
    """
    try:
        data = request.get_json()
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], data['filename'])
        object_to_remove = data['object']  # Đối tượng cần xóa

        # Kiểm tra file tồn tại
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404

        print("Object to remove:", object_to_remove)

        # Tạo mask bằng hàm create_mask từ object_utils.py
        mask = create_mask(file_path, object_to_remove, mask_rcnn_model, mask_rcnn_transforms)
        if mask is None:
            return jsonify({'error': 'Object not found in image'}), 400

        print(f"Mask created with shape: {mask.shape}")

        # Chuẩn hóa mask và lưu thành file
        normalized_mask = (mask * 255).astype(np.uint8)
        mask_path = os.path.join(PROCESSED_FOLDER, "mask.png")
        Image.fromarray(normalized_mask).save(mask_path)
        print(f"Mask saved to: {mask_path}")

        # Đọc lại ảnh gốc và mask từ file
        original_image = np.array(Image.open(file_path).convert("RGB"))
        mask_image = np.array(Image.open(mask_path)) / 255.0

        # Áp dụng mask lên ảnh bằng hàm apply_mask
        masked_image = apply_mask(original_image, mask_image)
        print(f"Applied mask to image. Masked image shape: {masked_image.shape}")

        # Chuyển masked_image sang torch.Tensor
        import torch
        image_tensor = torch.tensor(masked_image / 255.0, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0)
        mask_tensor = torch.tensor(mask_image, dtype=torch.float32).unsqueeze(0).unsqueeze(0)

        print("Image tensor shape:", image_tensor.shape)
        print("Mask tensor shape:", mask_tensor.shape)

        # Xóa đối tượng bằng DeepFill
        result = deepfill.infer(image=image_tensor[0], mask=mask_tensor[0], return_vals=['inpainted'])
        result_path = os.path.join(PROCESSED_FOLDER, 'removed.jpg')

        # Lưu ảnh kết quả
        Image.fromarray(result[0]).save(result_path)
        print(f"Result saved to: {result_path}")

        return jsonify({
            'image_url': '/processed/removed.jpg'
        }), 200

    except Exception as e:
        print(f"Error in /remove_object: {e}")
        return jsonify({'error': str(e)}), 500









@app.route('/processed/<path:filename>')
def processed_file(filename):
    """
    Trả về file kết quả từ thư mục processed.
    """
    try:
        print("Requested file:", filename)
        return send_from_directory(PROCESSED_FOLDER, filename)
    
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404


if __name__ == "__main__":
    app.run(debug=True)
