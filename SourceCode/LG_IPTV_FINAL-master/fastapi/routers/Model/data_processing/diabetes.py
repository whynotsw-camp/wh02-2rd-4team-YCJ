import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from lightgbm import LGBMClassifier
from imblearn.combine import SMOTEENN
from sklearn.model_selection import RandomizedSearchCV

# 데이터 로드
data_path = "/content/drive/MyDrive/ml연습/data/diabetes_data.csv"
df = pd.read_csv(data_path)

# 데이터 컬럼 이름 정리
df = df.rename(columns={"Diabetes_012": "Diabetes",
                        "Sex": "Gender",
                        "HvyAlcoholConsump": "Alco",
                        "BMI": "BMI Encoded",
                        "HighChol": "Col",
                        "HighBP": "Hyper",
                        "Smoker": "Smoke"})

df.columns = df.columns.str.strip()  # 공백 제거

# 필요한 컬럼 선택
columns_to_use = ["Gender", "Age", "Hyper", "BMI Encoded", "Smoke", "Col", "Alco", "Diabetes"]
df_subset = df[columns_to_use]

# Diabetes 값 변경: 0 유지, 1 제거, 2를 1로 변경
df_subset = df_subset[df_subset["Diabetes"] != 1]  # 1 제거
df_subset["Diabetes"] = df_subset["Diabetes"].replace({2: 1})

df_subset[["Smoke", "Col", "Alco", "Diabetes"]] = df_subset[["Smoke", "Col", "Alco", "Diabetes"]].astype(int)

# 독립 변수(X)와 종속 변수(y) 정의
X = df_subset.drop('Diabetes', axis=1)
y = df_subset['Diabetes']

# 데이터 불균형 해결 (SMOTE-Tomek)
smote_tomek = SMOTETomek(random_state=42)
X_resampled, y_resampled = smote_tomek.fit_resample(X, y)

# 학습 및 테스트 데이터 분리
X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)

# LightGBM 모델 정의 (클래스 가중치 조정)
scale_pos_weight = (len(y_train) - sum(y_train)) / sum(y_train)  # 클래스 가중치 계산
model = LGBMClassifier(random_state=42, scale_pos_weight=scale_pos_weight)

# 하이퍼파라미터 튜닝
param_dist = {
    'n_estimators': [300, 500],
    'learning_rate': [0.05, 0.1],
    'num_leaves': [31, 50],
    'min_child_samples': [20, 30],
    'feature_fraction': [0.8, 1.0]
}

random_search = RandomizedSearchCV(
    estimator=model,
    param_distributions=param_dist,
    n_iter=20,
    cv=3,
    n_jobs=-1,
    verbose=1,
    random_state=42
)
random_search.fit(X_train, y_train)

# 최적 하이퍼파라미터 출력
print("Best Parameters:", random_search.best_params_)

# 최적 모델로 예측 수행
best_rf = random_search.best_estimator_
y_pred_proba = best_rf.predict_proba(X_test)[:, 1]

# 임계값 조정: 0.55로 설정
threshold = 0.55
y_pred_adjusted = (y_pred_proba >= threshold).astype(int)