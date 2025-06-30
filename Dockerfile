# 회상치료 AI 아바타 Docker 이미지
FROM python:3.9-slim

# 메타데이터
LABEL name="avatar-emotion-assistant"
LABEL version="1.0.0"
LABEL description="회상치료 AI 아바타 - 감정비서"

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 필요한 디렉토리 생성
RUN mkdir -p logs memory_data static/videos static/images backups

# 포트 노출
EXPOSE 5000

# 환경 변수 설정
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# 헬스체크 설정
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# 비root 사용자 생성 및 전환
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# 애플리케이션 실행
CMD ["python", "app.py"]
