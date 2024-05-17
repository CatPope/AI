from jikko.jikko import *
import time

jk = Pyjikko()

PORT = 'COM3'

jk.serial_connect(PORT)
jk.start()

TRIG = 13
ECHO = 12
SERVO = 8

jk.lcd_set(0x27, 16, 2)

jk.lcd_display(0, 0, "Car Barrier")
jk.lcd_display(0, 1, "System Ready")

while True:
    distance = jk.sonic_read(TRIG, ECHO)

    if distance < 20:
        jk.servo_degree(SERVO, 90)
        jk.lcd_clear()
        jk.lcd_display(0, 0, "Car Barrier")
        jk.lcd_display(0, 1, "open")
        print("Barrier opened")
        time.sleep(2)
    else:
        jk.servo_degree(SERVO, 0)
        jk.lcd_clear()
        jk.lcd_display(0, 0, "Car Barrier")
        jk.lcd_display(0, 1, "closed")
        print("Barrier closed")
        time.sleep(2)
