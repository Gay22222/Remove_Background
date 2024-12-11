import cv2
import os

# Vẽ bounding boxes lên ảnh
def draw_boxes(image_path, detections, classes, model, processed_folder):
    """
    Vẽ bounding boxes lên ảnh dựa trên kết quả nhận diện.

    Args:
        image_path (str): Đường dẫn đến file ảnh đầu vào.
        detections (list): Danh sách bounding boxes (từ YOLO hoặc Mask-RCNN).
        classes (list): Danh sách ID lớp của vật thể.
        model (object): Mô hình nhận diện (cần có thuộc tính `names`).
        processed_folder (str): Thư mục để lưu ảnh đã xử lý.

    Returns:
        output_path (str): Đường dẫn ảnh đã vẽ bounding boxes.
    """
    # Đọc ảnh đầu vào
    image = cv2.imread(image_path)
    names = model.names  # Danh sách tên lớp từ mô hình
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # Màu sắc cho bounding boxes

    # Vẽ bounding boxes
    for i, box in enumerate(detections):
        x1, y1, x2, y2 = map(int, box)  # Chuyển tọa độ bounding box sang số nguyên
        cls_id = int(classes[i])  # ID lớp
        label = names[cls_id]  # Tên lớp từ ID
        color = colors[cls_id % len(colors)]  # Chọn màu dựa trên ID lớp
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)  # Vẽ bounding box
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)  # Thêm nhãn lớp

    # Đảm bảo thư mục lưu kết quả tồn tại
    if not os.path.exists(processed_folder):
        os.makedirs(processed_folder)

    # Lưu ảnh đã xử lý
    output_path = os.path.join(processed_folder, 'result.jpg')
    cv2.imwrite(output_path, image)
    return output_path
