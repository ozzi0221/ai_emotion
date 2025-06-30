# 🫂 회상치료 AI 아바타 - 감정비서

> 치매 어르신을 위한 따뜻한 감정 케어와 회상치료를 제공하는 AI 아바타 시스템

![회상치료 AI 아바타](https://img.shields.io/badge/회상치료-AI%20아바타-ff6b9d?style=for-the-badge&logo=heart&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white) ![Google Gemini](https://img.shields.io/badge/Google%20Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)

## 🌟 프로젝트 소개

**회상치료 AI 아바타**는 치매 예방과 정서 케어를 위해 특별히 설계된 대화형 AI 시스템입니다. 어르신들의 과거 기억을 자연스럽게 떠올릴 수 있도록 도와주며, 따뜻하고 공감적인 대화를 통해 정서적 안정감을 제공합니다.

### 🎯 핵심 목표
- 💕 따뜻하고 공감적인 대화를 통한 정서 케어
- 🧠 과거 기억을 자연스럽게 회상하도록 유도
- 🎵 추억의 노래, 사진, 영상 등 콘텐츠 추천
- 🗣️ 실시간 음성 대화 (STT/TTS 지원)
- 📊 감정 상태 분석 및 메모리 키워드 추출

## ✨ 주요 기능

### 🎤 실시간 음성 대화
- **음성 인식 (STT)**: 브라우저 내장 Web Speech API 활용
- **음성 합성 (TTS)**: 자연스러운 한국어 음성 출력
- **실시간 스트리밍**: 문장 단위로 즉시 응답 제공
- **음성 설정**: 속도, 높낮이, 볼륨 개별 조정 가능

### 🧠 회상치료 특화 기능
- **맞춤형 질문**: 고향, 가족, 직업, 취미 등 개인적 추억 유도
- **감정 분석**: 대화 내용을 분석하여 감정 상태 파악
- **메모리 키워드**: 대화에서 추출한 추억 관련 키워드 시각화
- **점진적 유도**: 강요하지 않고 자연스럽게 기억 회상 돕기

### 🎵 멀티미디어 콘텐츠
- **유튜브 검색**: 언급된 노래, 장소 등 자동 검색 링크 제공
- **추억의 콘텐츠**: 시대별, 지역별 맞춤 콘텐츠 추천
- **연관 검색**: 대화 맥락에 맞는 관련 검색어 제안

### 🎭 아바타 시스템
- **상태별 애니메이션**: 대기/말하기 상태에 따른 비주얼 변화
- **감정 표현**: 대화 내용에 따른 감정 인디케이터 표시
- **비디오 fallback**: 비디오 파일이 없어도 정적 아바타로 작동

### 📱 사용자 친화적 인터페이스
- **직관적 UI**: 큰 버튼, 명확한 표시, 접근성 고려
- **반응형 디자인**: 태블릿, 모바일 등 다양한 화면 크기 지원
- **빠른 시작**: 원클릭 주제 선택 버튼
- **설정 저장**: 개인별 음성 설정 자동 저장

## 🛠️ 기술 스택

### Backend
- **Flask**: 웹 서버 프레임워크
- **Google Gemini API**: 대화형 AI 모델
- **Server-Sent Events**: 실시간 스트리밍 응답
- **Python**: 메인 프로그래밍 언어

### Frontend
- **HTML5**: 시맨틱 웹 구조
- **CSS3**: 모던 스타일링 (애니메이션, 그라데이션, 반응형)
- **JavaScript ES6+**: 동적 인터랙션
- **Web Speech API**: 브라우저 내장 음성 기능
- **Font Awesome**: 아이콘 라이브러리

### 특화 기능
- **정규식 기반 키워드 추출**: 추억 관련 단어 자동 분류
- **TTS 큐 시스템**: 자연스러운 음성 출력 관리
- **감정 분석 알고리즘**: 대화 내용 기반 감정 상태 파악

## 🚀 설치 및 실행

### 1️⃣ 사전 준비
```bash
# Python 3.8+ 설치 확인
python --version

# Git으로 프로젝트 클론 (또는 ZIP 다운로드)
git clone https://github.com/your-repo/avatar-therapy.git
cd avatar-therapy
```

### 2️⃣ Google Gemini API 키 발급
1. [Google AI Studio](https://makersuite.google.com/app/apikey) 접속
2. 새 API 키 생성
3. 생성된 키 복사 (나중에 사용)

### 3️⃣ 환경 설정
```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일 편집 (메모장, VS Code 등)
# GEMINI_API_KEY=your-gemini-api-key-here
# 위 줄에서 'your-gemini-api-key-here'를 실제 API 키로 교체
```

### 4️⃣ 실행 (Windows)
```batch
# 배치 파일로 자동 실행 (권장)
start.bat

# 또는 수동 실행
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```

### 5️⃣ 실행 (Linux/Mac)
```bash
# 셸 스크립트 실행 권한 부여
chmod +x start.sh

# 자동 실행
./start.sh

# 또는 수동 실행
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### 6️⃣ 브라우저 접속
서버가 시작되면 브라우저에서 `http://localhost:5000`에 접속하세요!

## 🎬 아바타 비디오 설정 (선택사항)

더욱 생동감 있는 아바타를 원한다면 비디오 파일을 추가할 수 있습니다:

### 📁 필요한 파일들
```
static/videos/
├── avatar_idle.mp4      # 대기 상태 비디오
├── avatar_speaking.mp4  # 말하기 상태 비디오
├── avatar_idle.webm     # 대기 상태 (WebM)
└── avatar_speaking.webm # 말하기 상태 (WebM)
```

### 🎨 제작 가이드
- **해상도**: 720x1280 (9:16 세로 비율)
- **길이**: 5-10초 반복 루프
- **내용**: 친근한 중년 캐릭터, 자연스러운 움직임
- **크기**: 5MB 이하 권장

자세한 제작 가이드는 `static/videos/README_UPDATED.md`를 참고하세요.

> 💡 **주의**: 비디오 파일이 없어도 시스템은 정상 작동하며, 정적 아바타 화면이 표시됩니다.

## 📋 사용법

### 🎯 빠른 시작
1. 브라우저에서 `http://localhost:5000` 접속
2. 화면의 **빠른 제안 버튼** 클릭:
   - 🏠 고향 이야기
   - 🎵 좋아하는 노래  
   - 👨‍👩‍👧‍👦 가족 추억
   - 💰 첫 월급
3. 아바타와 자연스럽게 대화 시작!

### 🎤 음성 대화
1. **마이크 버튼** 클릭 → 음성 인식 시작
2. 자연스럽게 말하기
3. 자동으로 텍스트 변환 및 응답
4. **스피커 버튼**으로 음성 출력 on/off

### ⚙️ 개인 설정
1. **설정 버튼** 클릭
2. 음성 속도, 높낮이, 볼륨 조절
3. 설정은 자동으로 저장됨

### 🎵 멀티미디어 활용
- 노래 제목 언급 시 → 자동 유튜브 검색 링크 제공
- 장소, 음식 등 언급 시 → 관련 콘텐츠 추천
- **"유튜브에서 ~ 검색해줘"** 버튼 클릭하여 추억 영상 감상

## 🔧 고급 설정

### 환경 변수 (.env)
```bash
# Google Gemini API 설정
GEMINI_API_KEY=your-actual-api-key-here

# Flask 서버 설정
FLASK_SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True  # 개발 모드
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# 아바타 비디오 파일명
AVATAR_IDLE_VIDEO=avatar_idle.mp4
AVATAR_SPEAKING_VIDEO=avatar_speaking.mp4

# TTS 기본 설정
DEFAULT_VOICE_RATE=0.8      # 말하기 속도 (0.1-10)
DEFAULT_VOICE_PITCH=1.0     # 음성 높낮이 (0-2)
DEFAULT_VOICE_VOLUME=0.8    # 음성 크기 (0-1)
DEFAULT_VOICE_LANG=ko-KR    # 언어 설정

# 회상치료 특화 설정
MAX_CONVERSATION_HISTORY=10    # 대화 기록 보관 수
RESPONSE_MAX_SENTENCES=3       # 최대 응답 문장 수
STREAMING_DELAY=0.1           # 스트리밍 지연 시간
```

### API 엔드포인트
- `POST /chat`: 메인 대화 API (스트리밍)
- `GET /youtube_search?q=검색어`: 유튜브 검색 URL 생성
- `POST /clear_history`: 대화 기록 초기화
- `GET /conversation_stats`: 대화 통계 조회
- `GET /health`: 서버 상태 확인

## 🎨 회상치료 특화 프롬프트

시스템은 다음과 같은 회상치료 전문 프롬프트로 작동합니다:

### 🎯 역할
- 고령자, 특히 치매 예방과 정서 케어를 위한 전문 AI
- 따뜻하고 공감적인 대화 상대
- 과거 기억을 자연스럽게 유도하는 가이드

### 💭 주요 대화 주제
- 🏠 **어린 시절 고향집**: \"어릴 때 살던 집은 어떤 모습이었나요?\"
- 💰 **첫 월급**: \"첫 월급 받으셨을 때 기분이 어떠셨어요?\"
- 👨‍👩‍👧‍👦 **가족 추억**: \"자녀분들과 가장 기억에 남는 순간은?\"
- 🎵 **추억의 노래**: \"젊을 때 즐겨 들으셨던 노래가 있나요?\"
- 🍚 **옛날 음식**: \"어머니가 해주시던 음식 중 기억나는 것은?\"
- 🎊 **명절**: \"추석이나 설날에 가족들과 어떻게 보내셨나요?\"

### 🤝 대화 원칙
- **존댓말 사용**: 어르신에 대한 예의와 존경
- **천천히 대화**: 2-3문장 이내, 짧고 명확하게
- **강요하지 않기**: 기억이 안 나셔도 자연스럽게 넘어가기
- **감정 공감**: \"정말 소중한 기억이네요\", \"그때 행복하셨겠어요\"
- **점진적 유도**: 구체적 질문보다는 열린 질문으로 시작

## 🔍 트러블슈팅

### ❌ API 키 오류
```
⚠️ 경고: GEMINI_API_KEY가 설정되지 않았습니다.
```
**해결방법**: `.env` 파일에서 `GEMINI_API_KEY`를 실제 API 키로 교체

### ❌ 음성 인식 안됨
**원인**: 브라우저가 Web Speech API를 지원하지 않음  
**해결방법**: Chrome, Edge, Safari 등 최신 브라우저 사용

### ❌ 비디오 재생 안됨
**원인**: 비디오 파일이 없거나 형식 문제  
**해결방법**: 자동으로 fallback 화면이 표시됨. 문제없이 사용 가능

### ❌ 서버 시작 안됨
```bash
# 포트 충돌 시
netstat -ano | findstr :5000
taskkill /F /PID <PID번호>

# 또는 다른 포트 사용
python app.py --port 5001
```

### ❌ 패키지 설치 오류
```bash
# pip 업그레이드
python -m pip install --upgrade pip

# 권한 문제 시 (Windows)
pip install -r requirements.txt --user
```

## 🤝 기여하기

이 프로젝트는 치매 어르신을 위한 의미 있는 기술 솔루션입니다. 기여를 환영합니다!

### 📝 기여 분야
- 🎨 **UI/UX 개선**: 더욱 어르신 친화적인 인터페이스
- 🧠 **AI 대화 품질**: 회상치료 전문성 강화
- 🎵 **콘텐츠 확장**: 연대별, 지역별 추억 콘텐츠
- 🔧 **기술 개선**: 성능 최적화, 새로운 기능
- 📖 **문서화**: 사용법, 가이드 개선
- 🌍 **접근성**: 시각/청각 장애인 지원 기능

### 🔄 개발 워크플로우
1. Fork 및 Clone
2. 기능 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 커밋 (`git commit -m 'Add amazing feature'`)
4. 푸시 (`git push origin feature/amazing-feature`)
5. Pull Request 생성

## 📜 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참고하세요.

## 🙏 감사의 말

- **Google Gemini**: 강력한 AI 대화 모델 제공
- **Web Speech API**: 브라우저 내장 음성 기능
- **Flask 커뮤니티**: 훌륭한 웹 프레임워크
- **오픈소스 생태계**: 무료 도구와 라이브러리들

---

<div align=\"center\">

### 💝 따뜻한 기술로 어르신들의 마음을 어루만져주는 AI 아바타

**회상치료 AI 아바타**는 단순한 챗봇이 아닙니다.  
어르신들의 소중한 추억을 함께 나누고, 정서적 안정감을 제공하는  
**마음이 있는 기술**입니다.

[🏠 홈으로 가기](#-회상치료-ai-아바타---감정비서) | [📞 문의하기](mailto:your-email@example.com) | [⭐ 별점 주기](https://github.com/your-repo/avatar-therapy)

</div>
