import time
import logging
from logging_setup import setup_logging
from model_loader import load_model
from audio_recorder import record_audio
from audio_processor import process_audio_file
from qa_processor import KoreanQAProcessor

def get_voice_answer(model, question, q_type):
    print(f"\n질문: {question}")
    print("스페이스바를 눌러 답변을 시작하고, 다시 눌러서 종료하세요.")
    
    audio_filename = record_audio(filename=f"{q_type.lower()}_recorded_audio.wav")
    if not audio_filename:
        logging.error("녹음이 취소되었습니다.")
        return None
        
    segments, info = process_audio_file(model, audio_filename)
    
    if segments is None:
        logging.error("STT 변환 실패")
        return None
    
    answer_text = " ".join([segment.text for segment in segments])
    logging.info(f"음성 답변: {answer_text}")
    return answer_text

def main():
    setup_logging()
    start_time = time.time()
    
    logging.info("모델 로딩 시작...")
    model = load_model()
    qa_processor = KoreanQAProcessor()
    
    questions = [
        ("이름", "이름이 무엇입니까?"),
        ("나이", "나이가 몇살입니까?"),
        ("직업", "직업이 무엇입니까?"),
        ("취미", "취미가 무엇입니까?"),
        ("TF", "김철수는 좋은 사람입니까?"),
        ("GENDER", "김철수는 어떤 성별입니까?"),
        ("CHOICE", "김철수의 직업은?", ["의사", "교사", "소프트웨어 엔지니어", "요리사"])
    ]
    
    answers = {}
    for q_type, question, *choices in questions:
        answer_text = get_voice_answer(model, question, q_type)
        if answer_text:
            if choices:
                processed_answer = qa_processor.get_answer(question, answer_text, q_type, choices[0])
            else:
                processed_answer = qa_processor.get_answer(question, answer_text, q_type)
            
            answers[q_type] = processed_answer
            print(f"처리된 답변: {processed_answer}")
            print("-" * 30)
    
    print("\n최종 결과:")
    for q_type, answer in answers.items():
        print(f"{q_type}: {answer}")
    
    total_time = time.time() - start_time
    logging.info(f"총 소요 시간: {total_time/60:.1f}분 ({total_time:.1f}초)")

if __name__ == "__main__":
    main()