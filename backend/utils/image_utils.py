from ultralytics import YOLO
import cv2
import os
# Load mô hình YOLOv8
def load_model(model_path=None):
    if model_path:
        model = YOLO(model_path)  # Custom model
    else:
        model = YOLO('yolov8n.pt')  # Mô hình YOLOv8 pre-trained
    return model

# Nhận diện vật thể trong ảnh
def detect_objects(image_path, model):
    # Dự đoán
    results = model(image_path)

    # Trả về danh sách các bounding boxes và labels
    detections = results[0].boxes.xyxy  # Tọa độ bounding boxes
    classes = results[0].boxes.cls  # Lớp (class) vật thể
    scores = results[0].boxes.conf  # Độ tin cậy
    return detections, classes, scores

# Vẽ bounding boxes
def draw_boxes(image_path, detections, classes, model, processed_folder):
    # Đọc ảnh đầu vào
    image = cv2.imread(image_path)
    names = model.names  # Lấy danh sách tên classes
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # Màu sắc cho các lớp

    # Vẽ bounding boxes
    for i, box in enumerate(detections):
        x1, y1, x2, y2 = map(int, box)
        cls_id = int(classes[i])
        label = names[cls_id]
        color = colors[cls_id % len(colors)]  # Chọn màu sắc tương ứng
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    # Xây dựng đường dẫn output trong processed_folder
    output_path = os.path.join(processed_folder, 'result.jpg')
    cv2.imwrite(output_path, image)
    return output_path
