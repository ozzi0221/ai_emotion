"""
콘텐츠 추천 유틸리티

회상치료 AI 아바타에서 사용자에게 적합한 콘텐츠를 추천하는 시스템입니다.
"""

import json
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from .text_processing import extract_memory_keywords, extract_emotions

class ContentRecommender:
    """회상치료 콘텐츠 추천 시스템"""
    
    def __init__(self):
        self.content_database = self._initialize_content_database()
        self.recommendation_weights = {
            'memory_match': 0.4,    # 기억 키워드 일치도
            'emotion_match': 0.3,   # 감정 일치도
            'popularity': 0.2,      # 인기도
            'recency': 0.1         # 최신성
        }
    
    def _initialize_content_database(self) -> Dict:
        """콘텐츠 데이터베이스를 초기화합니다"""
        return {
            'music': {
                '고향의봄': {
                    'title': '고향의 봄',
                    'artist': '이은하',
                    'year': '1960년대',
                    'youtube_query': '고향의 봄 이은하',
                    'keywords': ['고향', '봄', '어린시절', '시골'],
                    'emotions': ['그리운', '평온한'],
                    'description': '봄날 고향을 그리워하는 애틋한 마음이 담긴 노래',
                    'popularity': 95
                },
                '개여울': {
                    'title': '개여울',
                    'artist': '정미조',
                    'year': '1970년대',
                    'youtube_query': '개여울 정미조',
                    'keywords': ['시골', '강', '마을', '정겨운'],
                    'emotions': ['그리운', '평온한'],
                    'description': '시골 마을의 정겨운 풍경을 노래한 명곡',
                    'popularity': 88
                },
                '봉선화연정': {
                    'title': '봉선화 연정',
                    'artist': '이미자',
                    'year': '1960년대',
                    'youtube_query': '봉선화 연정 이미자',
                    'keywords': ['꽃', '연정', '사랑', '젊은시절'],
                    'emotions': ['그리운', '애틋한'],
                    'description': '젊은 날의 순수한 사랑을 그린 애절한 노래',
                    'popularity': 92
                },
                '애수': {
                    'title': '애수',
                    'artist': '이미자',
                    'year': '1960년대',
                    'youtube_query': '애수 이미자',
                    'keywords': ['그리움', '슬픔', '인생'],
                    'emotions': ['슬픈', '그리운'],
                    'description': '인생의 애환을 담은 이미자의 대표곡',
                    'popularity': 90
                },
                '상록수': {
                    'title': '상록수',
                    'artist': '현인',
                    'year': '1940년대',
                    'youtube_query': '상록수 현인',
                    'keywords': ['나무', '변치않는', '신념', '의지'],
                    'emotions': ['평온한', '희망적'],
                    'description': '변치 않는 의지와 신념을 노래한 명곡',
                    'popularity': 85
                }
            },
            'videos': {
                '60년대한국': {
                    'title': '1960년대 한국의 모습',
                    'description': '60년대 우리나라의 일상과 풍경',
                    'youtube_query': '1960년대 한국 옛날 영상',
                    'keywords': ['60년대', '옛날', '한국', '일상'],
                    'emotions': ['그리운', '평온한'],
                    'duration': '15분',
                    'popularity': 88
                },
                '시골마을': {
                    'title': '옛날 시골 마을 풍경',
                    'description': '전통 시골 마을의 아름다운 풍경',
                    'youtube_query': '옛날 시골 마을 풍경',
                    'keywords': ['시골', '마을', '농촌', '전통'],
                    'emotions': ['그리운', '평온한'],
                    'duration': '10분',
                    'popularity': 92
                },
                '학교생활': {
                    'title': '옛날 학교 교실 풍경',
                    'description': '추억의 학창시절 교실 모습',
                    'youtube_query': '옛날 학교 교실 추억',
                    'keywords': ['학교', '교실', '학창시절', '추억'],
                    'emotions': ['그리운', '기쁜'],
                    'duration': '8분',
                    'popularity': 85
                }
            },
            'activities': {
                '전통놀이': {
                    'title': '전통 놀이 체험',
                    'description': '옛날 아이들이 즐겼던 전통 놀이들',
                    'keywords': ['놀이', '전통', '어린시절', '게임'],
                    'emotions': ['기쁜', '그리운'],
                    'suggestions': ['공기놀이', '딱지치기', '구슬치기', '술래잡기'],
                    'popularity': 80
                },
                '전통음식': {
                    'title': '추억의 음식 이야기',
                    'description': '어릴 때 먹었던 맛있는 음식들',
                    'keywords': ['음식', '요리', '맛', '어머니'],
                    'emotions': ['그리운', '따뜻한'],
                    'suggestions': ['된장찌개', '김치', '엿', '떡', '전통차'],
                    'popularity': 90
                }
            },
            'topics': {
                '가족이야기': {
                    'title': '가족과의 추억',
                    'description': '소중한 가족들과 함께한 시간들',
                    'keywords': ['가족', '어머니', '아버지', '형제', '자녀'],
                    'emotions': ['따뜻한', '그리운', '기쁜'],
                    'questions': [
                        '어머니께서 해주신 음식 중 가장 기억에 남는 것은?',
                        '아버지와 함께 한 특별한 추억이 있으신가요?',
                        '형제자매들과 어떤 놀이를 하셨나요?'
                    ],
                    'popularity': 95
                },
                '첫경험': {
                    'title': '인생의 첫 경험들',
                    'description': '처음 경험했던 소중한 순간들',
                    'keywords': ['첫', '경험', '기억', '특별한'],
                    'emotions': ['기쁜', '설레는', '그리운'],
                    'questions': [
                        '첫 월급을 받으셨을 때 기분이 어떠셨나요?',
                        '처음 학교에 갔을 때를 기억하시나요?',
                        '첫 데이트는 어디서 하셨나요?'
                    ],
                    'popularity': 88
                }
            }
        }
    
    def recommend_content(self, user_input: str, user_history: Dict = None, content_type: str = 'all') -> List[Dict]:
        """사용자 입력을 바탕으로 콘텐츠를 추천합니다"""
        # 키워드와 감정 추출
        keywords = extract_memory_keywords(user_input)
        emotions = extract_emotions(user_input)
        
        recommendations = []
        
        # 콘텐츠 타입별로 추천
        if content_type in ['all', 'music']:
            recommendations.extend(self._recommend_music(keywords, emotions, user_history))
        
        if content_type in ['all', 'videos']:
            recommendations.extend(self._recommend_videos(keywords, emotions, user_history))
        
        if content_type in ['all', 'activities']:
            recommendations.extend(self._recommend_activities(keywords, emotions, user_history))
        
        if content_type in ['all', 'topics']:
            recommendations.extend(self._recommend_topics(keywords, emotions, user_history))
        
        # 점수순으로 정렬
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:5]  # 상위 5개만 반환
    
    def _recommend_music(self, keywords: Dict, emotions: List[str], user_history: Dict = None) -> List[Dict]:
        """음악 추천"""
        recommendations = []
        
        for music_id, music_info in self.content_database['music'].items():
            score = self._calculate_content_score(music_info, keywords, emotions, user_history)
            
            if score > 0:
                recommendations.append({
                    'type': 'music',
                    'id': music_id,
                    'title': music_info['title'],
                    'artist': music_info['artist'],
                    'youtube_query': music_info['youtube_query'],
                    'description': music_info['description'],
                    'score': score,
                    'reason': self._generate_recommendation_reason(music_info, keywords, emotions)
                })
        
        return recommendations
    
    def _recommend_videos(self, keywords: Dict, emotions: List[str], user_history: Dict = None) -> List[Dict]:
        """영상 추천"""
        recommendations = []
        
        for video_id, video_info in self.content_database['videos'].items():
            score = self._calculate_content_score(video_info, keywords, emotions, user_history)
            
            if score > 0:
                recommendations.append({
                    'type': 'video',
                    'id': video_id,
                    'title': video_info['title'],
                    'youtube_query': video_info['youtube_query'],
                    'description': video_info['description'],
                    'duration': video_info['duration'],
                    'score': score,
                    'reason': self._generate_recommendation_reason(video_info, keywords, emotions)
                })
        
        return recommendations
    
    def _recommend_activities(self, keywords: Dict, emotions: List[str], user_history: Dict = None) -> List[Dict]:
        """활동 추천"""
        recommendations = []
        
        for activity_id, activity_info in self.content_database['activities'].items():
            score = self._calculate_content_score(activity_info, keywords, emotions, user_history)
            
            if score > 0:
                recommendations.append({
                    'type': 'activity',
                    'id': activity_id,
                    'title': activity_info['title'],
                    'description': activity_info['description'],
                    'suggestions': activity_info['suggestions'],
                    'score': score,
                    'reason': self._generate_recommendation_reason(activity_info, keywords, emotions)
                })
        
        return recommendations
    
    def _recommend_topics(self, keywords: Dict, emotions: List[str], user_history: Dict = None) -> List[Dict]:
        """대화 주제 추천"""
        recommendations = []
        
        for topic_id, topic_info in self.content_database['topics'].items():
            score = self._calculate_content_score(topic_info, keywords, emotions, user_history)
            
            if score > 0:
                recommendations.append({
                    'type': 'topic',
                    'id': topic_id,
                    'title': topic_info['title'],
                    'description': topic_info['description'],
                    'questions': topic_info['questions'],
                    'score': score,
                    'reason': self._generate_recommendation_reason(topic_info, keywords, emotions)
                })
        
        return recommendations
    
    def _calculate_content_score(self, content: Dict, keywords: Dict, emotions: List[str], user_history: Dict = None) -> float:
        """콘텐츠 점수를 계산합니다"""
        score = 0.0
        
        # 키워드 매칭 점수
        content_keywords = content.get('keywords', [])
        keyword_match_count = 0
        total_keywords = 0
        
        for category, subcategories in keywords.items():
            if isinstance(subcategories, dict):
                for subcategory, words in subcategories.items():
                    total_keywords += len(words)
                    for word in words:
                        if word in content_keywords:
                            keyword_match_count += 1
            else:
                total_keywords += len(subcategories)
                for word in subcategories:
                    if word in content_keywords:
                        keyword_match_count += 1
        
        if total_keywords > 0:
            keyword_score = (keyword_match_count / total_keywords) * self.recommendation_weights['memory_match']
            score += keyword_score
        
        # 감정 매칭 점수
        content_emotions = content.get('emotions', [])
        emotion_match_count = sum(1 for emotion in emotions if emotion in content_emotions)
        if emotions:
            emotion_score = (emotion_match_count / len(emotions)) * self.recommendation_weights['emotion_match']
            score += emotion_score
        
        # 인기도 점수
        popularity = content.get('popularity', 50) / 100.0
        popularity_score = popularity * self.recommendation_weights['popularity']
        score += popularity_score
        
        # 사용자 히스토리 기반 조정
        if user_history:
            history_bonus = self._calculate_history_bonus(content, user_history)
            score += history_bonus
        
        return min(score, 1.0)  # 최대 1.0으로 제한
    
    def _calculate_history_bonus(self, content: Dict, user_history: Dict) -> float:
        """사용자 히스토리를 바탕으로 보너스 점수를 계산합니다"""
        bonus = 0.0
        
        favorite_topics = user_history.get('favorite_topics', {})
        content_keywords = content.get('keywords', [])
        
        for keyword in content_keywords:
            if keyword in favorite_topics:
                frequency = favorite_topics[keyword]
                bonus += min(frequency * 0.01, 0.1)  # 최대 10% 보너스
        
        return bonus
    
    def _generate_recommendation_reason(self, content: Dict, keywords: Dict, emotions: List[str]) -> str:
        """추천 이유를 생성합니다"""
        reasons = []
        
        # 키워드 기반 이유
        content_keywords = content.get('keywords', [])
        matched_keywords = []
        
        for category, subcategories in keywords.items():
            if isinstance(subcategories, dict):
                for subcategory, words in subcategories.items():
                    for word in words:
                        if word in content_keywords:
                            matched_keywords.append(word)
            else:
                for word in subcategories:
                    if word in content_keywords:
                        matched_keywords.append(word)
        
        if matched_keywords:
            reasons.append(f"'{', '.join(matched_keywords[:2])}'와 관련된 내용")
        
        # 감정 기반 이유
        content_emotions = content.get('emotions', [])
        matched_emotions = [emotion for emotion in emotions if emotion in content_emotions]
        
        if matched_emotions:
            emotion_map = {
                '그리운': '그리운 마음',
                '기쁜': '즐거운 추억',
                '평온한': '평온한 감정',
                '따뜻한': '따뜻한 느낌'
            }
            emotion_text = ', '.join([emotion_map.get(e, e) for e in matched_emotions[:2]])
            reasons.append(f"{emotion_text}을 불러일으킬 수 있는 콘텐츠")
        
        # 인기도 기반 이유
        popularity = content.get('popularity', 0)
        if popularity > 90:
            reasons.append("많은 분들이 좋아하시는 인기 콘텐츠")
        
        return " · ".join(reasons) if reasons else "회상치료에 도움이 되는 콘텐츠"
    
    def get_random_content(self, content_type: str = 'music', count: int = 1) -> List[Dict]:
        """랜덤 콘텐츠를 반환합니다"""
        if content_type not in self.content_database:
            return []
        
        items = list(self.content_database[content_type].items())
        selected = random.sample(items, min(count, len(items)))
        
        result = []
        for item_id, item_info in selected:
            result.append({
                'type': content_type,
                'id': item_id,
                **item_info
            })
        
        return result
    
    def get_popular_content(self, content_type: str = 'music', count: int = 5) -> List[Dict]:
        """인기 콘텐츠를 반환합니다"""
        if content_type not in self.content_database:
            return []
        
        items = [(item_id, item_info) for item_id, item_info in self.content_database[content_type].items()]
        items.sort(key=lambda x: x[1].get('popularity', 0), reverse=True)
        
        result = []
        for item_id, item_info in items[:count]:
            result.append({
                'type': content_type,
                'id': item_id,
                **item_info
            })
        
        return result
    
    def add_content(self, content_type: str, content_id: str, content_info: Dict) -> bool:
        """새로운 콘텐츠를 추가합니다"""
        if content_type not in self.content_database:
            self.content_database[content_type] = {}
        
        self.content_database[content_type][content_id] = content_info
        return True
    
    def update_popularity(self, content_type: str, content_id: str, feedback: int) -> bool:
        """콘텐츠 인기도를 업데이트합니다 (1: 좋음, -1: 나쁨)"""
        if (content_type in self.content_database and 
            content_id in self.content_database[content_type]):
            
            current_popularity = self.content_database[content_type][content_id].get('popularity', 50)
            new_popularity = max(0, min(100, current_popularity + feedback))
            self.content_database[content_type][content_id]['popularity'] = new_popularity
            return True
        
        return False

