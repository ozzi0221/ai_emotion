"""
메모리 관리 유틸리티

회상치료 AI 아바타의 대화 기록과 사용자 프로필을 관리합니다.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
import hashlib

class MemoryManager:
    """대화 기록과 사용자 메모리를 관리하는 클래스"""
    
    def __init__(self, memory_dir: str = "memory_data"):
        self.memory_dir = memory_dir
        self.ensure_memory_directory()
        
    def ensure_memory_directory(self):
        """메모리 디렉토리가 존재하는지 확인하고 생성"""
        if not os.path.exists(self.memory_dir):
            os.makedirs(self.memory_dir)
    
    def generate_user_id(self, identifier: str = "default") -> str:
        """사용자 식별자를 생성합니다"""
        # 간단한 해시 기반 사용자 ID 생성
        return hashlib.md5(identifier.encode()).hexdigest()[:8]
    
    def save_conversation(self, user_id: str, conversation: Dict) -> bool:
        """대화를 저장합니다"""
        try:
            user_file = os.path.join(self.memory_dir, f"user_{user_id}.json")
            
            # 기존 데이터 로드
            user_data = self.load_user_data(user_id)
            
            # 새 대화 추가
            if 'conversations' not in user_data:
                user_data['conversations'] = []
            
            conversation['timestamp'] = datetime.now().isoformat()
            conversation['id'] = len(user_data['conversations']) + 1
            
            user_data['conversations'].append(conversation)
            user_data['last_updated'] = datetime.now().isoformat()
            
            # 저장
            with open(user_file, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"대화 저장 오류: {e}")
            return False
    
    def load_user_data(self, user_id: str) -> Dict:
        """사용자 데이터를 로드합니다"""
        user_file = os.path.join(self.memory_dir, f"user_{user_id}.json")
        
        if os.path.exists(user_file):
            try:
                with open(user_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"사용자 데이터 로드 오류: {e}")
                return self.create_empty_user_data()
        else:
            return self.create_empty_user_data()
    
    def create_empty_user_data(self) -> Dict:
        """빈 사용자 데이터 구조를 생성합니다"""
        return {
            'conversations': [],
            'profile': {
                'preferences': {},
                'memory_themes': {},
                'favorite_content': [],
                'emotional_state': 'neutral'
            },
            'statistics': {
                'total_conversations': 0,
                'favorite_topics': {},
                'conversation_frequency': {},
                'last_active': None
            },
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
    
    def get_recent_conversations(self, user_id: str, limit: int = 10) -> List[Dict]:
        """최근 대화를 가져옵니다"""
        user_data = self.load_user_data(user_id)
        conversations = user_data.get('conversations', [])
        
        # 시간순으로 정렬하고 최근 대화만 반환
        recent = sorted(conversations, key=lambda x: x.get('timestamp', ''), reverse=True)
        return recent[:limit]
    
    def analyze_user_preferences(self, user_id: str) -> Dict:
        """사용자의 선호도를 분석합니다"""
        user_data = self.load_user_data(user_id)
        conversations = user_data.get('conversations', [])
        
        if not conversations:
            return {}
        
        # 주제별 빈도 분석
        topic_frequency = defaultdict(int)
        emotion_frequency = defaultdict(int)
        time_preferences = defaultdict(int)
        
        for conv in conversations:
            # 메모리 키워드 분석
            memory_keywords = conv.get('memory_keywords', {})
            for category, subcategories in memory_keywords.items():
                topic_frequency[category] += 1
                if isinstance(subcategories, dict):
                    for subcategory in subcategories.keys():
                        topic_frequency[f"{category}_{subcategory}"] += 1
            
            # 시간대 분석
            timestamp = conv.get('timestamp', '')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    hour = dt.hour
                    if 6 <= hour < 12:
                        time_preferences['morning'] += 1
                    elif 12 <= hour < 18:
                        time_preferences['afternoon'] += 1
                    elif 18 <= hour < 22:
                        time_preferences['evening'] += 1
                    else:
                        time_preferences['night'] += 1
                except:
                    pass
        
        return {
            'favorite_topics': dict(topic_frequency),
            'time_preferences': dict(time_preferences),
            'total_conversations': len(conversations),
            'analysis_date': datetime.now().isoformat()
        }
    
    def update_user_profile(self, user_id: str, profile_updates: Dict) -> bool:
        """사용자 프로필을 업데이트합니다"""
        try:
            user_data = self.load_user_data(user_id)
            
            # 프로필 업데이트
            if 'profile' not in user_data:
                user_data['profile'] = {}
            
            user_data['profile'].update(profile_updates)
            user_data['last_updated'] = datetime.now().isoformat()
            
            # 저장
            user_file = os.path.join(self.memory_dir, f"user_{user_id}.json")
            with open(user_file, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"프로필 업데이트 오류: {e}")
            return False
    
    def get_conversation_context(self, user_id: str, context_length: int = 5) -> str:
        """대화 컨텍스트를 문자열로 반환합니다"""
        recent_conversations = self.get_recent_conversations(user_id, context_length)
        
        context_parts = []
        for conv in reversed(recent_conversations):  # 시간순으로 정렬
            user_msg = conv.get('user', '')
            assistant_msg = conv.get('assistant', '')
            
            if user_msg and assistant_msg:
                context_parts.append(f"사용자: {user_msg}")
                context_parts.append(f"아바타: {assistant_msg}")
        
        return "\n".join(context_parts)
    
    def find_similar_conversations(self, user_id: str, keywords: List[str], limit: int = 3) -> List[Dict]:
        """유사한 대화를 찾습니다"""
        user_data = self.load_user_data(user_id)
        conversations = user_data.get('conversations', [])
        
        if not conversations or not keywords:
            return []
        
        # 키워드 매칭 점수 계산
        scored_conversations = []
        for conv in conversations:
            score = 0
            content = (conv.get('user', '') + ' ' + conv.get('assistant', '')).lower()
            
            for keyword in keywords:
                if keyword.lower() in content:
                    score += 1
            
            if score > 0:
                conv['similarity_score'] = score
                scored_conversations.append(conv)
        
        # 점수순으로 정렬하고 반환
        scored_conversations.sort(key=lambda x: x['similarity_score'], reverse=True)
        return scored_conversations[:limit]
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> int:
        """오래된 데이터를 정리합니다"""
        cleanup_count = 0
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        try:
            for filename in os.listdir(self.memory_dir):
                if filename.startswith('user_') and filename.endswith('.json'):
                    file_path = os.path.join(self.memory_dir, filename)
                    user_id = filename.replace('user_', '').replace('.json', '')
                    
                    user_data = self.load_user_data(user_id)
                    conversations = user_data.get('conversations', [])
                    
                    # 오래된 대화 필터링
                    filtered_conversations = []
                    for conv in conversations:
                        timestamp_str = conv.get('timestamp', '')
                        if timestamp_str:
                            try:
                                conv_date = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                if conv_date > cutoff_date:
                                    filtered_conversations.append(conv)
                                else:
                                    cleanup_count += 1
                            except:
                                # 파싱 실패 시 유지
                                filtered_conversations.append(conv)
                        else:
                            # 타임스탬프 없는 경우 유지
                            filtered_conversations.append(conv)
                    
                    # 변경사항이 있으면 저장
                    if len(filtered_conversations) != len(conversations):
                        user_data['conversations'] = filtered_conversations
                        user_data['last_updated'] = datetime.now().isoformat()
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(user_data, f, ensure_ascii=False, indent=2)
        
        except Exception as e:
            print(f"데이터 정리 오류: {e}")
        
        return cleanup_count
    
    def export_user_data(self, user_id: str, include_conversations: bool = True) -> Optional[Dict]:
        """사용자 데이터를 내보냅니다"""
        try:
            user_data = self.load_user_data(user_id)
            
            export_data = {
                'user_id': user_id,
                'profile': user_data.get('profile', {}),
                'statistics': user_data.get('statistics', {}),
                'preferences': self.analyze_user_preferences(user_id),
                'export_date': datetime.now().isoformat()
            }
            
            if include_conversations:
                export_data['conversations'] = user_data.get('conversations', [])
            
            return export_data
        except Exception as e:
            print(f"데이터 내보내기 오류: {e}")
            return None
    
    def get_memory_statistics(self) -> Dict:
        """전체 메모리 통계를 반환합니다"""
        try:
            total_users = 0
            total_conversations = 0
            total_size = 0
            
            for filename in os.listdir(self.memory_dir):
                if filename.startswith('user_') and filename.endswith('.json'):
                    total_users += 1
                    file_path = os.path.join(self.memory_dir, filename)
                    total_size += os.path.getsize(file_path)
                    
                    user_id = filename.replace('user_', '').replace('.json', '')
                    user_data = self.load_user_data(user_id)
                    total_conversations += len(user_data.get('conversations', []))
            
            return {
                'total_users': total_users,
                'total_conversations': total_conversations,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / 1024 / 1024, 2),
                'average_conversations_per_user': round(total_conversations / max(total_users, 1), 2),
                'statistics_date': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"통계 생성 오류: {e}")
            return {}

# 전역 메모리 매니저 인스턴스
memory_manager = MemoryManager()

# 편의 함수들
def save_conversation(user_id: str, user_message: str, assistant_message: str, metadata: Dict = None) -> bool:
    """대화 저장 편의 함수"""
    conversation = {
        'user': user_message,
        'assistant': assistant_message,
        'metadata': metadata or {}
    }
    return memory_manager.save_conversation(user_id, conversation)

def get_user_context(user_id: str, context_length: int = 5) -> str:
    """사용자 컨텍스트 조회 편의 함수"""
    return memory_manager.get_conversation_context(user_id, context_length)

def analyze_preferences(user_id: str) -> Dict:
    """사용자 선호도 분석 편의 함수"""
    return memory_manager.analyze_user_preferences(user_id)

# 예시 사용법
if __name__ == "__main__":
    # 테스트 코드
    test_user_id = "test_user"
    
    print("=== 메모리 관리 테스트 ===")
    
    # 대화 저장 테스트
    save_conversation(
        test_user_id,
        "어릴 때 고향에서 살았어요",
        "고향에서의 추억을 더 들려주세요 😊",
        {"keywords": ["고향", "어릴때"], "emotions": ["그리운"]}
    )
    
    # 사용자 데이터 조회
    user_data = memory_manager.load_user_data(test_user_id)
    print(f"저장된 대화 수: {len(user_data.get('conversations', []))}")
    
    # 선호도 분석
    preferences = analyze_preferences(test_user_id)
    print(f"분석 결과: {preferences}")
    
    # 메모리 통계
    stats = memory_manager.get_memory_statistics()
    print(f"전체 통계: {stats}")
