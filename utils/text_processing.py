"""
텍스트 처리 유틸리티

회상치료 AI 아바타에서 사용되는 텍스트 처리 기능들을 제공합니다.
"""

import re
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# 한국어 회상치료 관련 키워드 사전
MEMORY_KEYWORDS = {
    '시간대': {
        '어린시절': ['어릴때', '어린시절', '초등학교', '국민학교', '어렸을때', '꼬마때', '아이때'],
        '청소년기': ['중학교', '고등학교', '청소년', '10대', '학창시절', '수험생', '입시'],
        '청년기': ['대학교', '20대', '젊었을때', '신혼', '결혼', '취업', '사회생활'],
        '장년기': ['30대', '40대', '중년', '직장생활', '승진', '아이들', '육아'],
        '노년기': ['50대', '60대', '은퇴', '손자', '손녀', '퇴직', '노후']
    },
    '장소': {
        '고향': ['고향', '시골', '농촌', '마을', '동네', '우리집', '친정', '시댁'],
        '학교': ['학교', '교실', '운동장', '도서관', '강당', '교무실', '학원'],
        '직장': ['회사', '사무실', '공장', '가게', '상점', '사업장', '일터'],
        '놀이장소': ['놀이터', '공원', '산', '강', '바다', '시장', '극장', '교회']
    },
    '인물': {
        '가족': ['어머니', '아버지', '엄마', '아빠', '할머니', '할아버지', '형', '누나', '언니', '동생', '남편', '아내', '아들', '딸', '며느리', '사위'],
        '친구': ['친구', '동창', '선배', '후배', '동기', '동료', '이웃', '선생님'],
        '연인': ['남자친구', '여자친구', '첫사랑', '애인', '연인', '좋아하던']
    },
    '활동': {
        '놀이': ['놀이', '게임', '숨바꼭질', '술래잡기', '공기놀이', '딱지치기', '구슬치기'],
        '음식': ['밥', '반찬', '김치', '된장찌개', '라면', '과자', '떡', '엿', '사탕'],
        '음악': ['노래', '음악', '가요', '트로트', '동요', '찬송가', '민요'],
        '명절': ['설날', '추석', '단오', '어버이날', '크리스마스', '생일']
    }
}

# 감정 관련 키워드
EMOTION_KEYWORDS = {
    '긍정적': ['기쁜', '행복한', '즐거운', '재미있는', '좋은', '따뜻한', '사랑스러운', '고마운', '뿌듯한'],
    '그리운': ['그리운', '보고싶은', '그때가', '아쉬운', '애틋한', '간절한'],
    '힘든': ['힘든', '어려운', '슬픈', '아픈', '고생', '고달픈', '괴로운'],
    '평온한': ['평온한', '조용한', '차분한', '편안한', '안락한', '고요한']
}

# 유튜브 검색 키워드 매핑
YOUTUBE_SEARCH_MAPPING = {
    '음악': {
        '고향의봄': '고향의 봄 노래 이은하',
        '개여울': '정미조 개여울',
        '봉선화': '봉선화 연정 이미자',
        '애수': '애수 이미자',
        '그대와 영원히': '그대와 영원히 양희은',
        '상록수': '상록수 현인',
        '목포의 눈물': '목포의 눈물 이난영'
    },
    '영상': {
        '60년대': '1960년대 한국 옛날 영상',
        '70년대': '1970년대 한국 옛날 사진',
        '80년대': '1980년대 추억 영상',
        '시골': '옛날 시골 마을 풍경',
        '학교': '옛날 학교 교실 추억'
    }
}

def extract_memory_keywords(text: str) -> Dict[str, List[str]]:
    """텍스트에서 회상치료 관련 키워드를 추출합니다."""
    found_keywords = {}
    
    for category, subcategories in MEMORY_KEYWORDS.items():
        for subcategory, keywords in subcategories.items():
            found_words = []
            for keyword in keywords:
                if keyword in text:
                    found_words.append(keyword)
            
            if found_words:
                if category not in found_keywords:
                    found_keywords[category] = {}
                found_keywords[category][subcategory] = found_words
    
    return found_keywords

def extract_emotions(text: str) -> List[str]:
    """텍스트에서 감정 키워드를 추출합니다."""
    emotions = []
    
    for emotion_type, keywords in EMOTION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                emotions.append(emotion_type)
                break
    
    return emotions

