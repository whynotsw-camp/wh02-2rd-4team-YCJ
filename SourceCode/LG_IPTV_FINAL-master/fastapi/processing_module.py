# BMI Encoded 만드는 함수
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