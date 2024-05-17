# 베이직 키트 부품점검 PART3 : 조도센서, 초음파센서, 온습도센서, 토양수분센서
from jikko.jikko import *

jk = Pyjikko()

# 포트 번호 알맞게 바꾸기
PORT = 'COM3'     

jk.serial_connect(PORT)
jk.start()

CDS = A0
TRIG = 13
ECHO = 12
TEM_HUM = 4
SOIL = A1

while(True):

    print("------------------------------")
    print(f"조도센서 값 : {jk.cds_read(CDS)}")
    print(f"초음파 센서 값 : {jk.sonic_read(TRIG, ECHO)}")
    print(f"온도 센서 값 : {jk.temp_read(TEM_HUM)}")
    print(f"습도 센서 값 : {jk.humi_read(TEM_HUM)}")
    print(f"토양수분 센서 값  : {jk.soil_read(SOIL)}")
    print("------------------------------")
    time.sleep(1)


