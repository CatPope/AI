# 베이직 키트 부품점검 PART1 : LED, 부저, LCD
from jikko.jikko import *

jk = Pyjikko()

# 포트 번호 알맞게 바꾸기
PORT = 'COM3'     

jk.serial_connect(PORT)
jk.start()

LED = 5
BUZZER = 6

jk.lcd_set(0x27, 16, 2)

while(True):

    jk.lcd_clear()
    jk.lcd_display(0,0,"hello,jikko")
    jk.lcd_display(0,1,"LED, BUZZER ON")

    jk.led_digital(LED, HIGH)

    jk.buzzer(BUZZER, 131, 1)
    jk.buzzer(BUZZER, 147, 1)
    jk.buzzer(BUZZER, 165, 1)
    jk.buzzer(BUZZER, 175, 1)
    jk.buzzer(BUZZER, 196, 1)
    time.sleep(1)

    jk.led_digital(LED, LOW)

    jk.lcd_clear()
    jk.lcd_display(0,0,"hello,jikko")
    jk.lcd_display(0,1,"LED, BUZZER OFF")
    time.sleep(1)

