from services.youtube import search_youtube_videos, get_video_details
from services.similarity import calculate_similarity_tfidf, calculate_similarity_nlp

CATEGORY_KEYWORDS = {
    "수면장애": ["수면 건강"],
    "심혈관질환": ["심 건강"],
    "당뇨": ["혈당 관리"],
    "간암": ["간 건강"],
    "폐암": ["폐 건강"],
    "식단 관리": ["식단 관리"],
    "근력 운동": ["근력 운동"],
    "스트레스 관리": ["스트레스 관리"],
    "영양 보충제": ["영양 보충제"],
    "정기 검진 중요성": ["정기 검진 중요성"]   
} 

YOUTUBE_SEARCH_KEYWORDS = {
    "수면 건강": ["수면장애, 예방, 관리"],
    "심 건강": ["심혈관질환", "예방", "관리"],
    "혈당 관리": ["당뇨", "예방", "관리"],
    "간 건강": ["간암", "관리", "예방"],
    "폐 건강": ["폐암", "관리", "예방"],
    ## 위는 병 분류 모델과 관련 / 아래는 건강한 사람들을 위한 키워드
    "식단 관리": ["노인","식단", "관리"],
    "근력 운동": ["노인", "근력운동"],
    "스트레스 관리": ["노인", "스트레스"],
    "영양 보충제": ["노인", "영양","보충제"],
    "정기 검진 중요성": ["노인", "건강검진"]
}

def recommend_videos(categories):
    # 사용자 카테고리에 따라 키워드 생성
    keywords = []
    for category in categories:
        if category in CATEGORY_KEYWORDS:
            keywords.extend(CATEGORY_KEYWORDS[category])

    search_keywords = []
    for keyword in keywords:
        if keyword in YOUTUBE_SEARCH_KEYWORDS:
            search_keywords.extend(YOUTUBE_SEARCH_KEYWORDS[keyword])

    # YouTube 검색 및 유사도 계산
    search_results, _ = search_youtube_videos(search_keywords)
    video_ids = [item["id"]["videoId"] for item in search_results if "id" in item and "videoId" in item["id"]]
    video_details = [get_video_details(video_id) for video_id in video_ids]

    texts = [video["title"] for video in video_details if video]
    tfidf_scores = calculate_similarity_tfidf(texts, search_keywords)
    nlp_scores = calculate_similarity_nlp(texts, search_keywords)

    # 점수 계산 및 정렬
    recommendations = []
    for i, video in enumerate(video_details):
        if video:
            recommendations.append({
                "title": video["title"],
                "thumbnail": video["thumbnail"],
                "duration": video["duration"],
                "link": f"https://www.youtube.com/watch?v={video['videoId']}",
                "score": 0.5 * tfidf_scores[i] + 0.5 * nlp_scores[i]
            })
    return sorted(recommendations, key=lambda x: x["score"], reverse=True)
