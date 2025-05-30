# src/dimension.py
def calc_scale(pallet_bbox, real_pallet_width_mm=1000):
    """팔레트의 실제 폭(1m)과 이미지 내 픽셀 폭으로 스케일(mm/px) 계산"""
    pixel_width = pallet_bbox[2] - pallet_bbox[0]
    return real_pallet_width_mm / pixel_width if pixel_width else 1

def get_dimensions(front_bbox, side_bbox, front_scale, side_scale):
    """
    정면(가로/높이), 측면(세로/높이) bbox와 스케일로 실제 가로/세로/높이 계산(m 단위)
    """
    width = (front_bbox[2] - front_bbox[0]) * front_scale / 1000.0
    height1 = (front_bbox[3] - front_bbox[1]) * front_scale / 1000.0
    depth = (side_bbox[2] - side_bbox[0]) * side_scale / 1000.0
    height2 = (side_bbox[3] - side_bbox[1]) * side_scale / 1000.0
    height = (height1 + height2) / 2
    return [round(width, 3), round(depth, 3), round(height, 3)]

if __name__ == "__main__":
    print(get_dimensions([10, 10, 210, 110], [12, 20, 212, 120], 5, 5))
