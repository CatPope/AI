# src/main.py
from detect import detect_object_bbox
from dimension import calc_scale, get_dimensions
from utils import save_results

def pipeline(front_img, side_img, model_path='../model/yolo11x.pt', real_pallet_width=1000):
    # 1. 팔레트 검출 (정면, 측면)
    front_pallet_bbox = detect_object_bbox(front_img, model_path, label='pallet')
    side_pallet_bbox = detect_object_bbox(side_img, model_path, label='pallet')
    if front_pallet_bbox is None or side_pallet_bbox is None:
        raise ValueError("팔레트 검출 실패: 이미지 또는 YOLO label 확인 필요")

    front_scale = calc_scale(front_pallet_bbox, real_pallet_width)
    side_scale = calc_scale(side_pallet_bbox, real_pallet_width)

    # 2. 화물(적재물) 박스 검출
    front_cargo_bbox = detect_object_bbox(front_img, model_path, label='cargo')
    side_cargo_bbox = detect_object_bbox(side_img, model_path, label='cargo')
    if front_cargo_bbox is None or side_cargo_bbox is None:
        raise ValueError("적재물(cargo) 검출 실패: 이미지 또는 YOLO label 확인 필요")

    # 3. 치수 산출
    width, depth, height = get_dimensions(front_cargo_bbox, side_cargo_bbox, front_scale, side_scale)
    result = {
        "가로(m)": width,
        "세로(m)": depth,
        "높이(m)": height
    }
    save_results(result, "../data/result/result.json")
    return result

if __name__ == "__main__":
    res = pipeline("../data/image_set/front.png", "../data/image_set/side.png")
    print(res)
