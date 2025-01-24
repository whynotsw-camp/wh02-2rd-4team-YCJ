from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from model_loader import load_model
from audio_processor import process_audio_file
from qa_processor import KoreanQAProcessor
import uvicorn

'''
make the program run by one key
compress the process
or make the program like exe file
'''

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 모델 전역 초기화
model = load_model()
qa_processor = KoreanQAProcessor()

@app.post("/process-voice")
async def process_voice(
    audio: UploadFile = File(...),
    question: str = Form(...),  # Form 필드로 변경
    question_type: str = Form(...)  # Form 필드로 변경
):
    if not question or not question_type:
        raise HTTPException(status_code=400, detail="Question and question_type are required")
    
    logging.info(f"Received voice request - Question: {question}, Type: {question_type}")
    logging.info(f"Audio file size: {audio.size} bytes")
    
    # 임시 파일로 저장
    temp_file = f"temp_{question_type}.wav"
    try:
        # 임시 파일로 저장
        content = await audio.read()
        with open(temp_file, "wb") as f:
            f.write(content)
        logging.info(f"Saved temporary file: {temp_file}")
        
        # 오디오 처리
        segments, info = process_audio_file(model, temp_file)
        if segments is None:
            logging.error("Audio processing failed")
            return {"error": "음성 처리 실패"}
        
        # 텍스트 추출 및 유효성 검사
        answer_text = " ".join([segment.text for segment in segments])
        answer_text = answer_text.strip()
        
        if not answer_text:
            return {"error": "음성이 인식되지 않았습니다"}
            
        logging.info(f"Extracted text: {answer_text}")
        
        # QA 처리
        processed_answer = qa_processor.get_answer(question, answer_text, question_type)
        if not processed_answer:
            return {"error": "답변을 처리할 수 없습니다"}
            
        logging.info(f"Processed answer: {processed_answer}")
        
        return {
            "success": True,
            "raw_text": answer_text,
            "processed_answer": processed_answer
        }
    except Exception as e:
        logging.error(f"Error processing voice: {str(e)}")
        return {"error": str(e), "success": False}
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_file):
            os.remove(temp_file)
            logging.info(f"Removed temporary file: {temp_file}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
