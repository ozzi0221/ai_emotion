"""
보안 유틸리티

회상치료 AI 아바타의 보안 관련 기능들을 제공합니다.
"""

import re
import hashlib
import hmac
import secrets
import time
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import ipaddress
import urllib.parse

class SecurityManager:
    """보안 관리 클래스"""
    
    def __init__(self):
        self.blocked_ips = set()
        self.rate_limit_cache = {}
        self.suspicious_patterns = self._load_suspicious_patterns()
        self.allowed_domains = {
            'youtube.com', 'youtu.be', 'google.com',
            'googleapis.com', 'gemini.google.dev'
        }
        
    def _load_suspicious_patterns(self) -> List[str]:
        """의심스러운 패턴 목록을 로드합니다"""
        return [
            # SQL Injection 패턴
            r'(union|select|insert|update|delete|drop|create|alter)\s+',
            r'(or|and)\s+\d+\s*=\s*\d+',
            r'(\'|\"|`)\s*(or|and|union)',
            
            # XSS 패턴
            r'<script[^>]*>.*?</script>',
            r'javascript\s*:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            
            # Command Injection 패턴
            r'(\||;|&|`|\$\(|\${)',
            r'(rm|del|format|shutdown|reboot)\s+',
            
            # Path Traversal 패턴
            r'\.\./|\.\.\\',
            r'(file|ftp|http|https)://',
            
            # 기타 악의적 패턴
            r'eval\s*\(',
            r'exec\s*\(',
            r'system\s*\(',
            r'shell_exec\s*\(',
        ]
    
    def sanitize_input(self, text: str) -> str:
        """사용자 입력을 안전하게 정리합니다"""
        if not text:
            return ""
        
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)
        
        # 특수 문자 제한 (한글, 영문, 숫자, 기본 구두점만 허용)
        text = re.sub(r'[^\w\s가-힣.,!?~♪♫🎵😊😄😢💝❤️🏠🎼\-()]', '', text)
        
        # 연속된 공백 제거
        text = re.sub(r'\s+', ' ', text)
        
        # 앞뒤 공백 제거
        text = text.strip()
        
        # 길이 제한
        if len(text) > 500:
            text = text[:500]
        
        return text
    
    def validate_input(self, text: str) -> Tuple[bool, str]:
        """입력 유효성을 검사합니다"""
        if not text:
            return False, "입력이 비어있습니다."
        
        # 길이 검사
        if len(text) > 500:
            return False, "입력이 너무 깁니다. (최대 500자)"
        
        if len(text.strip()) < 1:
            return False, "의미있는 내용을 입력해주세요."
        
        # 악의적 패턴 검사
        for pattern in self.suspicious_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False, "부적절한 내용이 포함되어 있습니다."
        
        # 반복 문자 검사
        if re.search(r'(.)\1{10,}', text):
            return False, "과도한 반복 문자가 포함되어 있습니다."
        
        # 스팸성 내용 검사
        spam_keywords = ['광고', '판매', '구매', '링크', 'http', 'www', '.com', '.kr']
        spam_count = sum(1 for keyword in spam_keywords if keyword.lower() in text.lower())
        if spam_count >= 3:
            return False, "스팸성 내용으로 판단됩니다."
        
        return True, ""
    
    def check_rate_limit(self, client_ip: str, max_requests: int = 30, window_minutes: int = 1) -> Tuple[bool, Dict]:
        """요청 빈도 제한을 확인합니다"""
        current_time = time.time()
        window_start = current_time - (window_minutes * 60)
        
        if client_ip not in self.rate_limit_cache:
            self.rate_limit_cache[client_ip] = []
        
        # 오래된 요청 기록 제거
        self.rate_limit_cache[client_ip] = [
            req_time for req_time in self.rate_limit_cache[client_ip]
            if req_time > window_start
        ]
        
        # 현재 요청 추가
        self.rate_limit_cache[client_ip].append(current_time)
        
        request_count = len(self.rate_limit_cache[client_ip])
        
        if request_count > max_requests:
            return False, {
                'error': 'Too many requests',
                'requests': request_count,
                'max_requests': max_requests,
                'window_minutes': window_minutes,
                'retry_after': window_minutes * 60
            }
        
        return True, {
            'requests': request_count,
            'max_requests': max_requests,
            'remaining': max_requests - request_count
        }
    
    def is_blocked_ip(self, client_ip: str) -> bool:
        """IP가 차단되었는지 확인합니다"""
        try:
            ip = ipaddress.ip_address(client_ip)
            return client_ip in self.blocked_ips or self._is_in_blocked_ranges(ip)
        except ValueError:
            return True  # 잘못된 IP는 차단
    
    def _is_in_blocked_ranges(self, ip: ipaddress.ip_address) -> bool:
        """차단된 IP 범위에 포함되는지 확인합니다"""
        blocked_ranges = [
            # 예시: 특정 범위 차단
            # ipaddress.ip_network('192.168.1.0/24'),
        ]
        
        for blocked_range in blocked_ranges:
            if ip in blocked_range:
                return True
        
        return False
    
    def block_ip(self, client_ip: str, reason: str = "Security violation") -> bool:
        """IP를 차단합니다"""
        try:
            # IP 유효성 검사
            ipaddress.ip_address(client_ip)
            self.blocked_ips.add(client_ip)
            
            # 로그 기록
            self._log_security_event(f"IP blocked: {client_ip}, Reason: {reason}")
            return True
        except ValueError:
            return False
    
    def unblock_ip(self, client_ip: str) -> bool:
        """IP 차단을 해제합니다"""
        if client_ip in self.blocked_ips:
            self.blocked_ips.remove(client_ip)
            self._log_security_event(f"IP unblocked: {client_ip}")
            return True
        return False
    
    def validate_youtube_url(self, url: str) -> Tuple[bool, str]:
        """YouTube URL의 안전성을 검증합니다"""
        if not url:
            return False, "URL이 비어있습니다."
        
        try:
            parsed = urllib.parse.urlparse(url)
            
            # 도메인 검사
            if parsed.netloc.lower() not in ['www.youtube.com', 'youtube.com', 'youtu.be', 'm.youtube.com']:
                return False, "허용되지 않은 도메인입니다."
            
            # 프로토콜 검사
            if parsed.scheme.lower() not in ['http', 'https']:
                return False, "허용되지 않은 프로토콜입니다."
            
            # 경로 검사
            if parsed.netloc.lower() in ['youtube.com', 'www.youtube.com']:
                if not (parsed.path.startswith('/watch') or 
                       parsed.path.startswith('/results') or
                       parsed.path.startswith('/embed')):
                    return False, "허용되지 않은 YouTube 경로입니다."
            
            return True, ""
            
        except Exception as e:
            return False, f"URL 검증 오류: {str(e)}"
    
    def generate_secure_token(self, length: int = 32) -> str:
        """보안 토큰을 생성합니다"""
        return secrets.token_urlsafe(length)
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """비밀번호를 해시화합니다"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # PBKDF2를 사용한 해시화
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 반복 횟수
        )
        
        return password_hash.hex(), salt
    
    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """비밀번호를 검증합니다"""
        password_hash, _ = self.hash_password(password, salt)
        return hmac.compare_digest(password_hash, stored_hash)
    
    def create_csrf_token(self, session_id: str) -> str:
        """CSRF 토큰을 생성합니다"""
        timestamp = str(int(time.time()))
        message = f"{session_id}:{timestamp}"
        
        # HMAC 서명 생성
        secret_key = "your-csrf-secret-key"  # 실제로는 환경변수에서 로드
        signature = hmac.new(
            secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return f"{timestamp}.{signature}"
    
    def verify_csrf_token(self, token: str, session_id: str, max_age: int = 3600) -> bool:
        """CSRF 토큰을 검증합니다"""
        try:
            timestamp_str, signature = token.split('.', 1)
            timestamp = int(timestamp_str)
            
            # 토큰 만료 검사
            if time.time() - timestamp > max_age:
                return False
            
            # 서명 검증
            message = f"{session_id}:{timestamp_str}"
            secret_key = "your-csrf-secret-key"
            expected_signature = hmac.new(
                secret_key.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except (ValueError, TypeError):
            return False
    
    def log_security_event(self, event_type: str, details: Dict, client_ip: str = None) -> None:
        """보안 이벤트를 로깅합니다"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'client_ip': client_ip,
            'details': details
        }
        
        self._log_security_event(str(log_entry))
    
    def _log_security_event(self, message: str) -> None:
        """보안 이벤트를 파일에 기록합니다"""
        try:
            log_file = "security.log"
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now().isoformat()} - {message}\n")
        except Exception as e:
            print(f"보안 로그 기록 실패: {e}")
    
    def get_security_headers(self) -> Dict[str, str]:
        """보안 헤더를 반환합니다"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
                "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
                "img-src 'self' data: https:; "
                "media-src 'self' https:; "
                "connect-src 'self' https://generativelanguage.googleapis.com; "
                "frame-src https://www.youtube.com https://youtube.com"
            ),
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
    
    def check_suspicious_activity(self, user_input: str, client_ip: str) -> Tuple[bool, str]:
        """의심스러운 활동을 감지합니다"""
        # 입력 패턴 분석
        if self._contains_suspicious_patterns(user_input):
            self.log_security_event(
                'suspicious_input',
                {'input': user_input[:100], 'pattern_match': True},
                client_ip
            )
            return True, "의심스러운 입력 패턴이 감지되었습니다."
        
        # 요청 빈도 확인
        rate_ok, rate_info = self.check_rate_limit(client_ip)
        if not rate_ok:
            return True, "요청이 너무 빈번합니다."
        
        return False, ""
    
    def _contains_suspicious_patterns(self, text: str) -> bool:
        """의심스러운 패턴을 포함하고 있는지 확인합니다"""
        for pattern in self.suspicious_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def cleanup_old_logs(self, days_to_keep: int = 30) -> int:
        """오래된 로그를 정리합니다"""
        try:
            log_file = "security.log"
            if not os.path.exists(log_file):
                return 0
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            filtered_lines = []
            removed_count = 0
            
            for line in lines:
                try:
                    # 로그 라인에서 타임스탬프 추출
                    timestamp_str = line.split(' - ')[0]
                    log_date = datetime.fromisoformat(timestamp_str)
                    
                    if log_date > cutoff_date:
                        filtered_lines.append(line)
                    else:
                        removed_count += 1
                except:
                    # 파싱 실패 시 유지
                    filtered_lines.append(line)
            
            # 필터된 로그 다시 저장
            with open(log_file, 'w', encoding='utf-8') as f:
                f.writelines(filtered_lines)
            
            return removed_count
            
        except Exception as e:
            print(f"로그 정리 오류: {e}")
            return 0

# 전역 보안 매니저 인스턴스
security_manager = SecurityManager()

# 편의 함수들
def sanitize_user_input(text: str) -> str:
    """사용자 입력 정리 편의 함수"""
    return security_manager.sanitize_input(text)

def validate_user_input(text: str) -> Tuple[bool, str]:
    """사용자 입력 검증 편의 함수"""
    return security_manager.validate_input(text)

def check_rate_limit(client_ip: str) -> Tuple[bool, Dict]:
    """요청 빈도 확인 편의 함수"""
    return security_manager.check_rate_limit(client_ip)

def validate_youtube_url(url: str) -> Tuple[bool, str]:
    """YouTube URL 검증 편의 함수"""
    return security_manager.validate_youtube_url(url)

def get_security_headers() -> Dict[str, str]:
    """보안 헤더 조회 편의 함수"""
    return security_manager.get_security_headers()

# 예시 사용법
if __name__ == "__main__":
    # 테스트 코드
    print("=== 보안 기능 테스트 ===")
    
    # 입력 검증 테스트
    test_inputs = [
        "안녕하세요! 좋은 노래 추천해주세요.",
        "<script>alert('xss')</script>",
        "SELECT * FROM users WHERE id=1",
        "어릴 때 엄마와 함께 들었던 고향의 봄이 그리워요."
    ]
    
    for test_input in test_inputs:
        is_valid, message = validate_user_input(test_input)
        sanitized = sanitize_user_input(test_input)
        print(f"입력: {test_input[:30]}...")
        print(f"유효성: {is_valid}, 메시지: {message}")
        print(f"정리된 입력: {sanitized}")
        print("-" * 50)
    
    # URL 검증 테스트
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://malicious-site.com/video",
        "https://youtube.com/results?search_query=test"
    ]
    
    for url in test_urls:
        is_valid, message = validate_youtube_url(url)
        print(f"URL: {url}")
        print(f"유효성: {is_valid}, 메시지: {message}")
        print("-" * 50)
