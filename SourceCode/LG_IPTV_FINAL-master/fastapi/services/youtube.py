import requests
import isodate

API_KEY = "AIzaSyB9EEtBLqsJ_OoTmT3uPJBMuVD4Wvqu8vw"

def search_youtube_videos(keywords, pageToken=None):
    query = "+".join(keywords)
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&maxResults=10&key={API_KEY}"
    if pageToken:
        url += f"&pageToken={pageToken}"
    response = requests.get(url).json()
    return response.get("items", []), response.get("nextPageToken")


def get_video_details(video_id):
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails,statistics&id={video_id}&key={API_KEY}"
    response = requests.get(url).json()
    video = response.get("items", [])[0]
    if not video:
        return None
    duration = isodate.parse_duration(video["contentDetails"]["duration"]).total_seconds()
    return {
        "videoId": video_id,
        "title": video["snippet"]["title"],
        "thumbnail": video["snippet"]["thumbnails"]["high"]["url"],
        "duration": duration,
        #"totalTime": 0  # Replace with actual value if tracked
    }   

# # 기존 진행 방식 wath_records를 array 형태로 구성 watch_records 이중 array 안dptj video_id로 구별되는 각 영상의 데이터를 저장 
# def record_watch_time(video_id, watched_time, duration, watch_records):
#     if video_id not in watch_records:
#         watch_records[video_id] = {"total_time": 0, "duration": duration, "percentage": 0}
#     watch_records[video_id]["total_time"] += watched_time
#     watch_records[video_id]["percentage"] = (watch_records[video_id]["total_time"] / duration) * 100
#     return watch_records[video_id]


# 추천 개선 방식: db에서 watch_records를 조회하여 video_id로 구별되는 각 영상의 데이터를 저장
# percentage 의 경우 현 파일에서 사용하지 않음
def record_watch_time(video_id, watched_time, duration):
    if not video_id:
        watch_records = {"total_time": 0, "duration": duration, "percentage": 0}
    watch_records["total_time"] += watched_time
    return watch_records