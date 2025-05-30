# src/classify_.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

def train_classifier(train_csv_path, model_save_path="rf_model.joblib"):
    df = pd.read_csv(train_csv_path)
    X = df.drop(columns=["stability"])
    y = df["stability"]
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    joblib.dump(model, model_save_path)

def infer_stability(input_features, model_path="rf_model.joblib"):
    model = joblib.load(model_path)
    result = model.predict([input_features])
    prob = model.predict_proba([input_features])
    return result[0], float(prob.max())

if __name__ == "__main__":
    # 학습
    train_classifier("../data/train.csv")
    # 예측
    res, conf = infer_stability([1.2, 0.8, 0.9, 120, 1])
    print("분류 결과:", res, "신뢰도:", conf)
