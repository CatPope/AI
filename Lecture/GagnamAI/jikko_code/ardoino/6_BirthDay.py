from jikko.jikko import *
import time

jk = Pyjikko()

PORT = 'COM3'

NEO = 7
RX = 10
TX = 11
CDS = A0

jk.serial_connect(PORT)
jk.start()

jk.lcd_set(0x27, 16, 2)
jk.neopixel_set(NEO, 4)
jk.neopixel_bright(NEO,20)
jk.mp3_set(RX, TX)
jk.mp3_volume(20)

while True :
    light = jk.cds_read(CDS)
    jk.lcd_clear()
    jk.lcd_display(0, 0, str(light))
    
    if light >= 500:
        jk.mp3_play(2)
        time.sleep(2)
        jk.neopixel_display_all(NEO, NeoColor.YELLOW)
        time.sleep(1)
        jk.neopixel_display_all(NEO, NeoColor.GREEN)
        time.sleep(1)
        jk.neopixel_clear(NEO)
    else:
        jk.neopixel_clear(NEO)
    
    
    