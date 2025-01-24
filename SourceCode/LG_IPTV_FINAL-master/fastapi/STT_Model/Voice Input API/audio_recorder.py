import pyaudio
import wave
import keyboard
import threading
import time
import os

def record_audio(filename="recorded_audio.wav", trigger_key='space'):
    """키 입력으로 제어되는 음성 녹음"""
    # Recorded_audio 디렉토리 생성
    save_dir = "Recorded_audio"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # 파일 경로 설정
    filepath = os.path.join(save_dir, filename)
    
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024

    frames = []
    recording = False
    finished = False

    def audio_callback(in_data, frame_count, time_info, status):
        if recording:
            frames.append(in_data)
        return (in_data, pyaudio.paContinue)

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                   channels=CHANNELS,
                   rate=RATE,
                   input=True,
                   frames_per_buffer=CHUNK,
                   stream_callback=audio_callback)

    stream.start_stream()
    
    print(f"'{trigger_key}' 키를 눌러 녹음을 시작/중지하세요. 'esc'를 누르면 종료됩니다.")
    
    while not finished:
        if keyboard.is_pressed(trigger_key):
            if not recording:
                recording = True
                print("\n녹음 시작...")
            else:
                recording = False
                finished = True
                print("\n녹음 중지...")
            time.sleep(0.3)  # 키 입력 디바운싱
        
        if keyboard.is_pressed('esc'):
            recording = False
            finished = True
            print("\n녹음 취소...")
    
    stream.stop_stream()
    stream.close()
    p.terminate()

    if frames:  # 녹음된 데이터가 있을 경우에만 파일 저장
        wf = wave.open(filepath, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        return filepath
    
    return None