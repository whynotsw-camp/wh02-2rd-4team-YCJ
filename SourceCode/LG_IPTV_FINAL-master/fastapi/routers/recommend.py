from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from services.recommendation import recommend_videos
from config import SessionLocal
from models import User, Detail
from processing_module import calculate_bmi_category, calculate_hypertension

import os
import pickle
import joblib
import pandas as pd
import warnings
from sklearn.exceptions import InconsistentVersionWarning
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

# 현재 파일의 디렉토리 경로
current_dir = os.path.dirname(__file__)
# Model 폴더 경로 추가
model_dir = os.path.join(current_dir, 'Model')

sleep_model_path = os.path.join(model_dir, 'Sleep_model.pkl')
cardio_model_path = os.path.join(model_dir, 'Cardio_model.pkl')
diabetes_model_path = os.path.join(model_dir, 'diabetes_model.joblib')
liver_model_path = os.path.join(model_dir, 'liver_model.joblib')
lung_model_path = os.path.join(model_dir, 'lung_model.joblib')

# Sleep 모델 로드
try:
    with open(sleep_model_path, 'rb') as file:
        loaded_Sleep_RF = pickle.load(file)
    print("Model loaded successfully!")
except FileNotFoundError:
    print(f"Model file not found at {sleep_model_path}")
except Exception as e:
    print(f"An error occurred while loading the model: {e}")

# Cardio 모델 로드
try:
    with open(cardio_model_path, 'rb') as file:
        loaded_Cardio_XGB = pickle.load(file)
    print("Model loaded successfully!")
except FileNotFoundError:
    print(f"Model file not found at {cardio_model_path}")
except Exception as e:
    print(f"An error occurred while loading the model: {e}")

# diabetes 모델 로드
try:
    with open(diabetes_model_path, 'rb') as file:
        loaded_Diabetes_GBM = joblib.load(file)
    print("Model loaded successfully!")
except FileNotFoundError:
    print(f"Model file not found at {diabetes_model_path}")
except Exception as e:
    print(f"An error occurred while loading the model: {e}")

# liver 모델 로드
try:
    with open(liver_model_path, 'rb') as file:
        loaded_Liver_RF = joblib.load(file)
    print("Model loaded successfully!")
except FileNotFoundError:
    print(f"Model file not found at {liver_model_path}")
except Exception as e:
    print(f"An error occurred while loading the model: {e}")

# lung 모델 로드
try:
    with open(lung_model_path, 'rb') as file:
        loaded_Lung_LG = joblib.load(file)
    print("Model loaded successfully!")
except FileNotFoundError:
    print(f"Model file not found at {lung_model_path}")
