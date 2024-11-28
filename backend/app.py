import os
from flask import Flask, render_template, send_from_directory, request, jsonify, send_file
from utils.image_utils import load_model, detect_objects, draw_boxes

# Khởi tạo Flask app
app = Flask(
    __name__,
    static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/public')),  # Đảm bảo đường dẫn đúng
    template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/public'))  # Đảm bảo đường dẫn đúng
)

# Cấu hình thư mục lưu file tải lên và kết quả xử lý
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Đường dẫn tuyệt đối của thư mục chứa app.py
app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(BASE_DIR, '../uploads'))  # Thư mục 'uploads'
PROCESSED_FOLDER = os.path.abspath(os.path.join(BASE_DIR, '../processed'))  # Thư mục 'processed'

# Đảm bảo thư mục 'uploads' tồn tại
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])  # Tạo thư mục nếu chưa tồn tại

# Đảm bảo thư mục 'processed' tồn tại
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)  # Tạo thư mục nếu chưa tồn tại

# Load model YOLOv8 khi server khởi động
model = load_model()

# Route cho favicon.ico
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Route cho trang chủ
@app.route('/')
def index():
    return render_template('index.html')

# Route xử lý tải ảnh và nhận diện vật thể
@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Thực hiện nhận diện vật thể
        detections, classes, _ = detect_objects(file_path, model)
        detections = detections.tolist()
        class_ids = classes.tolist()

        # Lấy tên lớp từ `model.names`
        class_names = [model.names[int(cls_id)] for cls_id in class_ids]

        # Lưu ảnh kết quả
        result_path = os.path.join(PROCESSED_FOLDER, 'result.jpg')
        result_path = draw_boxes(file_path, detections, class_ids, model, PROCESSED_FOLDER)

        # Trả về đường dẫn và danh sách tên lớp
        result_url = f"/processed/result.jpg"
        return jsonify({
            'objects': class_names,  # Tên các vật thể
            'image_url': result_url  # Đường dẫn đến ảnh kết quả
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred while processing the file.'}), 500

@app.route('/processed/<path:filename>')
def processed_file(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)



# Chạy ứng dụng Flask
if __name__ == "__main__":
    app.run(debug=True)
