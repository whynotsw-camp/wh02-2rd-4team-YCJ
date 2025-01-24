import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE

# 데이터 로드
file_path = '/content/drive/MyDrive/ml연습/data/liver_data.csv'  # 파일 경로를 수정하세요.
data = pd.read_csv(file_path)

data = data.rename(columns={"BMI": "BMI Encoded",
                            "AlcoholConsumption": "Alco",
                            "Smoking": "Smoke",
                            "PhysicalActivity": "Daily Steps",
                            'Hypertension': "Hyper",
                            "Diagnosis": "Liver"})

data.columns = data.columns.str.strip()  # 공백 제거

# 필요한 컬럼 선택
columns_to_use = ['Age', 'Gender', 'BMI Encoded', 'Alco', 'Smoke', 'Daily Steps', 'Hyper', 'Liver']
data_subset = data[columns_to_use]

# Alcohol 컬럼 처리 (1보다 작으면 0, 1 이상은 1)
data_subset['Alco'] = data_subset['Alco'].apply(lambda x: 0 if x < 1 else 1)

# PhysicalActivity 값에서 0.5가 30분 걷는 것으로 간주하여 하루 걸음수 계산
data_subset['Daily Steps'] = data['Daily Steps'] * 3000

# 보기 설정: 1. 거의 걷지 않는다(3000), 2. 조금 걷는다(5600), 3. 보통 걷는다(7000), 4. 꽤 많이 걷는다(8000), 5. 매우 많이 걷는다(10000)
bins = [0, 3000, 5600, 7000, 8000, 10000]
labels = [1, 2, 3, 4, 5]
data_subset['Daily Steps'] = pd.cut(data_subset['Daily Steps'], bins=bins, labels=labels, right=True)

# NaN 값을 매우 많이 걷는다(5)로 직접 할당
data_subset['Daily Steps'] = data_subset['Daily Steps'].fillna(5)

# PhysicalActivity 컬럼의 데이터 타입을 int로 변환
data_subset['Daily Steps'] = data_subset['Daily Steps'].astype(int)

# 독립 변수(X)와 종속 변수(y) 정의
X = data_subset.drop('Liver', axis=1)
y = data_subset['Liver']

# 데이터 불균형 해결 (SMOTE)
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X, y)

# 학습 및 테스트 데이터 분리
X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)

# Random Forest 모델 생성 및 학습
rf_model = RandomForestClassifier(random_state=42)

# 하이퍼파라미터 후보 정의
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'max_features': ['sqrt', 'log2']
}

# GridSearchCV 설정
grid_search = GridSearchCV(estimator=rf_model, param_grid=param_grid, cv=3, n_jobs=-1, verbose=2)
grid_search.fit(X_train, y_train)

# 최적 하이퍼파라미터 확인
print("Best Parameters:", grid_search.best_params_)

# 최적 모델로 예측 수행
best_rf = grid_search.best_estimator_  # 최적 모델 가져오기
y_pred = best_rf.predict(X_test)