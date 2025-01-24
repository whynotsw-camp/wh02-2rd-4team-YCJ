# Package
import os
import gc
import pickle
import numpy as np
import pandas as pd

import warnings
warnings.filterwarnings("ignore")

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from collections import Counter
from sklearn import tree


# 현재 파일의 디렉토리 경로를 기준으로 dataset 폴더의 sleep.csv 경로 설정
current_dir = os.path.dirname(__file__)  # 현재 파일의 디렉토리
file_path = os.path.join(current_dir, 'datasets', 'Cardio_Data.csv')

# CSV 파일을 읽어 데이터프레임에 저장
try:
    cardio_df = pd.read_csv(file_path, sep=';')
    print("DataFrame Loaded Successfully:")
except FileNotFoundError:
    print(f"File not found at path: {file_path}")
except Exception as e:
    print(f"An error occurred: {e}")

# 나이의 값을 정상적으로 바꾸기
cardio_df['age'] = cardio_df['age'].apply(lambda x: x // 365)

cardio_df

# 필요없는 id칼럼 삭제
cardio_df_T = cardio_df.drop(columns=['id'])

# 컬럼명 변경
cardio_df_T.rename(columns={'ap_hi': 'Systolic', 'ap_lo': 'Diastolic','age' : 'Age', 'weight':'Weight'}, inplace=True)

# X's & Y Split
cols = ['Systolic','Diastolic','Age','Weight']
Y_XG = cardio_df_T['cardio']
X_XG = cardio_df_T[cols]

idx = list(range(X_XG.shape[0]))
train_idx, valid_idx = train_test_split(idx, test_size=0.3, random_state=12)
print(">>>> # of Train data : {}".format(len(train_idx)))
print(">>>> # of valid data : {}".format(len(valid_idx)))
print(">>>> # of Train data Y : {}".format(Counter(Y_XG.iloc[train_idx])))
print(">>>> # of valid data Y : {}".format(Counter(Y_XG.iloc[valid_idx])))



best_model_XGF = XGBClassifier(n_estimators=10, learning_rate=0.1,
                           max_depth=5, reg_alpha=0.5, objective='binary:logistic',
                           random_state=119)
best_model_XGF.fit(X_XG.iloc[train_idx], Y_XG.iloc[train_idx])



# 모델 저장 경로
model_save_path = os.path.join(current_dir, 'Cardio_model.pkl')

# 모델 저장
with open(model_save_path, 'wb') as file:
    pickle.dump(best_model_XGF, file)
print(f"Model saved successfully at {model_save_path}")