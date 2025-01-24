from transformers import pipeline, AutoModelForQuestionAnswering, AutoTokenizer
from kiwipiepy import Kiwi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
import logging

class KoreanQAProcessor:
    def __init__(self):
        self.model_name = "monologg/koelectra-base-v3-finetuned-korquad"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForQuestionAnswering.from_pretrained(self.model_name)
        self.qa_pipeline = pipeline(
            "question-answering",
            model=self.model,
            tokenizer=self.tokenizer
        )
        self.kiwi = Kiwi()
        
        self.positive_words = {'예', '네', '맞아요', '그렇습니다', '마십니다', '합니다', '좋습니다'}
        self.negative_words = {'아니요', '아니오', '아닙니다', '안', '않', '없'}
        
        self.walking_levels = {
            '매우': 10000,
            '많이': 8000,
            '보통': 7000,
            '조금': 5600,
            '거의': 3000
        }
        
        # 한글 숫자 변환 사전 추가
        self.korean_numbers = {
            # 기본 한글 숫자
            '영': 0, '공': 0, '빵': 0,
            '일': 1, '하나': 1, '한': 1, '첫': 1,
            '이': 2, '둘': 2,
            '삼': 3, '셋': 3,
            '사': 4, '넷': 4,
            '오': 5, '다섯': 5,
            '육': 6, '여섯': 6,
            '칠': 7, '일곱': 7,
            '팔': 8, '여덟': 8,
            '구': 9, '아홉': 9,
            '십': 10, '열': 10,
            
            # 십단위 고유어
            '스무': 20, '스물': 20,
            '서른': 30,
            '마흔': 40,
            '쉰': 50,
            '예순': 60,
            '일흔': 70,
            '여든': 80,
            '아흔': 90
        }
        
        # 단위 정의
        self.number_units = {
            '십': 10,
            '백': 100,
            '천': 1000,
            '만': 10000,
            '억': 100000000
        }

    def extract_name(self, text):
        """이름 추출"""
        # "이름은 XXX" 패턴 찾기
        name_pattern = re.search(r'이름[은는이가]\s*([가-힣]{2,4})', text)
        if name_pattern:
            return name_pattern.group(1)
        
        # 형태소 분석으로 이름 후보 찾기
        morphs = self.kiwi.analyze(text)
        for word, pos, _, _ in morphs[0]:
            if pos == 'NNP' and len(word) >= 2 and len(word) <= 4:
                return word
        return None

    def extract_number(self, text):
        """숫자 추출 개선"""
        try:
            # 1. 아라비아 숫자 먼저 처리
            num_pattern = re.findall(r'\d+\.?\d*', text)
            if num_pattern:
                return num_pattern[0]
            
            # 2. 복합 한글 숫자 처리
            words = text.split()
            for word in words:
                total = 0
                current = 0
                unit = 1
                
                # 각 글자별로 처리
                for char in word:
                    if char in self.korean_numbers:
                        current = self.korean_numbers[char]
                    elif char in self.number_units:
                        if current == 0:
                            current = 1
                        unit = self.number_units[char]
                        total += (current * unit)
                        current = 0
                        unit = 1
                    else:
                        if current > 0:
                            total += current
                            current = 0
                
                if current > 0:
                    total += current
                
                if total > 0:
                    return str(total)
                
                # 단일 한글 숫자 확인
                if word in self.korean_numbers:
                    return str(self.korean_numbers[word])
            
            # 3. 형태소 분석을 통한 숫자 추출
            morphs = self.kiwi.analyze(text)
            for word_info in morphs[0]:
                if len(word_info) >= 2:
                    word, pos = word_info[0], word_info[1]
                    if pos in ['NR', 'SN']:  # 수사나 숫자를 찾음
                        if word in self.korean_numbers:
                            return str(self.korean_numbers[word])
                        try:
                            return str(int(word))
                        except ValueError:
                            continue

        except Exception as e:
            logging.error(f"Error processing number: {str(e)}")
        
        return None

    def check_yes_no(self, text):
        """예/아니오 응답 확인"""
        text = text.lower()
        
        # 긍정 단어 확인
        if any(word in text for word in self.positive_words):
            return "예"
            
        # 부정 단어 확인
        if any(word in text for word in self.negative_words):
            return "아니오"
            
        return None

    def extract_walking_level(self, text):
        """걷기 운동량 수준 추출"""
        for level, steps in self.walking_levels.items():
            if level in text:
                return steps
        return 7000  # 기본값: 보통

    def get_answer(self, question, context, question_type):
        """질문 유형에 따른 답변 추출"""
        logging.info(f"Processing answer - Type: {question_type}, Context: {context}")
        
        try:
            if question_type == 'name':
                answer = self.extract_name(context)
                logging.info(f"Extracted name: {answer}")
                return answer

            elif question_type == 'age':
                answer = self.extract_number(context)
                logging.info(f"Extracted age: {answer}")
                return answer

            elif question_type == 'sex':
                if '남' in context:
                    return '남자'
                elif '여' in context:
                    return '여자'
                return None

            elif question_type in ['weight', 'height', 'sleepTime', 'heartRate']:
                answer = self.extract_number(context)
                logging.info(f"Extracted number for {question_type}: {answer}")
                return answer

            elif question_type in ['drink', 'smoke', 'fatigue', 'cholesterol']:
                answer = self.check_yes_no(context)
                logging.info(f"Extracted yes/no for {question_type}: {answer}")
                return answer

            elif question_type == 'walking':
                answer = self.extract_walking_level(context)
                logging.info(f"Extracted walking level: {answer}")
                return answer

            elif question_type in ['systolicBP', 'diastolicBP']:
                numbers = re.findall(r'\d+', context)
                if len(numbers) >= 2:
                    return numbers[0] if question_type == 'systolicBP' else numbers[1]
                return None

            logging.warning(f"Unknown question type: {question_type}")
            return None

        except Exception as e:
            logging.error(f"Error processing answer: {str(e)}")
            return None