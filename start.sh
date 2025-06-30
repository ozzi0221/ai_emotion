#!/bin/bash

echo "🚀 회상치료 AI 아바타 서버 시작 중..."

# 가상환경 확인
if [ ! -d "venv" ]; then
    echo "📦 가상환경 생성 중..."
    python -m venv venv
fi

# 가상환경 활성화
echo "🔧 가상환경 활성화 중..."
source venv/bin/activate

# 의존성 설치
echo "📚 패키지 설치 중..."
pip install -r requirements.txt

# 환경 변수 체크
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일을 찾을 수 없습니다. .env.example을 참고하여 생성해주세요."
    exit 1
fi

# API 키 체크
if grep -q "your-gemini-api-key-here" .env; then
    echo "⚠️  Google Gemini API 키를 설정해주세요!"
    echo "   1. https://makersuite.google.com/app/apikey 에서 API 키 발급"
    echo "   2. .env 파일의 GEMINI_API_KEY 값 수정"
    echo ""
    read -p "API 키를 설정했다면 엔터를 누르세요..."
fi

# 서버 시작
echo "🎯 서버 시작..."
echo "💖 회상치료 AI 아바타가 http://localhost:5000 에서 실행됩니다"
echo ""
python app.py
