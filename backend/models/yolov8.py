import torch
from ultralytics import YOLO

def load_yolov8_model(model_path='yolov8n.pt'):
    """
    Tải mô hình YOLOv8.

    Args:
        model_path (str): Đường dẫn đến file trọng số của mô hình (YOLOv8).

    Returns:
        model: Đối tượng YOLOv8 đã được tải.
    """
    model = YOLO(model_path)  # Tải trọng số YOLOv8
    return model

def detect_objects(image_path, model):
    """
    Nhận diện vật thể trong ảnh bằng YOLOv8.

    Args:
        image_path (str): Đường dẫn đến file ảnh cần nhận diện.
        model: Đối tượng YOLOv8 đã được tải.

    Returns:
        detections (list): Danh sách bounding boxes của các vật thể.
        classes (list): Danh sách class IDs của các vật thể.
        confidences (list): Danh sách độ tin cậy tương ứng với các vật thể.
    """
    # Dự đoán các vật thể trong ảnh
    results = model(image_path)
    
    # Khởi tạo các danh sách để lưu kết quả
    detections = []
    classes = []
    confidences = []

    # Duyệt qua kết quả và lưu thông tin bounding box, class và confidence
    for result in results[0].boxes.data:
        bbox, cls, conf = result[:4], result[5].item(), result[4].item()
        detections.append(bbox.tolist())  # Lưu bounding box
        classes.append(int(cls))  # Lưu ID lớp
        confidences.append(conf)  # Lưu độ tin cậy

    return detections, classes, confidences
