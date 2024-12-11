import cv2
import os
import random

# Tạo danh sách màu ngẫu nhiên
random.seed(42)  # Đảm bảo kết quả ngẫu nhiên lặp lại
colors = [tuple(random.randint(0, 255) for _ in range(3)) for _ in range(100)]

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
    if image is None:
        raise ValueError(f"Image at path {image_path} could not be read.")
    
    names = model.names  # Danh sách tên lớp từ mô hình

    # Vẽ bounding boxes
    for i, box in enumerate(detections):
        try:
            x1, y1, x2, y2 = map(int, box)  # Chuyển tọa độ bounding box sang số nguyên
            cls_id = int(classes[i])  # ID lớp
            label = f"{names[cls_id]} ({i + 1})"  # Tên lớp và ID duy nhất
            color = (0, 255, 0)  # Màu cho bounding box
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)  # Vẽ bounding box
            cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)  # Thêm nhãn lớp
        except Exception as e:
            print(f"Error processing bounding box at index {i}: {e}")
            continue

    # Đảm bảo thư mục lưu kết quả tồn tại
    os.makedirs(processed_folder, exist_ok=True)

    # Đổi tên file kết quả
    file_name = os.path.basename(image_path).split('.')[0] + '_result.jpg'
    output_path = os.path.join(processed_folder, file_name)

    # Lưu ảnh đã xử lý
    cv2.imwrite(output_path, image)
    return output_path


def expand_bounding_boxes(bounding_boxes, image_shape, scale=0.1):
    """
    Mở rộng các bounding box theo một tỷ lệ.

    Args:
        bounding_boxes (list): Danh sách bounding boxes (x1, y1, x2, y2).
        image_shape (tuple): Kích thước ảnh (height, width).
        scale (float): Tỷ lệ mở rộng (0.1 = mở rộng 10% mỗi chiều).

    Returns:
        list: Danh sách bounding boxes sau khi mở rộng.
    """
    height, width = image_shape[:2]
    expanded_boxes = []

    for box in bounding_boxes:
        x1, y1, x2, y2 = box
        box_width = x2 - x1
        box_height = y2 - y1

        # Tính toán tọa độ mới với giới hạn trong ảnh
        new_x1 = max(0, x1 - box_width * scale)
        new_y1 = max(0, y1 - box_height * scale)
        new_x2 = min(width, x2 + box_width * scale)
        new_y2 = min(height, y2 + box_height * scale)

        expanded_boxes.append([new_x1, new_y1, new_x2, new_y2])

    return expanded_boxes



