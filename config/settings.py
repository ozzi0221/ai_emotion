"""
설정 관리 모듈

회상치료 AI 아바타의 모든 설정을 중앙에서 관리합니다.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

@dataclass
class APIConfig:
    """API 관련 설정"""
    gemini_api_key: str = os.getenv('GEMINI_API_KEY', 'your-gemini-api-key-here')
    gemini_model: str = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
    max_tokens: int = int(os.getenv('GEMINI_MAX_TOKENS', '500'))
    temperature: float = float(os.getenv('GEMINI_TEMPERATURE', '0.7'))
    top_p: float = float(os.getenv('GEMINI_TOP_P', '0.8'))
    top_k: int = int(os.getenv('GEMINI_TOP_K', '40'))

@dataclass
class AppConfig:
    """애플리케이션 설정"""
    secret_key: str = os.getenv('FLASK_SECRET_KEY', 'change-this-secret-key')
    debug: bool = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host: str = os.getenv('FLASK_HOST', '0.0.0.0')
    port: int = int(os.getenv('FLASK_PORT', '5000'))
    threaded: bool = os.getenv('FLASK_THREADED', 'True').lower() == 'true'

@dataclass
class ConversationConfig:
    """대화 관련 설정"""
    max_history: int = int(os.getenv('MAX_CONVERSATION_HISTORY', '10'))
    max_response_sentences: int = int(os.getenv('RESPONSE_MAX_SENTENCES', '3'))
    streaming_delay: float = float(os.getenv('STREAMING_DELAY', '0.1'))
    max_input_length: int = int(os.getenv('MAX_INPUT_LENGTH', '500'))
    context_window: int = int(os.getenv('CONTEXT_WINDOW', '5'))

@dataclass
class TTSConfig:
    """TTS 관련 설정"""
    default_rate: float = float(os.getenv('DEFAULT_VOICE_RATE', '0.8'))
    default_pitch: float = float(os.getenv('DEFAULT_VOICE_PITCH', '1.0'))
    default_volume: float = float(os.getenv('DEFAULT_VOICE_VOLUME', '0.8'))
    default_lang: str = os.getenv('DEFAULT_VOICE_LANG', 'ko-KR')
    max_queue_size: int = int(os.getenv('TTS_MAX_QUEUE_SIZE', '10'))

@dataclass
class AvatarConfig:
    """아바타 관련 설정"""
    idle_video: str = os.getenv('AVATAR_IDLE_VIDEO', 'avatar_idle.mp4')
    speaking_video: str = os.getenv('AVATAR_SPEAKING_VIDEO', 'avatar_speaking.mp4')
    video_format: str = os.getenv('AVATAR_VIDEO_FORMAT', 'mp4')
    fallback_enabled: bool = os.getenv('AVATAR_FALLBACK_ENABLED', 'True').lower() == 'true'

@dataclass
class SecurityConfig:
    """보안 관련 설정"""
    rate_limit_requests: int = int(os.getenv('RATE_LIMIT_REQUESTS', '30'))
    rate_limit_window: int = int(os.getenv('RATE_LIMIT_WINDOW', '60'))
    csrf_enabled: bool = os.getenv('CSRF_ENABLED', 'True').lower() == 'true'
    csrf_secret: str = os.getenv('CSRF_SECRET', 'change-this-csrf-secret')
    blocked_keywords: list = os.getenv('BLOCKED_KEYWORDS', '').split(',')
    max_failed_attempts: int = int(os.getenv('MAX_FAILED_ATTEMPTS', '5'))

@dataclass
class MemoryConfig:
    """메모리 관리 설정"""
    memory_dir: str = os.getenv('MEMORY_DIR', 'memory_data')
    max_memory_size_mb: int = int(os.getenv('MAX_MEMORY_SIZE_MB', '100'))
    cleanup_interval_days: int = int(os.getenv('CLEANUP_INTERVAL_DAYS', '30'))
    auto_backup: bool = os.getenv('AUTO_BACKUP', 'True').lower() == 'true'
    backup_dir: str = os.getenv('BACKUP_DIR', 'backups')

@dataclass
class LoggingConfig:
    """로깅 설정"""
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    log_file: str = os.getenv('LOG_FILE', 'app.log')
    security_log_file: str = os.getenv('SECURITY_LOG_FILE', 'security.log')
    max_log_size_mb: int = int(os.getenv('MAX_LOG_SIZE_MB', '10'))
    backup_count: int = int(os.getenv('LOG_BACKUP_COUNT', '5'))
    log_format: str = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

@dataclass
class ContentConfig:
    """콘텐츠 관련 설정"""
    youtube_api_key: str = os.getenv('YOUTUBE_API_KEY', '')
    content_cache_ttl: int = int(os.getenv('CONTENT_CACHE_TTL', '3600'))
    max_recommendations: int = int(os.getenv('MAX_RECOMMENDATIONS', '5'))
    enable_content_filtering: bool = os.getenv('ENABLE_CONTENT_FILTERING', 'True').lower() == 'true'

class Config:
    """전체 설정 클래스"""
    
    def __init__(self):
        self.api = APIConfig()
        self.app = AppConfig()
        self.conversation = ConversationConfig()
        self.tts = TTSConfig()
        self.avatar = AvatarConfig()
        self.security = SecurityConfig()
        self.memory = MemoryConfig()
        self.logging = LoggingConfig()
        self.content = ContentConfig()
        
        # 설정 검증
        self._validate_config()
    
    def _validate_config(self):
        """설정값들의 유효성을 검증합니다"""
        errors = []
        
        # API 키 확인
        if self.api.gemini_api_key == 'your-gemini-api-key-here':
            errors.append("GEMINI_API_KEY가 설정되지 않았습니다.")
        
        # 포트 범위 확인
        if not (1 <= self.app.port <= 65535):
            errors.append(f"잘못된 포트 번호: {self.app.port}")
        
        # 메모리 설정 확인
        if self.memory.max_memory_size_mb < 1:
            errors.append("메모리 크기는 1MB 이상이어야 합니다.")
        
        # TTS 설정 확인
        if not (0.1 <= self.tts.default_rate <= 3.0):
            errors.append("TTS 속도는 0.1-3.0 범위여야 합니다.")
        
        if not (0.0 <= self.tts.default_pitch <= 2.0):
            errors.append("TTS 피치는 0.0-2.0 범위여야 합니다.")
        
        if not (0.0 <= self.tts.default_volume <= 1.0):
            errors.append("TTS 볼륨은 0.0-1.0 범위여야 합니다.")
        
        # 보안 설정 확인
        if self.security.rate_limit_requests < 1:
            errors.append("요청 제한은 1 이상이어야 합니다.")
        
        if errors:
            print("⚠️  설정 검증 오류:")
            for error in errors:
                print(f"   - {error}")
            print("   .env 파일을 확인하고 올바른 값으로 수정해주세요.")
    
    def get_gemini_generation_config(self) -> Dict[str, Any]:
        """Gemini API 생성 설정을 반환합니다"""
        return {
            'max_output_tokens': self.api.max_tokens,
            'temperature': self.api.temperature,
            'top_p': self.api.top_p,
            'top_k': self.api.top_k
        }
    
    def get_flask_config(self) -> Dict[str, Any]:
        """Flask 설정을 반환합니다"""
        return {
            'SECRET_KEY': self.app.secret_key,
            'DEBUG': self.app.debug,
            'THREADED': self.app.threaded
        }
    
    def get_tts_settings(self) -> Dict[str, Any]:
        """TTS 설정을 반환합니다"""
        return {
            'rate': self.tts.default_rate,
            'pitch': self.tts.default_pitch,
            'volume': self.tts.default_volume,
            'lang': self.tts.default_lang
        }
    
    def export_config(self) -> Dict[str, Any]:
        """현재 설정을 딕셔너리로 내보냅니다 (민감한 정보 제외)"""
        return {
            'app': {
                'debug': self.app.debug,
                'host': self.app.host,
                'port': self.app.port,
                'threaded': self.app.threaded
            },
            'conversation': {
                'max_history': self.conversation.max_history,
                'max_response_sentences': self.conversation.max_response_sentences,
                'streaming_delay': self.conversation.streaming_delay,
                'max_input_length': self.conversation.max_input_length
            },
            'tts': {
                'default_rate': self.tts.default_rate,
                'default_pitch': self.tts.default_pitch,
                'default_volume': self.tts.default_volume,
                'default_lang': self.tts.default_lang
            },
            'avatar': {
                'idle_video': self.avatar.idle_video,
                'speaking_video': self.avatar.speaking_video,
                'video_format': self.avatar.video_format
            },
            'security': {
                'rate_limit_requests': self.security.rate_limit_requests,
                'rate_limit_window': self.security.rate_limit_window,
                'csrf_enabled': self.security.csrf_enabled
            },
            'memory': {
                'memory_dir': self.memory.memory_dir,
                'max_memory_size_mb': self.memory.max_memory_size_mb,
                'cleanup_interval_days': self.memory.cleanup_interval_days
            },
            'content': {
                'max_recommendations': self.content.max_recommendations,
                'enable_content_filtering': self.content.enable_content_filtering
            }
        }
    
    def create_directories(self):
        """필요한 디렉토리들을 생성합니다"""
        directories = [
            self.memory.memory_dir,
            self.memory.backup_dir,
            'static/videos',
            'static/images',
            'logs'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def __str__(self) -> str:
        """설정 정보를 문자열로 반환합니다"""
        config_info = [
            "회상치료 AI 아바타 설정 정보:",
            f"- 디버그 모드: {self.app.debug}",
            f"- 서버 주소: {self.app.host}:{self.app.port}",
            f"- 최대 대화 기록: {self.conversation.max_history}개",
            f"- 최대 응답 문장: {self.conversation.max_response_sentences}개",
            f"- TTS 기본 속도: {self.tts.default_rate}x",
            f"- 요청 제한: {self.security.rate_limit_requests}회/{self.security.rate_limit_window}초",
            f"- 메모리 디렉토리: {self.memory.memory_dir}",
            f"- 최대 메모리 크기: {self.memory.max_memory_size_mb}MB"
        ]
        
        return "\n".join(config_info)

# 전역 설정 인스턴스
config = Config()

# 편의 함수들
def get_config() -> Config:
    """전역 설정 인스턴스를 반환합니다"""
    return config

def reload_config():
    """설정을 다시 로드합니다"""
    global config
    load_dotenv(override=True)
    config = Config()

def get_system_prompt() -> str:
    """회상치료 AI 시스템 프롬프트를 반환합니다"""
    return """당신은 고령자, 특히 치매 예방과 정서 케어를 위한 회상치료 AI 아바타입니다.

