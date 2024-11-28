from ultralytics import YOLO
import cv2
import os

# Load mô hình YOLOv8
def load_model(model_path=None):
    """
    Hàm load mô hình YOLOv8.
    Nếu có đường dẫn model_path, load mô hình custom từ file.
    Nếu không, load mô hình YOLOv8 pre-trained mặc định.
    
    Args:
        model_path (str): Đường dẫn đến file mô hình custom (nếu có).
    
    Returns:
        model (YOLO): Mô hình YOLO đã được load.
    """
    if model_path:
        model = YOLO(model_path)  # Load mô hình custom
    else:
        model = YOLO('yolov8n.pt')  # Load mô hình pre-trained YOLOv8
    return model

# Nhận diện vật thể trong ảnh
def detect_objects(image_path, model):
    """
    Hàm nhận diện vật thể trong ảnh sử dụng mô hình YOLO.
    
    Args:
        image_path (str): Đường dẫn đến file ảnh đầu vào.
        model (YOLO): Mô hình YOLO đã được load.
    
    Returns:
        detections (tensor): Danh sách bounding boxes của vật thể.
        classes (tensor): Danh sách class IDs của vật thể.
        scores (tensor): Độ tin cậy của mỗi vật thể.
    """
    # Thực hiện dự đoán
    results = model(image_path)

    # Lấy kết quả từ YOLO
    detections = results[0].boxes.xyxy  # Bounding boxes: tọa độ [x1, y1, x2, y2]
    classes = results[0].boxes.cls  # Class IDs
    scores = results[0].boxes.conf  # Confidence scores
    return detections, classes, scores

# Vẽ bounding boxes
def draw_boxes(image_path, detections, classes, model, processed_folder):
    """
    Hàm vẽ bounding boxes lên ảnh dựa trên kết quả nhận diện.
    
    Args:
        image_path (str): Đường dẫn đến file ảnh đầu vào.
        detections (tensor): Danh sách bounding boxes của vật thể.
        classes (tensor): Danh sách class IDs của vật thể.
        model (YOLO): Mô hình YOLO (dùng để lấy tên các lớp).
        processed_folder (str): Đường dẫn thư mục để lưu ảnh đã xử lý.
    
    Returns:
        output_path (str): Đường dẫn ảnh đã được vẽ bounding boxes.
    """
    # Đọc ảnh đầu vào
    image = cv2.imread(image_path)
    names = model.names  # Lấy danh sách tên classes từ mô hình
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # Danh sách màu sắc cho các bounding boxes

    # Vẽ bounding boxes trên ảnh
    for i, box in enumerate(detections):
        x1, y1, x2, y2 = map(int, box)  # Chuyển đổi tọa độ về dạng int
        cls_id = int(classes[i])  # ID của class
        label = names[cls_id]  # Tên của class từ mô hình
        color = colors[cls_id % len(colors)]  # Chọn màu dựa trên ID của class
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)  # Vẽ hình chữ nhật cho bounding box
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)  # Thêm nhãn vào bounding box

    # Đảm bảo thư mục processed_folder tồn tại
    if not os.path.exists(processed_folder):
        os.makedirs(processed_folder)

    # Đường dẫn lưu ảnh kết quả
    output_path = os.path.join(processed_folder, 'result.jpg')
    cv2.imwrite(output_path, image)  # Lưu ảnh đã xử lý
    return output_path
