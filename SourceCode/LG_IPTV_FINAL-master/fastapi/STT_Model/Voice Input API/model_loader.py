import time
import logging
from faster_whisper import WhisperModel
from gpu_setup import setup_gpu

def load_model():
    """모델 로딩"""
    start_time = time.time()
    device, compute_type = setup_gpu()
    model = WhisperModel("large-v3", device=device, compute_type=compute_type)
    load_time = time.time() - start_time
    logging.info(f"모델 로딩 완료 (소요 시간: {load_time:.2f}초)")
    return model