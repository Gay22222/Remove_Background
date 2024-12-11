import numpy as np
from PIL import Image
from models.mask_rcnn import detect_mask  # Import detect_mask từ mask_rcnn.py

def create_mask(image_path, object_to_remove, mask_rcnn, transforms):
    """
    Tạo mặt nạ (mask) cho đối tượng cần xóa bằng Mask-RCNN.

    Args:
        image_path (str): Đường dẫn đến ảnh gốc.
        object_to_remove (str): Tên hoặc nhãn của đối tượng cần xóa.
        mask_rcnn: Đối tượng mô hình Mask-RCNN.
        transforms: Các phép biến đổi cần thiết cho ảnh đầu vào.

    Returns:
        mask (numpy.array): Mặt nạ nhị phân (binary mask) của đối tượng cần xóa.
    """
    image = Image.open(image_path).convert("RGB")  # Mở ảnh và chuyển đổi sang RGB
    outputs = detect_mask(image, mask_rcnn, transforms)  # Phát hiện bằng Mask-RCNN

    # Duyệt qua các nhãn để tìm đối tượng cần xóa
    for i, label in enumerate(outputs['labels']):
        # So sánh nhãn với tên đối tượng cần xóa
        if label == object_to_remove:
            # Trả về mặt nạ đầu tiên tìm được
            return outputs['masks'][i, 0]  # Lấy mặt nạ của đối tượng cần xóa

    return None  # Nếu không tìm thấy đối tượng

def apply_mask(image, mask):
    """
    Áp dụng mặt nạ lên ảnh để xóa đối tượng.

    Args:
        image (numpy.array): Ảnh gốc (H, W, C).
        mask (numpy.array): Mặt nạ nhị phân (H, W).

    Returns:
        masked_image (numpy.array): Ảnh đã được áp dụng mặt nạ.
    """
    # Mở rộng mặt nạ từ (H, W) thành (H, W, 3) để khớp với ảnh RGB
    expanded_mask = np.stack([mask] * 3, axis=-1)

    # Áp dụng mặt nạ (mask) lên ảnh
    masked_image = image * (1 - expanded_mask)  # Vùng được xóa sẽ là 0
    return masked_image

