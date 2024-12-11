import torch
from torchvision.models.detection import maskrcnn_resnet50_fpn, MaskRCNN_ResNet50_FPN_Weights


# Định nghĩa ánh xạ nhãn (dựa trên COCO dataset)
LABEL_NAMES = {
    1: "person",
    2: "bicycle",
    3: "car",
    4: "motorcycle",
    5: "airplane",
    6: "bus",
    7: "train",
    8: "truck",
    9: "boat",
    10: "traffic light",
    11: "fire hydrant",
    # ... Thêm các nhãn khác từ COCO dataset
}

def get_label_name(label_id):
    """
    Lấy tên nhãn từ ID nhãn.
    
    Args:
        label_id (int): ID nhãn.
    
    Returns:
        str: Tên nhãn, hoặc 'unknown' nếu không tìm thấy.
    """
    return LABEL_NAMES.get(label_id, "unknown")


def load_mask_rcnn_model():
    """
    Tải mô hình Mask-RCNN với trọng số được huấn luyện sẵn.

    Returns:
        model: Đối tượng Mask-RCNN đã được tải.
        transforms: Các phép biến đổi (transform) cần thiết cho đầu vào của mô hình.
    """
    # Lấy trọng số mặc định từ torchvision
    weights = MaskRCNN_ResNet50_FPN_Weights.DEFAULT
    # Tải mô hình với trọng số đã được huấn luyện
    model = maskrcnn_resnet50_fpn(weights=weights, progress=False)
    model.eval()  # Chuyển sang chế độ đánh giá
    return model, weights.transforms()

def detect_mask(image, model, transforms):
    """
    Phát hiện vật thể và mặt nạ (mask) bằng Mask-RCNN.

    Args:
        image (PIL.Image): Ảnh đầu vào.
        model: Đối tượng Mask-RCNN.
        transforms: Các phép biến đổi cần thiết để chuẩn hóa ảnh.

    Returns:
        output (dict): Thông tin phát hiện bao gồm bounding boxes, masks và labels.
    """
    # Áp dụng các phép biến đổi và chuyển ảnh sang tensor
    image_tensor = transforms(image).unsqueeze(0)  # Thêm batch dimension
    with torch.no_grad():
        # Thực hiện dự đoán
        output = model(image_tensor)[0]

    # Chuyển đổi ID nhãn thành tên nhãn
    label_names = [get_label_name(int(label)) for label in output['labels'].cpu().numpy()]

    # Trả về thông tin bao gồm tên nhãn
    return {
        "boxes": output['boxes'].cpu().numpy(),  # Bounding boxes
        "masks": output['masks'].cpu().numpy(),  # Mặt nạ
        "labels": label_names  # Tên nhãn các vật thể
    }
