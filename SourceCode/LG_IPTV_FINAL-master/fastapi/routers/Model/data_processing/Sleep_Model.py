# Package
import os
import gc
import pickle
import numpy as np
import pandas as pd

import warnings
warnings.filterwarnings("ignore")

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from collections import Counter
from sklearn import tree


# 현재 파일의 디렉토리 경로를 기준으로 dataset 폴더의 sleep.csv 경로 설정
current_dir = os.path.dirname(__file__)  # 현재 파일의 디렉토리
file_path = os.path.join(current_dir, 'datasets', 'Sleep_Data.csv')

# CSV 파일을 읽어 데이터프레임에 저장
try:
    sleep_df = pd.read_csv(file_path)
    print("DataFrame Loaded Successfully:")
except FileNotFoundError:
    print(f"File not found at path: {file_path}")
except Exception as e:
    print(f"An error occurred: {e}")


# 'Blood Pressure' 칼럼을 수축기혈압(Systolic)과 이완기혈압(Diastolic)으로 나누기
sleep_df[['Systolic', 'Diastolic']] = sleep_df['Blood Pressure'].str.split('/', expand=True)
# 데이터 형식을 int로 변환
sleep_df['Systolic'] = sleep_df['Systolic'].astype(int)
sleep_df['Diastolic'] = sleep_df['Diastolic'].astype(int)


# 새로운 칼럼 'Sleep Disorder label' 생성
sleep_df['Sleep Disorder label'] = sleep_df['Sleep Disorder'].apply(lambda x: 0 if pd.isna(x) else 1)

cols = ['Gender','Age','Sleep Duration','Quality of Sleep','Physical Activity Level','Stress Level','BMI Category','Systolic','Diastolic','Heart Rate','Daily Steps','Sleep Disorder label']
sleep_df_T = sleep_df[cols]


sleep_df_T = pd.get_dummies(sleep_df_T, columns=['Gender'])

# 칼럼 이름 변경
sleep_df_T.rename(columns={'Gender_Female': 'Female', 'Gender_Male': 'Male'}, inplace=True)

# True/False를 1/0으로 변환
sleep_df_T['Female'] = sleep_df_T['Female'].astype(int)
sleep_df_T['Male'] = sleep_df_T['Male'].astype(int)

# 라벨 인코딩 매핑 정의
bmi_mapping = {
    'Normal': 2,
    'Overweight': 3,
    'Normal Weight': 1,
    'Obese': 4
}

# BMI 칼럼에 라벨 인코딩 적용
sleep_df_T['BMI Encoded'] = sleep_df_T['BMI Category'].map(bmi_mapping)

# 기존의 'BMI Category' 삭제
sleep_df_T.drop(columns=['BMI Category'], inplace=True)


# X's & Y Split
cols = ['BMI Encoded','Age','Sleep Duration','Systolic','Diastolic','Daily Steps']
Y_RF = sleep_df_T['Sleep Disorder label']
X_RF = sleep_df_T[cols]


idx = list(range(X_RF.shape[0]))
train_idx, valid_idx = train_test_split(idx, test_size=0.3, random_state=12)
print(">>>> # of Train data : {}".format(len(train_idx)))
print(">>>> # of valid data : {}".format(len(valid_idx)))
print(">>>> # of Train data Y : {}".format(Counter(Y_RF.iloc[train_idx])))
print(">>>> # of valid data Y : {}".format(Counter(Y_RF.iloc[valid_idx])))


# RandomForest 모델
best_model_RF = RandomForestClassifier(n_estimators=10, max_depth=4, random_state=12,
                               criterion='gini', max_features='sqrt',
                               bootstrap=True, oob_score=False) 
best_model_RF.fit(X_RF.iloc[train_idx], Y_RF.iloc[train_idx])


# 모델 저장 경로
model_save_path = os.path.join(current_dir, 'Sleep_model.pkl')

# 모델 저장
with open(model_save_path, 'wb') as file:
    pickle.dump(best_model_RF, file)
print(f"Model saved successfully at {model_save_path}")