[역할]
- 어르신과 따뜻하고 공감 있는 대화를 나누며, 과거의 기억을 자연스럽게 떠올릴 수 있도록 유도합니다.
- 어르신이 요청하거나 좋아할 수 있는 옛 사진, 영상, 노래 등 추억의 콘텐츠를 추천하거나 검색합니다.
- 대화는 항상 친절하고 천천히, 2~3문장 이내로 말하며, 감정을 존중하고 부드럽게 유도합니다.

[회상 질문 주제 예시]
- 어린 시절 고향집
- 첫 월급을 받았던 날
- 자녀들과 보낸 추억
- 좋아했던 노래나 음식
- 군대 시절
- 추석과 설날

[음악/사진/영상 요청 대응]
- 어르신이 말한 단어에서 관련 유튜브 검색어를 추출해주세요.
- 검색어는 **"유튜브에서 ~ 검색해줘"** 형태로 변환하여 응답에 포함하세요.

[감정 기반 응답 가이드]
- 어르신의 반응이 긍정적이면 그 감정을 강화해주는 말을 해주세요.
- 기억이 안 난다고 하면 절대 억지로 끌어내려 하지 말고 부드럽게 넘어가세요.

항상 존댓말을 사용하고, 따뜻하고 친근한 톤으로 대화하세요."""

# 예시 사용법
if __name__ == "__main__":
    print("=== 설정 정보 ===")
    print(config)
    print("\n=== 설정 검증 ===")
    
    # 필요한 디렉토리 생성
    config.create_directories()
    print("필요한 디렉토리들이 생성되었습니다.")
    
    # 설정 내보내기 테스트
    exported = config.export_config()
    print(f"\n설정 내보내기 완료: {len(exported)}개 섹션")