# 전역 추천 시스템 인스턴스
content_recommender = ContentRecommender()

# 편의 함수들
def recommend_for_user(user_input: str, user_history: Dict = None, content_type: str = 'all') -> List[Dict]:
    """사용자 추천 편의 함수"""
    return content_recommender.recommend_content(user_input, user_history, content_type)

def get_popular_music(count: int = 3) -> List[Dict]:
    """인기 음악 조회 편의 함수"""
    return content_recommender.get_popular_content('music', count)

def get_conversation_topics(count: int = 3) -> List[Dict]:
    """대화 주제 조회 편의 함수"""
    return content_recommender.get_popular_content('topics', count)

# 예시 사용법
if __name__ == "__main__":
    # 테스트 코드
    print("=== 콘텐츠 추천 테스트 ===")
    
    test_input = "어릴 때 고향에서 어머니와 함께 노래를 들었어요. 정말 그리워요."
    recommendations = recommend_for_user(test_input)
    
    print(f"추천 결과 ({len(recommendations)}개):")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. [{rec['type']}] {rec['title']}")
        print(f"   이유: {rec['reason']}")
        print(f"   점수: {rec['score']:.2f}")
        print()
    
    # 인기 음악 조회
    popular_music = get_popular_music(3)
    print("인기 음악:")
    for music in popular_music:
        print(f"- {music['title']} ({music['artist']})")