except Exception as e:
    print(f"An error occurred while loading the model: {e}")

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/api/recommendations/{user_id}")
async def get_recommendations(user_id: int, db: Session = Depends(get_db)):
    print(f"get_recommendations called with user_id: {user_id}")
    # if user_id == 0:
    #     print("Invalid user_id: 0")
    #     return JSONResponse({"error": "Invalid user_id"}, status_code=400)
    # 사용자 데이터 조회
    user = db.query(User).filter(User.user_id == user_id).first()
    detail = db.query(Detail).filter(Detail.user_id == user_id).first()

    if not user or not detail:
        print(f"User or Detail not found for user_id: {user_id}")
        return JSONResponse({"error": "User or Detail not found"}, status_code=404)

    print(f"User and Detail found for user_id: {user_id}")

    user_data = {
        'Name': user.name,
        'Age': user.age,
        'Gender': int(user.gender),
        'Height': user.height,
        'Weight': user.weight,
        'Alco': int(user.drinking_status),
        'Smoke': int(user.smoking_status),
        'Sleep Duration': detail.daily_sleep,
        'Tired': int(user.fatigue_status),
        'Systolic': detail.systolic_bp,
        'Diastolic': detail.diastolic_bp,
        'Daily Steps': detail.daily_steps,
        'Col': int(detail.cholesterol_status)
    }
    user_df = pd.DataFrame([user_data])
    print(user_df)

    print("User data prepared for prediction:", user_data)

    # 'BMI Encoded' 열 추가해서 새로운 데이터 프레임에 저장
    # 'Hyper' 열 추가해서 새로운 데이터 프레임에 저장
    tmdrbs_pd_f = user_df.copy()
    tmdrbs_pd_f['BMI Encoded'] = tmdrbs_pd_f.apply(lambda row: calculate_bmi_category(row['Height'], row['Weight']), axis=1)
    tmdrbs_pd_f['Hyper'] = tmdrbs_pd_f.apply(lambda row: calculate_hypertension(row['Systolic'], row['Diastolic']), axis=1)
            
    cols_sleep = ['BMI Encoded','Age','Sleep Duration','Systolic','Diastolic','Daily Steps']
    # BMI Encoded : 1 (저체중), 2(정상체중), 3(과체중), 4(비만)
    tmdrbs_sleep = tmdrbs_pd_f[cols_sleep]
    ################ 수면장애 위험군 분류 예측 모델 ########################
    try:
        sleep_predictions = loaded_Sleep_RF.predict(tmdrbs_sleep)
        if sleep_predictions == 1:
            print('수면장애 위험군입니다.')
        else:
            print('수면장애 위험군이 아닙니다.')
    except Exception as e:
        print(f"An error occurred during prediction: {e}")

    #####################################################################
    cols_cardio = ['Systolic','Diastolic','Age','Weight']
    tmdrbs_cardio = tmdrbs_pd_f[cols_cardio]
    ################ 심혈관질환 위험군 분류 예측 모델 ######################
    try:
        cardio_predictions = loaded_Cardio_XGB.predict(tmdrbs_cardio)
        if cardio_predictions == 1:
            print('심혈관질환 위험군입니다.')
        else:
            print('심혈관질환 위험군이 아닙니다.')
    except Exception as e:
        print(f"An error occurred during prediction: {e}")

    ######################################################################
    cols_diabetes = ["Gender", "Age", "Hyper", "BMI Encoded", "Smoke", "Col", "Alco"]
    tmdrbs_diabetes = tmdrbs_pd_f[cols_diabetes]
    ################ 당뇨 위험군 분류 예측 모델 ############################
    try:
        diabetes_predictions = loaded_Diabetes_GBM.predict(tmdrbs_diabetes)
        if diabetes_predictions == 1:
            print('당뇨 위험군입니다.')
        else:
            print('당뇨 위험군이 아닙니다.')
    except Exception as e:
        print(f"An error occurred during prediction: {e}")

    ######################################################################
    cols_liver = ['Age', 'Gender', 'BMI Encoded', 'Alco', 'Smoke', 'Daily Steps', 'Hyper']
    tmdrbs_liver = tmdrbs_pd_f[cols_liver]
    ################ 간암 위험군 분류 예측 모델 ############################
    try:
        liver_predictions = loaded_Liver_RF.predict(tmdrbs_liver)
        if liver_predictions == 1:
            print('간암 위험군입니다.')
        else:
            print('간암 위험군이 아닙니다.')
    except Exception as e:
        print(f"An error occurred during prediction: {e}")

    ######################################################################
    cols_lung = ['Gender', 'Age', 'Smoke', 'Tired', 'Alco']
    tmdrbs_lung = tmdrbs_pd_f[cols_lung]
    ################ 폐암 위험군 분류 예측 모델 ############################
    try:
        lung_predictions = loaded_Lung_LG.predict(tmdrbs_lung)
        if lung_predictions == 1:
            print('폐암 위험군입니다.')
        else:
            print('폐암 위험군이 아닙니다.')
    except Exception as e:
        print(f"An error occurred during prediction: {e}")
    #######################################################################
    
    # 추천 카테고리 결정
    categories1 = []
    categories2 = ["식단 관리", "근력 운동", "스트레스 관리","영양 보충제","정기 검진 중요성"]
    if sleep_predictions == 1:
        categories1.append("수면장애")
    if lung_predictions == 1:
        categories1.append("폐암")
    if diabetes_predictions == 1:
        categories1.append("당뇨")
    if liver_predictions == 1:
        categories1.append("간암")
    if cardio_predictions == 1:
        categories1.append("심혈관질환")

    categories = categories1 + categories2

    # 추천 비디오 생성
    recommendations = recommend_videos(categories)
    print("Recommendations generated:", recommendations)
    print("Categories generated:", categories)  # 디버그용 로그 추가
    return JSONResponse({"recommendations": recommendations, "categories": categories})