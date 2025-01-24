from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from config import SessionLocal
from models import User, Detail
import logging

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# 데이터베이스 세션 생성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def parse_bool(value: str) -> bool:
    return value == "1"

# 사용자 및 상세 정보 저장 API
@router.post("/api/user/save")
async def save_user(
    name: str = Form(...),
    age: str = Form(...),
    gender: str = Form(...),
    weight: str = Form(...),
    height: str = Form(...),
    drinking_status: str = Form(...),
    smoking_status: str = Form(...),
    obesity_status: str = Form(...),
    fatigue_status: str = Form(...),
    systolic_bp: str = Form(...),
    diastolic_bp: str = Form(...),
    heart_rate: str = Form(...),
    daily_steps: str = Form(...),
    cholesterol_status: str = Form(...),
    daily_sleep: str = Form(...),
    hypertension_status: str = Form(...)
):
    try:
        # 데이터 변환
        age = int(age)
        gender = parse_bool(gender)
        weight = float(weight)
        height = float(height)
        drinking_status = parse_bool(drinking_status)
        smoking_status = parse_bool(smoking_status)
        obesity_status = parse_bool(obesity_status)
        fatigue_status = parse_bool(fatigue_status)
        systolic_bp = int(systolic_bp)
        diastolic_bp = int(diastolic_bp)
        heart_rate = int(heart_rate)
        daily_steps = int(daily_steps)
        cholesterol_status = parse_bool(cholesterol_status)
        daily_sleep = float(daily_sleep)
        hypertension_status = parse_bool(hypertension_status)

        # 데이터 출력 (터미널 출력)
        print(f"Received data: name={name}, age={age}, gender={gender}, weight={weight}, height={height}, "
              f"drinking_status={drinking_status}, smoking_status={smoking_status}, obesity_status={obesity_status}, "
              f"fatigue_status={fatigue_status}, systolic_bp={systolic_bp}, diastolic_bp={diastolic_bp}, "
              f"heart_rate={heart_rate}, daily_steps={daily_steps}, cholesterol_status={cholesterol_status}, "
              f"daily_sleep={daily_sleep}, hypertension_status={hypertension_status}")

        # 데이터 출력 (로그 기록)
        logger.info(f"Received data: name={name}, age={age}, gender={gender}, weight={weight}, height={height}, "
                    f"drinking_status={drinking_status}, smoking_status={smoking_status}, obesity_status={obesity_status}, "
                    f"fatigue_status={fatigue_status}, systolic_bp={systolic_bp}, diastolic_bp={diastolic_bp}, "
                    f"heart_rate={heart_rate}, daily_steps={daily_steps}, cholesterol_status={cholesterol_status}, "
                    f"daily_sleep={daily_sleep}, hypertension_status={hypertension_status}")
        db = next(get_db())

        # 사용자 데이터 저장
        new_user = User(
            name=name,
            age=age,
            gender=gender,
            weight=weight,
            height=height,
            bmi=round(weight / ((height / 100) ** 2), 2),  # BMI 계산
            drinking_status=drinking_status,
            smoking_status=smoking_status,
            obesity_status=obesity_status,
            fatigue_status=fatigue_status
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # 상세 정보 저장
        new_detail = Detail(
            user_id=new_user.user_id,
            systolic_bp=systolic_bp,
            diastolic_bp=diastolic_bp,
            heart_rate=heart_rate,
            daily_steps=daily_steps,
            cholesterol_status=cholesterol_status,
            daily_sleep=daily_sleep,
            hypertension_status=hypertension_status
        )
        db.add(new_detail)
        db.commit()
        db.refresh(new_detail)

        return JSONResponse({
            "message": "User and detail data saved successfully",
            "user_id": new_user.user_id,
            "detail_id": new_detail.detail_id
        })
    except Exception as e:
        logger.error(f"Error saving user and detail data: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

# 특정 사용자 및 상세 정보 조회 API
@router.get("/api/user/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    detail = db.query(Detail).filter(Detail.user_id == user_id).first()

    user_data = {
        "user_id": user.user_id,
        "name": user.name,
        "age": user.age,
        "gender": user.gender,
        "weight": user.weight,
        "height": user.height,
        "bmi": user.bmi,
        "drinking_status": user.drinking_status,
        "smoking_status": user.smoking_status,
        "obesity_status": user.obesity_status,
        "fatigue_status": user.fatigue_status,
    }

    if detail:
        user_data.update({
            "detail": {
                "detail_id": detail.detail_id,
                "systolic_bp": detail.systolic_bp,
                "diastolic_bp": detail.diastolic_bp,
                "heart_rate": detail.heart_rate,
                "daily_steps": detail.daily_steps,
                "cholesterol_status": detail.cholesterol_status,
                "daily_sleep": detail.daily_sleep,
                "hypertension_status": detail.hypertension_status
            }
        })

    return JSONResponse(user_data)

# 모든 사용자 및 상세 정보 조회 API
@router.get("/api/user/save")
async def get_all_users(db: Session = Depends(get_db)):
    print("Get all users check")
    users = db.query(User).all()
    user_list = []
    for user in users:
        detail = db.query(Detail).filter(Detail.user_id == user.user_id).first()
        user_data = {
            "user_id": user.user_id,
            "name": user.name,
            "age": user.age,
            "gender": user.gender,
            "weight": user.weight,
            "height": user.height,
            "bmi": user.bmi,
            "drinking_status": user.drinking_status,
            "smoking_status": user.smoking_status,
            "obesity_status": user.obesity_status,
            "fatigue_status": user.fatigue_status,
        }
        print("user data input check")
        if detail:
            user_data.update({
                "detail": {
                    "detail_id": detail.detail_id,
                    "systolic_bp": detail.systolic_bp,
                    "diastolic_bp": detail.diastolic_bp,
                    "heart_rate": detail.heart_rate,
                    "daily_steps": detail.daily_steps,
                    "cholesterol_status": detail.cholesterol_status,
                    "daily_sleep": detail.daily_sleep,
                    "hypertension_status": detail.hypertension_status
                }
            })
        user_list.append(user_data)

    return JSONResponse({"users": user_list})

# 사용자 삭제 API
@router.delete("/api/user/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    detail = db.query(Detail).filter(Detail.user_id == user_id).first()
    if detail:
        db.delete(detail)

    db.delete(user)
    db.commit()
    return {"message": "User and detail data deleted successfully"}
