from jikko.jikko import *
import time

jk = Pyjikko()

PORT = 'COM3'

jk.serial_connect(PORT)
jk.start()

TRIG = 13
ECHO = 12

jk.lcd_set(0x27, 16, 2)

while True:
    distance = jk.sonic_read(TRIG, ECHO)

    jk.lcd_clear()
    jk.lcd_display(0, 0, "sonic ruler")

    jk.lcd_display(0, 1, f"Distance: {distance} cm")

    time.sleep(1)
