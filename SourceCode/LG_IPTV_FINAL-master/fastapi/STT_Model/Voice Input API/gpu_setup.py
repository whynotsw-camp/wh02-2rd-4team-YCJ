import torch
import logging

def setup_gpu():
    """GPU 사용 가능 여부 확인 및 설정"""
    if torch.cuda.is_available():
        logging.info(f"GPU 사용 가능: {torch.cuda.get_device_name(0)}")
        return "cuda", "float16"
    else:
        logging.info("GPU 사용 불가능 - CPU 모드로 실행")
        return "cpu", "int8"