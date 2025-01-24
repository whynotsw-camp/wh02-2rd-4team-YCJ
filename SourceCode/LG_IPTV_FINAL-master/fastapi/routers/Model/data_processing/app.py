import os
import pickle
import joblib
import pandas as pd
import warnings
from sklearn.exceptions import InconsistentVersionWarning

warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

# 현재 파일의 디렉토리 경로
current_dir = os.path.dirname(__file__)
sleep_model_path = os.path.join(current_dir, 'Sleep_model.pkl')
cardio_model_path = os.path.join(current_dir, 'Cardio_model.pkl')
diabetes_model_path = os.path.join(current_dir, 'diabetes_model.joblib')
liver_model_path = os.path.join(current_dir, 'liver_model.joblib')
lung_model_path = os.path.join(current_dir, 'lung_model.joblib')

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

#######################################################################################
############################ 사용자에게 받을 데이터 예시#################################
tmdrbs = {
    'Name' : '박승균', 
    'Age': 29,
    'Gender' : 1,
    'Height' : 172,
    'Weight' : 72,
    'Alco' : 1,
    'Smoke' : 1,
    'Sleep Duration': 7.0,
    'Tired' : 1,
    'Systolic': 120,
    'Diastolic': 81,
    'Daily Steps': 8000,
    'Col': 1           # 콜레스테롤 수치 여부
}

tmdrbs_pd = pd.DataFrame([tmdrbs])
print(tmdrbs_pd)
#######################################################################################
#######################################################################################
def calculate_bmi_category(height, weight):
    bmi = weight / (height / 100) ** 2
    if bmi < 18.5:
        return 1  # 저체중
    elif 18.5 <= bmi < 25:
        return 2  # 정상
    elif 25 <= bmi < 30:
        return 3  # 과체중
    else:
        return 4  # 비만
    
# 고혈압 여부를 판단하여 'Hyper' 컬럼 추가
def calculate_hypertension(systolic, diastolic):
    if systolic >= 140 or diastolic >= 90:
        return 1  # 고혈압
    else:
        return 0  # 정상

# 'BMI Encoded' 열 추가해서 새로운 데이터 프레임에 저장
tmdrbs_pd_f = tmdrbs_pd.copy()
tmdrbs_pd_f['BMI Encoded'] = tmdrbs_pd_f.apply(lambda row: calculate_bmi_category(row['Height'], row['Weight']), axis=1)
tmdrbs_pd_f['Hyper'] = tmdrbs_pd_f.apply(lambda row: calculate_hypertension(row['Systolic'], row['Diastolic']), axis=1)


cols_sleep = ['BMI Encoded','Age','Sleep Duration','Systolic','Diastolic','Daily Steps']
# BMI Encoded : 1 (저체중), 2(정상체중), 3(과체중), 4(비만)
tmdrbs_sleep = tmdrbs_pd_f[cols_sleep]
# 예측
try:
    sleep_predictions = loaded_Sleep_RF.predict(tmdrbs_sleep)
    if sleep_predictions == 1:
        print('수면장애 위험군입니다.')
    else:
        print('수면장애 위험군이 아닙니다.')
except Exception as e:
    print(f"An error occurred during prediction: {e}")

#####################################################################
#####################################################################
cols_cardio = ['Systolic','Diastolic','Age','Weight']
tmdrbs_cardio = tmdrbs_pd_f[cols_cardio]
# 예측
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
# 예측
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
# 예측
try:
    liver_predictions = loaded_Liver_RF.predict(tmdrbs_liver)
    if cardio_predictions == 1:
        print('간암 위험군입니다.')
    else:
        print('간암 위험군이 아닙니다.')
except Exception as e:
    print(f"An error occurred during prediction: {e}")

######################################################################
cols_lung = ['Gender', 'Age', 'Smoke', 'Tired', 'Alco']
tmdrbs_lung = tmdrbs_pd_f[cols_lung]
# 예측
try:
    lung_predictions = loaded_Lung_LG.predict(tmdrbs_lung)
    if lung_predictions == 1:
        print('폐암 위험군입니다.')
    else:
        print('폐암 위험군이 아닙니다.')
except Exception as e:
    print(f"An error occurred during prediction: {e}")


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
print(categories)


recommendations = recommend_videos(categories)
# return JSONResponse({"recommendations": recommendations})


# from services.youtube import search_youtube_videos, get_video_details
# from services.similarity import calculate_similarity_tfidf, calculate_similarity_nlp

# CATEGORY_KEYWORDS = {
#     "수면장애": ["수면 건강"],
#     "심혈관질환": ["심 건강"],
#     "당뇨": ["혈당 관리"],
#     "간암": ["간 건강"],
#     "폐암": ["폐 건강"],
#     "식단 관리": ["식단 관리"],
#     "근력 운동": ["근력 운동"],
#     "스트레스 관리": ["스트레스 관리"],
#     "영양 보충제": ["영양 보충제"],
#     "정기 검진 중요성": ["정기 검진 중요성"]   
# }

# YOUTUBE_SEARCH_KEYWORDS = {
#     "수면 건강": ["수면장애, 예방, 관리"],
#     "심 건강": ["심혈관질환", "예방", "관리"],
#     "혈당 관리": ["당뇨", "예방", "관리"],
#     "간 건강": ["간암", "관리", "예방"],
#     "폐 건강": ["폐암", "관리", "예방"],
#     ## 위는 병 분류 모델과 관련 / 아래는 건강한 사람들을 위한 키워드
#     "식단 관리": ["노인","식단", "관리"],
#     "근력 운동": ["노인", "근력운동"],
#     "스트레스 관리": ["노인", "스트레스"],
#     "영양 보충제": ["노인", "영양","보충제"],
#     "정기 검진 중요성": ["노인", "건강검진"]
# }

# def recommend_videos(categories):
#     # 사용자 카테고리에 따라 키워드 생성
#     keywords = []
#     for category in categories:
#         if category in CATEGORY_KEYWORDS:
#             keywords.extend(CATEGORY_KEYWORDS[category])

#     search_keywords = []
#     for keyword in keywords:
#         if keyword in YOUTUBE_SEARCH_KEYWORDS:
#             search_keywords.extend(YOUTUBE_SEARCH_KEYWORDS[keyword])

#     # YouTube 검색 및 유사도 계산
#     search_results = search_youtube_videos(search_keywords)
#     video_ids = [item["id"]["videoId"] for item in search_results]
#     video_details = get_video_details(video_ids)

#     texts = [video["snippet"]["title"] + " " + video["snippet"]["description"] for video in video_details]
#     tfidf_scores = calculate_similarity_tfidf(texts, search_keywords)
#     nlp_scores = calculate_similarity_nlp(texts, search_keywords)

#     # 점수 계산 및 정렬
#     recommendations = []
#     for i, video in enumerate(video_details):
#         recommendations.append({
#             "title": video["snippet"]["title"],
#             "link": f"https://www.youtube.com/watch?v={video['id']}",
#             "score": 0.5 * tfidf_scores[i] + 0.5 * nlp_scores[i]
#         })
#     return sorted(recommendations, key=lambda x: x["score"], reverse=True)




