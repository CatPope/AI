# src/detect.py
from ultralytics import YOLO

def detect_object_bbox(image_path, model_path='../model/yolov11x.pt', label='cargo'):
    """
    이미지에서 지정 label(예: 'cargo', 'pallet')의 첫 번째 bounding box 반환.
    YOLO 학습 시 클래스명이 label과 일치해야 함.
    """
    model = YOLO(model_path)
    results = model(image_path)
    for r in results:
        for box, cls in zip(r.boxes.xyxy, r.boxes.cls):
            if model.names[int(cls)] == label:
                x1, y1, x2, y2 = [int(x) for x in box]
                return [x1, y1, x2, y2]
    return None  # 미검출시

if __name__ == "__main__":
    bbox = detect_object_bbox("../data/front.jpg", label='cargo')
    print("cargo bbox:", bbox)
