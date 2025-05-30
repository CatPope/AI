# 베이직 키트 부품점검 PART3 : 서보모터, 네오픽셀
from jikko.jikko import *

jk = Pyjikko()

# 포트 번호 알맞게 바꾸기
PORT = 'COM3'     

jk.serial_connect(PORT)
jk.start()

NEO = 7
SERVO = 8

jk.neopixel_set(NEO, 4)
jk.neopixel_bright(NEO, 255)

while(True):

    jk.servo_degree(SERVO, 0)
    jk.neopixel_display_all(NEO, 0, 0, 0)
    time.sleep(1)
    
    jk.servo_degree(SERVO, 45)
    jk.neopixel_display(NEO, 0, 0, 0, 255)
    time.sleep(1)
    
    jk.servo_degree(SERVO, 90)
    jk.neopixel_display(NEO, 1, 0, 0, 255)
    time.sleep(1)

    jk.servo_degree(SERVO, 135)
    jk.neopixel_display(NEO, 2, 0, 0, 255)
    time.sleep(1)

    jk.servo_degree(SERVO, 90)
    jk.neopixel_display(NEO, 3, 0, 0, 255)
    time.sleep(1)

