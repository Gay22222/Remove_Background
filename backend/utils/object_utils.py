import numpy as np
from PIL import Image
from models.mask_rcnn import detect_mask  # Import hàm detect_mask từ file mask_rcnn.py

def create_mask(image_path, bounding_boxes, mask_rcnn, transforms):
    """
    Tạo mặt nạ (mask) dựa trên bounding boxes và Mask-RCNN.

    Args:
        image_path (str): Đường dẫn đến ảnh gốc.
        bounding_boxes (list): Danh sách các bounding boxes từ YOLO.
        mask_rcnn (model): Mô hình Mask-RCNN.
        transforms (callable): Các phép biến đổi cần thiết cho ảnh đầu vào.

    Returns:
        numpy.array: Mặt nạ nhị phân (binary mask) kết hợp của tất cả các bounding boxes.
    """
    # Đọc ảnh từ đường dẫn và chuyển sang định dạng RGB
    image = Image.open(image_path).convert("RGB")

    # Truyền bounding boxes vào hàm detect_mask để tạo mặt nạ
    outputs = detect_mask(image, mask_rcnn, transforms, yolo_boxes=bounding_boxes)

    # Kiểm tra nếu không tìm thấy mặt nạ nào
    if len(outputs['masks']) == 0:
        raise ValueError("No masks found for the selected bounding boxes.")

    # Khởi tạo mặt nạ kết hợp với kích thước giống mặt nạ đầu tiên
    combined_mask = np.zeros_like(outputs['masks'][0], dtype=np.uint8)

    # Kết hợp tất cả các mặt nạ bằng cách lấy giá trị lớn nhất
    for mask in outputs['masks']:
        combined_mask = np.maximum(combined_mask, mask)

    return combined_mask

def apply_mask(image, mask):
    """
    Áp dụng mặt nạ lên ảnh để xóa đối tượng.

    Args:
        image (numpy.array): Ảnh gốc (H, W, C).
        mask (numpy.array): Mặt nạ nhị phân (H, W).

    Returns:
        masked_image (numpy.array): Ảnh đã được áp dụng mặt nạ.
    """
    # Mở rộng mặt nạ từ kích thước (H, W) thành (H, W, 3) để khớp với ảnh RGB
    expanded_mask = np.stack([mask] * 3, axis=-1)

    # Áp dụng mặt nạ để loại bỏ đối tượng (giá trị tại vùng bị xóa sẽ là 0)
    masked_image = image * (1 - expanded_mask)
    return masked_image
