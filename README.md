# Remove_Background


Tạo môi trường ảo

python -m venv venv


Windows:

venv\Scripts\activate


MacOS/Linux:

source venv/bin/activate


Cài đặt các gói yêu cầu

pip install -r requirements.txt

Mô hình DeepFillv2 cần có các trọng số được huấn luyện trước [tại đây](https://drive.google.com/u/0/uc?id=1L63oBNVgz7xSb_3hGbUdkYW1IuRgMkCa&export=download) được cung cấp bởi [repo](https://github.com/nipponjo/deepfillv2-pytorch) . Đây là bản tái triển khai của DeepFillv2 trong Pytroch. Mã cho mô hình DeepFillv2 được mượn và sửa đổi một chút từ đó.

Đảm bảo đặt tệp pth trọng số trong [src/models/](/backend/models)

Chạy lệnh sau để khởi động server Flask:

python backend/app.py

Mặc định, ứng dụng sẽ chạy trên http://127.0.0.1:5000