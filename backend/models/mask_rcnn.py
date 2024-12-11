import torch
from torchvision.models.detection import maskrcnn_resnet50_fpn, MaskRCNN_ResNet50_FPN_Weights

# Định nghĩa ánh xạ nhãn (LABEL_NAMES) dựa trên COCO dataset
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
    12: "bicycle"
    # ... Thêm các nhãn khác từ COCO dataset nếu cần
}

def get_label_name(label_id):
    """
    Lấy tên nhãn từ ID nhãn.

    Args:
        label_id (int): ID của nhãn.

    Returns:
        str: Tên nhãn hoặc "unknown" nếu không tìm thấy.
    """
    return LABEL_NAMES.get(label_id, "unknown")

def load_mask_rcnn_model():
    """
    Tải mô hình Mask-RCNN với trọng số được huấn luyện sẵn từ COCO dataset.

    Returns:
        model: Mô hình Mask-RCNN đã được tải.
        transforms: Phép biến đổi cần thiết để chuẩn hóa ảnh đầu vào.
    """
    # Tải trọng số đã huấn luyện sẵn từ torchvision
    weights = MaskRCNN_ResNet50_FPN_Weights.DEFAULT
    # Khởi tạo mô hình với trọng số đã tải
    model = maskrcnn_resnet50_fpn(weights=weights, progress=False)
    # Đặt mô hình ở chế độ đánh giá (evaluation mode)
    model.eval()
    return model, weights.transforms()

def detect_mask(image, model, transforms, yolo_boxes=None):
    """
    Phát hiện vật thể và mặt nạ (mask) bằng Mask-RCNN, giới hạn theo bounding boxes từ YOLO.

    Args:
        image (PIL.Image): Ảnh đầu vào.
        model (torch.nn.Module): Mô hình Mask-RCNN đã được tải.
        transforms (callable): Phép biến đổi cần thiết cho ảnh đầu vào.
        yolo_boxes (list): Danh sách các bounding boxes từ YOLO (x1, y1, x2, y2).

    Returns:
        dict: Kết quả phát hiện bao gồm bounding boxes, masks, label IDs và tên nhãn.
    """
    # Chuẩn hóa ảnh đầu vào thành tensor
    image_tensor = transforms(image).unsqueeze(0)
    # Tắt tính năng gradient để tăng tốc quá trình infer
    with torch.no_grad():
        output = model(image_tensor)[0]

    # Lấy ID nhãn từ kết quả mô hình
    label_ids = output['labels'].cpu().numpy()
    # Lấy tên nhãn tương ứng từ LABEL_NAMES
    label_names = [LABEL_NAMES.get(int(label_id), "unknown") for label_id in label_ids]

    if yolo_boxes:
        # Nếu có bounding boxes từ YOLO, lọc các kết quả Mask-RCNN nằm trong các bounding boxes đó
        filtered_boxes = []
        filtered_masks = []
        filtered_labels = []
        filtered_names = []

        for yolo_box in yolo_boxes:
            # Lấy tọa độ của bounding box YOLO
            x1, y1, x2, y2 = map(int, yolo_box)

            # Duyệt qua các kết quả phát hiện của Mask-RCNN
            for idx, box in enumerate(output['boxes'].cpu().numpy()):
                bx1, by1, bx2, by2 = box

                # Kiểm tra nếu bounding box Mask-RCNN nằm trong bounding box YOLO
                if bx1 >= x1 and by1 >= y1 and bx2 <= x2 and by2 <= y2:
                    # Lưu lại các kết quả phù hợp
                    filtered_boxes.append(box)
                    filtered_masks.append(output['masks'][idx, 0].cpu().numpy())
                    filtered_labels.append(label_ids[idx])
                    filtered_names.append(label_names[idx])

        return {
            "boxes": filtered_boxes,
            "masks": filtered_masks,
            "label_ids": filtered_labels,
            "label_names": filtered_names,
        }

    # Nếu không có YOLO bounding boxes, trả về toàn bộ kết quả từ Mask-RCNN
    return {
        "boxes": output['boxes'].cpu().numpy(),
        "masks": output['masks'].cpu().numpy(),
        "label_ids": label_ids,
        "label_names": label_names,
    }
