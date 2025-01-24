from fastapi import APIRouter, HTTPException, Form, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models import Video
from config import SessionLocal
from services.youtube import search_youtube_videos, get_video_details, record_watch_time

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 유튜브 영상 검색 API
@router.get("/api/videos/search/{keywords}")
async def search_videos(keywords: str, pageToken: str = None):
    keyword_list = keywords.split(",")
    videos, next_page_token = search_youtube_videos(keyword_list, pageToken)
    if not videos:
        raise HTTPException(status_code=404, detail="영상 정보를 찾을 수 없습니다.")
    return JSONResponse({"videos": videos, "nextPageToken": next_page_token})


# 유튜브 영상 세부 정보 API
@router.get("/api/videos/{video_id}")
async def video_details_api(video_id: str):
    video_data = get_video_details(video_id)
    if not video_data:
        raise HTTPException(status_code=404, detail="영상 정보를 찾을 수 없습니다.")
    return JSONResponse({"video": video_data})

@router.post("/api/videos/save")
async def save_video(
    user_id: int = Form(...),
    video_id: int = Form(...),
    title: str = Form(...),
    video_length: int = Form(...),
    category: str = Form(...),
    db: Session = Depends(get_db)
):
    existing_video = db.query(Video).filter(Video.video_id == video_id, Video.user_id == user_id).first()
    if existing_video:
        raise HTTPException(status_code=400, detail="영상 정보가 이미 존재합니다.")

    new_video = Video(
        video_id=video_id,
        user_id=user_id,
        title=title,
        video_length=video_length,
        viewing_time=0,
        category=category
    )
    db.add(new_video)
    db.commit()
    db.refresh(new_video)

    return JSONResponse({"message": "영상 정보가 저장되었습니다.", "video_id": new_video.video_id})

# 시청 기록 저장 API
@router.post("/api/videos/{video_id}/watch")
async def update_watch_time(
    video_id: int,
    user_id: int = Form(...),
    watched_time: int = Form(...),
    db: Session = Depends(get_db)
):
    video = db.query(Video).filter(Video.video_id == video_id, Video.user_id == user_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="영상 정보를 찾을 수 없습니다.")

    # 기존 방식 : video 변수에 viewing_time 값을 추가 후 db.commit()으로 업데이트
    video.viewing_time += watched_time
    if video.viewing_time > video.video_length:
        video.viewing_time = video.video_length  # 시청 시간이 영상 길이를 초과하지 않도록 설정
    
    # 추천된 개선 방식 : 기존 방식에 video ID를 인자로 넘겨주어 함수 내에서 업데이트
    new_video = Video(
        video_id=video_id,
        user_id=user_id,
        video_length=video.video_length,
        viewing_time=watched_time
    )

    video_length = video.video_length
    watch_records = record_watch_time(video_id, watched_time, video_length)

    new_video.viewing_time = watch_records["total_time"]

    db.add(new_video)
    db.commit()
    db.refresh(new_video)

    return JSONResponse({
        "message": "시청 기록이 업데이트되었습니다.",
        "viewing_time": video.viewing_time
    })

# 특정 사용자의 영상 정보 조회 API
@router.get("/api/videos/user/{user_id}")
async def get_user_videos(user_id: int, db: Session = Depends(get_db)):
    videos = db.query(Video).filter(Video.user_id == user_id).all()
    if not videos:
        raise HTTPException(status_code=404, detail="영상 정보를 찾을 수 없습니다.")

    return JSONResponse({"videos": [{"video_id": video.video_id, "title": video.title, "viewing_time": video.viewing_time, "video_length": video.video_length, "category": video.category} for video in videos]})

