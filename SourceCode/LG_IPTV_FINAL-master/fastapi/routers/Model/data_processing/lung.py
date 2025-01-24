import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE
from sklearn.linear_model import LogisticRegression
import numpy as np

# 데이터 로드
file_path = '/content/drive/MyDrive/ml연습/data/lung_data.csv'  # 파일 경로를 수정하세요.
data = pd.read_csv(file_path)

data.columns = data.columns.str.strip()  # 공백 제거

data = data.rename(columns={"AGE": "Age",
                        "GENDER": "Gender",
                        "ALCOHOL CONSUMING": "Alco",
                        "Smoker": "Smoke",
                        "FATIGUE": "Tired"})

# 필요한 컬럼 선택
columns_to_use = ['Gender', 'Age', 'Smoke', 'Tired', 'Alco', 'LUNG_CANCER']
data_subset = data[columns_to_use]

# 'yes'/'no' 값을 1/0으로 변환
label_columns = ['LUNG_CANCER']
for col in label_columns:
    data_subset[col] = data_subset[col].replace({'YES': 1, 'NO': 0})

# GENDER 컬럼을 숫자로 인코딩
data_subset['Gender'] = LabelEncoder().fit_transform(data_subset['Gender'])

# 독립 변수(X)와 종속 변수(y) 정의
X = data_subset.drop('LUNG_CANCER', axis=1)
y = data_subset['LUNG_CANCER']

# 데이터 불균형 해결 (SMOTE)
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X, y)

# 학습/Validation/Test 데이터 분리 (추가된 부분)
X_train, X_temp, y_train, y_temp = train_test_split(X_resampled, y_resampled, test_size=0.3, random_state=42)  # 70% Train, 30% Temp
X_valid, X_test, y_valid, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)  # 15% Validation, 15% Test

# 모델 학습
logistic_model = LogisticRegression(max_iter=1000, random_state=42)
logistic_model.fit(X_train, y_train)