from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas

# SPI 인터페이스 초기화
serial = spi(port=0, device=0, gpio=noop())

# MAX7219 장치 초기화
device = max7219(serial, cascaded=1, block_orientation=0, rotate=0)
device.contrast(16)

# 원하는 모양을 지정하는 배열
# 1은 LED 켜짐, 0은 LED 꺼짐을 의미
patterns = [
    [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 1, 0, 1, 1, 0, 1, 0],
        [1, 0, 0, 1, 1, 0, 0, 1],
        [1, 0, 0, 1, 1, 0, 0, 1],
        [0, 1, 0, 1, 1, 0, 1, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ],
    [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 1, 0, 1, 1, 0, 1, 0],
        [1, 0, 0, 1, 1, 0, 0, 1],
        [1, 0, 0, 1, 1, 0, 0, 1],
        [0, 1, 0, 1, 1, 0, 1, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]
]


# 패턴을 그리는 함수
def draw_pattern(draw, pattern):
    for y, row in enumerate(pattern):
        for x, col in enumerate(row):
            if col:
                draw.point((x, y), fill="white")
            else:
                draw.point((x, y), fill="black")

    # 패턴을 매트릭스에 표시
    with canvas(device) as draw:
        draw_pattern(draw, pattern)