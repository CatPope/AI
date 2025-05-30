# 데이터 준비
import random
import os


# 데이터가 저장될 폴더 (data 폴더가 없으면 생성)
DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), "data")
if not os.path.exists(DATA_FILE_PATH):
  os.makedirs(DATA_FILE_PATH)


# 점수를 계산해서 평균에 따른 학점을 반환
# 편의상 A, B, C로 구분함.
def get_grade(kor, math):
  mean = int((kor + math) / 2)
  grade = "C"
  if 70 <= mean:
    grade = "A"
  elif 40 <= mean:
    grade = "B"
  return grade


# 20000개 데이터를 만들어 CSV에 기록한다.
csvname = os.path.join(DATA_FILE_PATH, "grade.csv")
fp = open(csvname,"w",encoding="utf-8")
fp.write("KOR,MATH,GRADE\r\n")


for i in range(20000):
  kor = random.randint(10, 100)
  math = random.randint(10, 100)
  grade = get_grade(kor, math)
  fp.write("{0},{1},{2}\r\n".format(kor, math, grade))


fp.close()


print("Done")
