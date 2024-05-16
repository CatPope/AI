from jikko.jikko import *
import time

jk = Pyjikko()

PORT = 'COM3'     

jk.serial_connect(PORT)
jk.start()

NEO = 7
CDS = A0

jk.lcd_set(0x27, 16, 2)
jk.neopixel_set(NEO, 4)

while True:
    light = jk.cds_read(CDS)
    jk.lcd_clear()
    jk.lcd_display(0, 0, str(light))
    
    if light < 200:
        jk.neopixel_clear(NEO)
        time.sleep(1)
        
    elif 200 <= light < 400:
        jk.neopixel_display(NEO, 0, NeoColor.WHITE)
        jk.neopixel_display(NEO, 1, NeoColor.WHITE)
        time.sleep(1)
        
    else :
        jk.neopixel_display_all(NEO, NeoColor.GREEN)
        time.sleep(1)
    jk.neopixel_clear(NEO)
    jk.lcd_clear()
        
        
        
        
        
        
        
        
        