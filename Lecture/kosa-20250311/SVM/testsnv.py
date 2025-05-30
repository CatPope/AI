# SVM으로 머신러닝
# pip install scikit-learn
# pip install pandas
from sklearn import svm, metrics
from sklearn.model_selection import train_test_split
import pandas as pd
import os
# ImportError: cannot import name 'joblib' from 'sklearn.externals'
# https://gaussian37.github.io/ml-sklearn-saving-model/
import joblib


# grade가 저장된 CSV 파일 읽기
DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), "data")
csvname = os.path.join(DATA_FILE_PATH, "grade.csv")


# CVS 파일 점검
if not os.path.exists(csvname):
    print("데이터 파일이 없습니다. makecsv.py를 먼저 실행하세요.")
    exit()


grade = pd.read_csv(csvname)


# 데이터 전처리 (학습을 위하여 데이터를 분리하고 가공-정규화)
label = grade["GRADE"]
kor = grade["KOR"] / 100
math = grade["MATH"] / 100
data = pd.concat([kor, math], axis=1)


# 학습 및 테스트 데이터로 분리
data_train, data_test, label_train, label_test = \
    train_test_split(data, label)


# 학습하기
model = svm.SVC()
model.fit(data_train, label_train)


# 모델 (weight) 저장 후 다시 읽기 (모델을 저장하고 다시 읽어서 사용할 수 있음을 확인)
weightsname = os.path.join(DATA_FILE_PATH, "model_weights.pkl")
joblib.dump(model, weightsname)
model = joblib.load(weightsname)


# 테스트 데이터로 에측하기 (평가를 위함)
predict = model.predict(data_test)


# 결과 확인하고 평가하기
ac_score = metrics.accuracy_score(label_test, predict)
cl_report = metrics.classification_report(label_test, predict)
print("Accuracy =", ac_score)
print("Report =\n", cl_report)
print()
input("Press Enter to continue...")


# 실제 데이터로 예측하기
kor = 90
math = 80
new_data = pd.DataFrame({
'KOR': [kor/100],
'MATH': [math/100]
})


predict = model.predict(new_data)
print(f"kor : {kor}, math : {math} => grade : {predict[0]}")
print()
input("Press Enter to continue...")