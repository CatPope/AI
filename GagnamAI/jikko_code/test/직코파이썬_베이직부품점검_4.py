# 베이직 키트 부품점검 PART3 : MP3 모듈, SD카드, 스피커
from jikko.jikko import *

jk = Pyjikko()

# 포트 번호 알맞게 바꾸기
PORT = 'COM4'     

jk.serial_connect(PORT)
jk.start()

RX = 10
TX = 11

jk.mp3_set(RX, TX)
jk.mp3_volume(20)

while(True):

    jk.mp3_play_time(6, 4)
    jk.mp3_play_time(7, 4)
    jk.mp3_play_time(8, 4)
    jk.mp3_play_time(9, 4)
    jk.mp3_play_time(10, 4)