def extract_youtube_search_terms(text: str) -> List[str]:
    """텍스트에서 유튜브 검색어를 추출합니다."""
    search_terms = []
    
    # 직접적인 노래 제목 언급
    for song_key, search_term in YOUTUBE_SEARCH_MAPPING['음악'].items():
        if song_key in text:
            search_terms.append(search_term)
    
    # 시대적 배경 언급
    for era_key, search_term in YOUTUBE_SEARCH_MAPPING['영상'].items():
        if era_key in text:
            search_terms.append(search_term)
    
    # 패턴 기반 추출
    patterns = [
        r'(?:노래|음악|곡).*?[\'\"](.*?)[\'\"]*?(?:들려|틀어|찾아)',
        r'[\'\"](.*?)[\'\"]*?(?:노래|음악|곡)',
        r'(?:유튜브에서|검색해).*?[\'\"](.*?)[\'\"]*',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if match.strip():
                search_terms.append(match.strip() + ' 노래')
    
    return list(set(search_terms))  # 중복 제거

def clean_text(text: str) -> str:
    """텍스트를 정리합니다."""
    # 특수문자 제거 (일부 유지)
    text = re.sub(r'[^\w\s가-힣.,!?~♪♫🎵😊😄😢💝❤️🏠🎼]', '', text)
    
    # 연속된 공백 제거
    text = re.sub(r'\s+', ' ', text)
    
    # 앞뒤 공백 제거
    text = text.strip()
    
    return text

def is_appropriate_content(text: str) -> bool:
    """회상치료에 적절한 내용인지 확인합니다."""
    inappropriate_keywords = [
        '정치', '종교', '돈', '병', '죽음', '사고', '전쟁', '폭력', '욕설'
    ]
    
    text_lower = text.lower()
    for keyword in inappropriate_keywords:
        if keyword in text_lower:
            return False
    
    return True

def suggest_follow_up_questions(memory_keywords: Dict, emotions: List[str]) -> List[str]:
    """추출된 키워드와 감정을 바탕으로 후속 질문을 제안합니다."""
    questions = []
    
    # 시간대 기반 질문
    if '시간대' in memory_keywords:
        for period in memory_keywords['시간대'].keys():
            if period == '어린시절':
                questions.append("그때 집 앞은 어떤 모습이었나요?")
                questions.append("어릴 때 가장 좋아했던 놀이가 있으셨나요?")
            elif period == '청년기':
                questions.append("첫 직장은 어떠셨나요?")
                questions.append("그때 좋아하던 노래가 있으셨나요?")
    
    # 장소 기반 질문
    if '장소' in memory_keywords:
        if '고향' in memory_keywords['장소']:
            questions.append("고향에서 가장 기억에 남는 곳은 어디인가요?")
        if '학교' in memory_keywords['장소']:
            questions.append("학창시절 가장 재미있었던 추억이 있으신가요?")
    
    # 감정 기반 질문
    if '긍정적' in emotions:
        questions.append("그때 정말 행복하셨겠어요. 또 다른 좋은 기억은 없으신가요?")
    if '그리운' in emotions:
        questions.append("정말 그리우셨겠어요. 그분들과의 추억을 더 들려주세요.")
    
    return questions[:3]  # 최대 3개까지만 반환

def format_response_with_emotions(text: str, emotions: List[str]) -> str:
    """감정에 맞는 이모지와 표현을 추가합니다."""
    if '긍정적' in emotions:
        text += " 😊"
    elif '그리운' in emotions:
        text += " 💝"
    elif '힘든' in emotions:
        text += " 따뜻하게 안아드리고 싶어요."
    elif '평온한' in emotions:
        text += " 🌸"
    
    return text

def create_conversation_summary(conversations: List[Dict]) -> Dict:
    """대화 내용을 요약합니다."""
    if not conversations:
        return {}
    
    total_keywords = {}
    total_emotions = []
    topics = set()
    
    for conv in conversations:
        text = conv.get('user', '') + ' ' + conv.get('assistant', '')
        
        # 키워드 집계
        keywords = extract_memory_keywords(text)
        for category, subcategories in keywords.items():
            if category not in total_keywords:
                total_keywords[category] = {}
            for subcategory, words in subcategories.items():
                if subcategory not in total_keywords[category]:
                    total_keywords[category][subcategory] = []
                total_keywords[category][subcategory].extend(words)
        
        # 감정 집계
        emotions = extract_emotions(text)
        total_emotions.extend(emotions)
        
        # 주제 추출
        for category in keywords.keys():
            topics.add(category)
    
    return {
        'keywords': total_keywords,
        'emotions': list(set(total_emotions)),
        'topics': list(topics),
        'conversation_count': len(conversations),
        'summary_date': datetime.now().isoformat()
    }

def generate_personalized_greeting(user_history: Dict) -> str:
    """사용자 히스토리를 바탕으로 개인화된 인사말을 생성합니다."""
    if not user_history:
        return "안녕하세요! 오늘은 어떤 추억을 나누고 싶으시나요? 😊"
    
    topics = user_history.get('topics', [])
    emotions = user_history.get('emotions', [])
    
    if '시간대' in topics:
        return "안녕하세요! 지난번에 말씀해주신 추억이 정말 인상깊었어요. 오늘은 또 어떤 이야기를 들려주실까요? 😊"
    elif '긍정적' in emotions:
        return "안녕하세요! 지난번 행복한 이야기를 들려주셔서 저도 기뻤어요. 오늘도 좋은 추억 이야기해볼까요? 💝"
    else:
        return "안녕하세요! 오늘은 어떤 소중한 추억을 함께 나누고 싶으시나요? 😊"

# 텍스트 검증 함수들
def validate_user_input(text: str) -> Tuple[bool, str]:
    """사용자 입력을 검증합니다."""
    if not text or not text.strip():
        return False, "메시지를 입력해 주세요."
    
    if len(text) > 500:
        return False, "메시지가 너무 깁니다. 500자 이내로 입력해 주세요."
    
    if not is_appropriate_content(text):
        return False, "회상치료에 적합하지 않은 내용입니다. 다른 주제로 이야기해볼까요?"
    
    return True, ""

# 예시 사용법
if __name__ == "__main__":
    # 테스트 코드
    test_text = "어릴 때 고향에서 어머니와 함께 고향의 봄 노래를 들었어요. 정말 그리운 추억이에요."
    
    print("=== 텍스트 처리 테스트 ===")
    print(f"원본 텍스트: {test_text}")
    print(f"메모리 키워드: {extract_memory_keywords(test_text)}")
    print(f"감정: {extract_emotions(test_text)}")
    print(f"유튜브 검색어: {extract_youtube_search_terms(test_text)}")
    print(f"후속 질문: {suggest_follow_up_questions(extract_memory_keywords(test_text), extract_emotions(test_text))}")
