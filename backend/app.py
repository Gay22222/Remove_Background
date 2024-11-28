import os
from flask import Flask, render_template, send_from_directory, request, jsonify, send_file
from utils.image_utils import load_model, detect_objects, draw_boxes

# Khởi tạo Flask app với đường dẫn tĩnh và template được cấu hình
app = Flask(
    __name__,
    static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/public')),  # Thư mục chứa file tĩnh (CSS, JS, favicon, v.v.)
    template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/public'))  # Thư mục chứa template HTML
)

# Cấu hình thư mục lưu file tải lên và kết quả xử lý
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Lấy đường dẫn tuyệt đối của thư mục chứa file `app.py`
app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(BASE_DIR, '../uploads'))  # Thư mục lưu file người dùng tải lên
PROCESSED_FOLDER = os.path.abspath(os.path.join(BASE_DIR, '../processed'))  # Thư mục lưu file ảnh sau khi xử lý

# Đảm bảo thư mục 'uploads' tồn tại
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])  # Tạo thư mục nếu chưa tồn tại

# Đảm bảo thư mục 'processed' tồn tại
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)  # Tạo thư mục nếu chưa tồn tại

# Load model YOLOv8 khi server khởi động
model = load_model()

# Route xử lý favicon.ico để hiển thị biểu tượng của website
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Route cho trang chủ
@app.route('/')
def index():
    return render_template('index.html')  # Render giao diện chính (index.html)

# Route xử lý tải ảnh và nhận diện vật thể
@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        # Kiểm tra xem file có được gửi từ request không
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        # Lấy file từ request và lưu vào thư mục 'uploads'
        file = request.files['file']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Gọi hàm detect_objects để nhận diện vật thể trong ảnh
        detections, classes, _ = detect_objects(file_path, model)
        detections = detections.tolist()  # Chuyển đổi bounding boxes từ tensor sang list
        class_ids = classes.tolist()  # Chuyển đổi class IDs từ tensor sang list

        # Lấy tên vật thể từ `model.names` dựa vào class IDs
        class_names = [model.names[int(cls_id)] for cls_id in class_ids]

        # Lưu ảnh kết quả với các bounding boxes đã được vẽ
        result_path = os.path.join(PROCESSED_FOLDER, 'result.jpg')
        result_path = draw_boxes(file_path, detections, class_ids, model, PROCESSED_FOLDER)

        # Trả về JSON chứa đường dẫn ảnh kết quả và danh sách các vật thể nhận diện được
        result_url = f"/processed/result.jpg"
        return jsonify({
            'objects': class_names,  # Danh sách tên các vật thể
            'image_url': result_url  # Đường dẫn đến ảnh kết quả
        })

    except Exception as e:
        # Log lỗi chi tiết và trả về thông báo lỗi dưới dạng JSON
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred while processing the file.'}), 500

# Route để phục vụ các file trong thư mục 'processed'
@app.route('/processed/<path:filename>')
def processed_file(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)  # Trả về file từ thư mục 'processed'

# Khởi chạy ứng dụng Flask
if __name__ == "__main__":
    app.run(debug=True)  # Chạy ứng dụng với chế độ debug (tự động reload khi có thay đổi code)
