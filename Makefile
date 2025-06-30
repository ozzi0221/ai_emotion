# 회상치료 AI 아바타 Makefile
# 개발, 테스트, 배포를 위한 자동화 스크립트

.PHONY: help install dev-install test lint format security clean build docker run stop logs deploy backup restore

# 기본 변수
PYTHON := python3
PIP := pip3
PROJECT_NAME := avatar-emotion-assistant
DOCKER_IMAGE := $(PROJECT_NAME):latest
DOCKER_COMPOSE := docker-compose
PORT := 5000

# 색상 정의
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# 기본 타겟
help: ## 도움말 표시
	@echo "$(BLUE)회상치료 AI 아바타 - 감정비서$(NC)"
	@echo "$(BLUE)================================$(NC)"
	@echo ""
	@echo "$(GREEN)사용 가능한 명령어:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(GREEN)예시:$(NC)"
	@echo "  make install     - 의존성 설치"
	@echo "  make test        - 테스트 실행"
	@echo "  make run         - 개발 서버 실행"
	@echo "  make docker      - Docker 이미지 빌드"

# 설치 및 설정
install: ## 기본 의존성 설치
	@echo "$(GREEN)📦 기본 의존성을 설치하고 있습니다...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✅ 설치 완료!$(NC)"

dev-install: ## 개발 의존성 포함 설치
	@echo "$(GREEN)📦 개발 의존성을 설치하고 있습니다...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -e ".[dev,test]"
	pre-commit install
	@echo "$(GREEN)✅ 개발 환경 설정 완료!$(NC)"

# 코드 품질
format: ## 코드 포매팅 (Black + isort)
	@echo "$(GREEN)🎨 코드를 포매팅하고 있습니다...$(NC)"
	black . --line-length=100
	isort . --profile black --line-length=100
	@echo "$(GREEN)✅ 포매팅 완료!$(NC)"

lint: ## 코드 린팅 (flake8 + mypy)
	@echo "$(GREEN)🔍 코드를 검사하고 있습니다...$(NC)"
	flake8 . --max-line-length=100
	mypy . --ignore-missing-imports
	@echo "$(GREEN)✅ 린팅 완료!$(NC)"

security: ## 보안 검사 (bandit + safety)
	@echo "$(GREEN)🔒 보안 검사를 실행하고 있습니다...$(NC)"
	bandit -r . -x tests/
	safety check
	@echo "$(GREEN)✅ 보안 검사 완료!$(NC)"

check: format lint security ## 모든 코드 품질 검사 실행
	@echo "$(GREEN)✅ 모든 코드 품질 검사가 완료되었습니다!$(NC)"

# 테스트
test: ## 모든 테스트 실행
	@echo "$(GREEN)🧪 테스트를 실행하고 있습니다...$(NC)"
	$(PYTHON) -m pytest tests/ -v

test-unit: ## 단위 테스트만 실행
	@echo "$(GREEN)🧪 단위 테스트를 실행하고 있습니다...$(NC)"
	$(PYTHON) -m pytest tests/ -v -m "unit"

test-integration: ## 통합 테스트만 실행
	@echo "$(GREEN)🧪 통합 테스트를 실행하고 있습니다...$(NC)"
	$(PYTHON) -m pytest tests/ -v -m "integration"

test-security: ## 보안 테스트만 실행
	@echo "$(GREEN)🧪 보안 테스트를 실행하고 있습니다...$(NC)"
	$(PYTHON) -m pytest tests/ -v -m "security"

test-coverage: ## 커버리지와 함께 테스트 실행
	@echo "$(GREEN)🧪 커버리지 테스트를 실행하고 있습니다...$(NC)"
	$(PYTHON) -m pytest tests/ --cov=. --cov-report=html --cov-report=term
	@echo "$(GREEN)📊 커버리지 리포트가 htmlcov/ 디렉토리에 생성되었습니다.$(NC)"

# 개발 서버
run: ## 개발 서버 실행
	@echo "$(GREEN)🚀 개발 서버를 시작합니다...$(NC)"
	@echo "$(BLUE)서버 주소: http://localhost:$(PORT)$(NC)"
	$(PYTHON) app.py

run-debug: ## 디버그 모드로 서버 실행
	@echo "$(GREEN)🐛 디버그 모드로 서버를 시작합니다...$(NC)"
	@echo "$(BLUE)서버 주소: http://localhost:$(PORT)$(NC)"
	FLASK_DEBUG=True $(PYTHON) app.py

run-prod: ## 프로덕션 모드로 서버 실행
	@echo "$(GREEN)🏭 프로덕션 모드로 서버를 시작합니다...$(NC)"
	gunicorn --bind 0.0.0.0:$(PORT) --workers 4 app:app

# Docker 관련
docker-build: ## Docker 이미지 빌드
	@echo "$(GREEN)🐳 Docker 이미지를 빌드하고 있습니다...$(NC)"
	docker build -t $(DOCKER_IMAGE) .
	@echo "$(GREEN)✅ Docker 이미지 빌드 완료!$(NC)"

docker-run: ## Docker 컨테이너 실행
	@echo "$(GREEN)🐳 Docker 컨테이너를 실행합니다...$(NC)"
	docker run -d --name $(PROJECT_NAME) -p $(PORT):$(PORT) $(DOCKER_IMAGE)
	@echo "$(GREEN)✅ 컨테이너가 실행되었습니다: http://localhost:$(PORT)$(NC)"

docker-stop: ## Docker 컨테이너 중지
	@echo "$(YELLOW)🛑 Docker 컨테이너를 중지합니다...$(NC)"
	docker stop $(PROJECT_NAME) || true
	docker rm $(PROJECT_NAME) || true
	@echo "$(GREEN)✅ 컨테이너가 중지되었습니다.$(NC)"

docker-logs: ## Docker 컨테이너 로그 확인
	@echo "$(GREEN)📋 Docker 컨테이너 로그:$(NC)"
	docker logs -f $(PROJECT_NAME)

# Docker Compose
compose-up: ## Docker Compose로 전체 스택 실행
	@echo "$(GREEN)🐳 Docker Compose로 전체 스택을 시작합니다...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✅ 서비스가 시작되었습니다!$(NC)"
	@echo "$(BLUE)웹 인터페이스: http://localhost:80$(NC)"
	@echo "$(BLUE)모니터링: http://localhost:3000$(NC)"

compose-down: ## Docker Compose 스택 중지
	@echo "$(YELLOW)🛑 Docker Compose 스택을 중지합니다...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✅ 스택이 중지되었습니다.$(NC)"

compose-logs: ## Docker Compose 로그 확인
	@echo "$(GREEN)📋 Docker Compose 로그:$(NC)"
	$(DOCKER_COMPOSE) logs -f

compose-restart: ## Docker Compose 재시작
	@echo "$(YELLOW)🔄 Docker Compose를 재시작합니다...$(NC)"
	$(DOCKER_COMPOSE) restart

# 데이터 관리
backup: ## 데이터 백업
	@echo "$(GREEN)💾 데이터를 백업하고 있습니다...$(NC)"
	mkdir -p backups
	tar -czf backups/backup_$(shell date +%Y%m%d_%H%M%S).tar.gz memory_data/ logs/
	@echo "$(GREEN)✅ 백업이 완료되었습니다.$(NC)"

restore: ## 최신 백업에서 데이터 복원
	@echo "$(YELLOW)⚠️  데이터를 복원합니다. 기존 데이터는 덮어쓰여집니다!$(NC)"
	@read -p "계속하시겠습니까? [y/N]: " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		latest_backup=$$(ls -t backups/backup_*.tar.gz 2>/dev/null | head -n1); \
		if [ -n "$$latest_backup" ]; then \
			echo "$(GREEN)📂 $$latest_backup에서 복원 중...$(NC)"; \
			tar -xzf "$$latest_backup"; \
			echo "$(GREEN)✅ 복원이 완료되었습니다.$(NC)"; \
		else \
			echo "$(RED)❌ 백업 파일을 찾을 수 없습니다.$(NC)"; \
		fi \
	else \
		echo "$(YELLOW)복원이 취소되었습니다.$(NC)"; \
	fi

clean-data: ## 모든 데이터 삭제 (주의!)
	@echo "$(RED)⚠️  경고: 모든 데이터를 삭제합니다!$(NC)"
	@read -p "정말로 모든 데이터를 삭제하시겠습니까? [y/N]: " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		rm -rf memory_data/ logs/ __pycache__/ .pytest_cache/ htmlcov/; \
		echo "$(GREEN)✅ 데이터가 삭제되었습니다.$(NC)"; \
	else \
		echo "$(YELLOW)삭제가 취소되었습니다.$(NC)"; \
	fi

# 정리
clean: ## 빌드 아티팩트 정리
	@echo "$(GREEN)🧹 빌드 아티팩트를 정리하고 있습니다...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .pytest_cache/ .mypy_cache/ .coverage htmlcov/
	@echo "$(GREEN)✅ 정리 완료!$(NC)"

clean-docker: ## Docker 이미지 및 컨테이너 정리
	@echo "$(GREEN)🧹 Docker 리소스를 정리하고 있습니다...$(NC)"
	docker system prune -f
	docker volume prune -f
	@echo "$(GREEN)✅ Docker 정리 완료!$(NC)"

# 배포
deploy-staging: ## 스테이징 환경에 배포
	@echo "$(GREEN)🚀 스테이징 환경에 배포 중...$(NC)"
	# 여기에 스테이징 배포 로직 추가
	@echo "$(GREEN)✅ 스테이징 배포 완료!$(NC)"

deploy-production: ## 프로덕션 환경에 배포
	@echo "$(GREEN)🚀 프로덕션 환경에 배포 중...$(NC)"
	@echo "$(RED)⚠️  프로덕션 배포는 신중하게 진행해주세요!$(NC)"
	# 여기에 프로덕션 배포 로직 추가
	@echo "$(GREEN)✅ 프로덕션 배포 완료!$(NC)"

# 모니터링
health-check: ## 서비스 상태 확인
	@echo "$(GREEN)🏥 서비스 상태를 확인하고 있습니다...$(NC)"
	curl -f http://localhost:$(PORT)/health || echo "$(RED)❌ 서비스가 응답하지 않습니다.$(NC)"

logs: ## 애플리케이션 로그 확인
	@echo "$(GREEN)📋 애플리케이션 로그:$(NC)"
	tail -f logs/app.log 2>/dev/null || echo "$(YELLOW)로그 파일이 없습니다.$(NC)"

# 개발 도구
shell: ## Python 쉘 실행
	@echo "$(GREEN)🐍 Python 쉘을 시작합니다...$(NC)"
	$(PYTHON) -i -c "from app import app; from utils import *"

# 전체 파이프라인
ci: check test ## CI 파이프라인 실행
	@echo "$(GREEN)✅ CI 파이프라인이 완료되었습니다!$(NC)"

all: clean install ci docker-build ## 전체 빌드 파이프라인 실행
	@echo "$(GREEN)🎉 전체 빌드 파이프라인이 완료되었습니다!$(NC)"

# 설정 확인
check-env: ## 환경 설정 확인
	@echo "$(GREEN)⚙️  환경 설정을 확인하고 있습니다...$(NC)"
	@echo "Python 버전: $$($(PYTHON) --version)"
	@echo "Pip 버전: $$($(PIP) --version)"
	@if [ -f .env ]; then \
		echo "$(GREEN)✅ .env 파일이 존재합니다.$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  .env 파일이 없습니다. .env.example을 참고하여 생성하세요.$(NC)"; \
	fi
	@if [ -d venv ]; then \
		echo "$(GREEN)✅ 가상환경이 존재합니다.$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  가상환경이 없습니다.$(NC)"; \
	fi

# 초기 설정
init: ## 프로젝트 초기 설정
	@echo "$(GREEN)🚀 프로젝트를 초기 설정하고 있습니다...$(NC)"
	@if [ ! -d venv ]; then \
		echo "$(GREEN)📦 가상환경을 생성합니다...$(NC)"; \
		$(PYTHON) -m venv venv; \
	fi
	@if [ ! -f .env ]; then \
		echo "$(GREEN)📝 .env 파일을 생성합니다...$(NC)"; \
		cp .env.example .env; \
		echo "$(YELLOW)⚠️  .env 파일을 편집하여 실제 API 키를 설정하세요.$(NC)"; \
	fi
	@echo "$(GREEN)📁 필요한 디렉토리를 생성합니다...$(NC)"
	mkdir -p logs memory_data backups static/videos static/images
	@echo "$(GREEN)✅ 초기 설정이 완료되었습니다!$(NC)"
	@echo ""
	@echo "$(BLUE)다음 단계:$(NC)"
	@echo "1. 가상환경 활성화: source venv/bin/activate (Linux/Mac) 또는 venv\\Scripts\\activate (Windows)"
	@echo "2. 의존성 설치: make dev-install"
	@echo "3. .env 파일에서 API 키 설정"
	@echo "4. 개발 서버 실행: make run"
