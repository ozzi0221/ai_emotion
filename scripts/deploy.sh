#!/bin/bash
# 회상치료 AI 아바타 배포 스크립트

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 설정
ENVIRONMENT="${ENVIRONMENT:-development}"
DOCKER_IMAGE="${DOCKER_IMAGE:-avatar-emotion-assistant}"
DOCKER_TAG="${DOCKER_TAG:-latest}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"

# 함수 정의
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# 도움말 표시
show_help() {
    echo "회상치료 AI 아바타 배포 스크립트"
    echo ""
    echo "사용법: $0 [옵션] [command]"
    echo ""
    echo "Commands:"
    echo "  build                   Docker 이미지 빌드"
    echo "  deploy                  서비스 배포"
    echo "  restart                 서비스 재시작"
    echo "  stop                    서비스 중지"
    echo "  status                  서비스 상태 확인"
    echo "  logs                    서비스 로그 확인"
    echo "  cleanup                 이전 버전 정리"
    echo "  health                  헬스 체크"
    echo "  rollback                이전 버전으로 롤백"
    echo ""
    echo "옵션:"
    echo "  -h, --help              이 도움말 표시"
    echo "  -e, --env ENV           환경 설정 (development/staging/production)"
    echo "  -t, --tag TAG           Docker 이미지 태그"
    echo "  -f, --file FILE         Docker Compose 파일"
    echo "  --dry-run               실제 배포 없이 테스트 실행"
    echo "  --no-backup             배포 전 백업 건너뛰기"
    echo "  --force                 확인 없이 강제 실행"
    echo ""
    echo "예시:"
    echo "  $0 build                이미지 빌드"
    echo "  $0 deploy               개발 환경 배포"
    echo "  $0 -e production deploy 프로덕션 배포"
    echo "  $0 --dry-run deploy     배포 테스트"
}

# 매개변수 파싱
COMMAND=""
DRY_RUN=false
NO_BACKUP=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -t|--tag)
            DOCKER_TAG="$2"
            shift 2
            ;;
        -f|--file)
            COMPOSE_FILE="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --no-backup)
            NO_BACKUP=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        build|deploy|restart|stop|status|logs|cleanup|health|rollback)
            COMMAND="$1"
            shift
            ;;
        *)
            error "알 수 없는 옵션: $1"
            ;;
    esac
done

# 환경별 설정
setup_environment() {
    case $ENVIRONMENT in
        development)
            COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
            DOCKER_TAG="${DOCKER_TAG:-dev}"
            ;;
        staging)
            COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.staging.yml}"
            DOCKER_TAG="${DOCKER_TAG:-staging}"
            ;;
        production)
            COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
            DOCKER_TAG="${DOCKER_TAG:-latest}"
            ;;
        *)
            error "지원되지 않는 환경: $ENVIRONMENT"
            ;;
    esac
    
    info "환경: $ENVIRONMENT"
    info "Docker 태그: $DOCKER_TAG"
    info "Compose 파일: $COMPOSE_FILE"
}

# 사전 요구사항 확인
check_prerequisites() {
    log "사전 요구사항 확인 중..."
    
    # Docker 확인
    if ! command -v docker &> /dev/null; then
        error "Docker가 설치되지 않았습니다"
    fi
    
    # Docker Compose 확인
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose가 설치되지 않았습니다"
    fi
    
    # Compose 파일 확인
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        error "Compose 파일이 없습니다: $COMPOSE_FILE"
    fi
    
    # .env 파일 확인
    if [[ ! -f ".env" ]]; then
        warn ".env 파일이 없습니다. .env.example을 참고하여 생성하세요."
    fi
    
    log "사전 요구사항 확인 완료"
}

# Docker 이미지 빌드
build_image() {
    log "Docker 이미지 빌드 시작..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: Docker 이미지 빌드 시뮬레이션"
        log "  이미지: $DOCKER_IMAGE:$DOCKER_TAG"
        return
    fi
    
    # 빌드 시작 시간 기록
    local start_time=$(date +%s)
    
    # Docker 이미지 빌드
    if docker build -t "$DOCKER_IMAGE:$DOCKER_TAG" .; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        log "Docker 이미지 빌드 완료 (${duration}초): $DOCKER_IMAGE:$DOCKER_TAG"
    else
        error "Docker 이미지 빌드 실패"
    fi
    
    # 이미지 크기 확인
    local image_size=$(docker images "$DOCKER_IMAGE:$DOCKER_TAG" --format "table {{.Size}}" | tail -n 1)
    info "이미지 크기: $image_size"
}

# 서비스 배포
deploy_service() {
    log "서비스 배포 시작 ($ENVIRONMENT 환경)..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: 서비스 배포 시뮬레이션"
        return
    fi
    
    # 프로덕션 환경 확인
    if [[ "$ENVIRONMENT" == "production" && "$FORCE" != "true" ]]; then
        warn "프로덕션 환경에 배포하려고 합니다!"
        echo -n "계속하시겠습니까? [y/N]: "
        read -r response
        
        case $response in
            [yY]|[yY][eE][sS])
                log "프로덕션 배포를 계속합니다..."
                ;;
            *)
                log "배포가 취소되었습니다"
                exit 0
                ;;
        esac
    fi
    
    # 백업 실행 (요청된 경우)
    if [[ "$NO_BACKUP" != "true" ]]; then
        backup_before_deploy
    fi
    
    # Docker Compose로 서비스 시작
    log "Docker Compose 서비스 시작..."
    
    # 환경 변수 설정
    export DOCKER_TAG
    export ENVIRONMENT
    
    if docker-compose -f "$COMPOSE_FILE" up -d; then
        log "서비스 배포 완료"
    else
        error "서비스 배포 실패"
    fi
    
    # 서비스 시작 대기
    wait_for_services
    
    # 헬스 체크
    perform_health_check
}

# 배포 전 백업
backup_before_deploy() {
    log "배포 전 백업 실행..."
    
    if [[ -f "scripts/backup.sh" ]]; then
        if bash scripts/backup.sh; then
            log "배포 전 백업 완료"
        else
            warn "배포 전 백업 실패"
        fi
    else
        warn "백업 스크립트를 찾을 수 없습니다"
    fi
}

# 서비스 시작 대기
wait_for_services() {
    log "서비스 시작 대기 중..."
    
    local max_attempts=30
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if check_service_health; then
            log "서비스가 정상적으로 시작되었습니다"
            return 0
        fi
        
        ((attempt++))
        info "대기 중... ($attempt/$max_attempts)"
        sleep 10
    done
    
    error "서비스 시작 타임아웃"
}

# 서비스 상태 확인
check_service_health() {
    local health_url="http://localhost:5000/health"
    
    if curl -sf "$health_url" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# 헬스 체크 수행
perform_health_check() {
    log "헬스 체크 수행 중..."
    
    local health_url="http://localhost:5000/health"
    
    if curl -sf "$health_url" | jq . 2>/dev/null; then
        log "헬스 체크 성공"
    else
        warn "헬스 체크 실패 또는 jq 미설치"
        
        # 기본 HTTP 응답 확인
        if curl -sf "$health_url" >/dev/null 2>&1; then
            log "서비스가 응답하고 있습니다"
        else
            error "서비스가 응답하지 않습니다"
        fi
    fi
}

# 서비스 재시작
restart_service() {
    log "서비스 재시작 중..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: 서비스 재시작 시뮬레이션"
        return
    fi
    
    if docker-compose -f "$COMPOSE_FILE" restart; then
        log "서비스 재시작 완료"
        wait_for_services
    else
        error "서비스 재시작 실패"
    fi
}

# 서비스 중지
stop_service() {
    log "서비스 중지 중..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: 서비스 중지 시뮬레이션"
        return
    fi
    
    if docker-compose -f "$COMPOSE_FILE" down; then
        log "서비스 중지 완료"
    else
        error "서비스 중지 실패"
    fi
}

# 서비스 상태 확인
check_status() {
    log "서비스 상태 확인 중..."
    
    # Docker Compose 상태
    docker-compose -f "$COMPOSE_FILE" ps
    
    # 개별 컨테이너 상태
    echo ""
    info "컨테이너 리소스 사용량:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

# 서비스 로그 확인
show_logs() {
    log "서비스 로그 확인..."
    
    local service="${1:-avatar-app}"
    local lines="${2:-100}"
    
    docker-compose -f "$COMPOSE_FILE" logs --tail="$lines" -f "$service"
}

# 이전 버전 정리
cleanup_old_versions() {
    log "이전 버전 정리 중..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: 이전 버전 정리 시뮬레이션"
        return
    fi
    
    # 사용하지 않는 Docker 이미지 정리
    docker image prune -f
    
    # 사용하지 않는 볼륨 정리
    docker volume prune -f
    
    # 사용하지 않는 네트워크 정리
    docker network prune -f
    
    log "정리 완료"
}

# 롤백 수행
perform_rollback() {
    log "이전 버전으로 롤백 중..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: 롤백 시뮬레이션"
        return
    fi
    
    # 이전 백업에서 복원
    if [[ -f "scripts/restore.sh" ]]; then
        if bash scripts/restore.sh --force; then
            log "데이터 롤백 완료"
        else
            error "데이터 롤백 실패"
        fi
    fi
    
    # 서비스 재시작
    restart_service
    
    log "롤백 완료"
}

# 메인 실행
main() {
    log "회상치료 AI 아바타 배포 스크립트 시작"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        warn "DRY RUN 모드: 실제 변경사항 없음"
    fi
    
    # 환경 설정
    setup_environment
    
    # 사전 요구사항 확인
    check_prerequisites
    
    # 명령어 실행
    case $COMMAND in
        build)
            build_image
            ;;
        deploy)
            build_image
            deploy_service
            ;;
        restart)
            restart_service
            ;;
        stop)
            stop_service
            ;;
        status)
            check_status
            ;;
        logs)
            show_logs "$2" "$3"
            ;;
        cleanup)
            cleanup_old_versions
            ;;
        health)
            perform_health_check
            ;;
        rollback)
            perform_rollback
            ;;
        "")
            error "명령어를 지정해주세요. --help로 도움말을 확인하세요."
            ;;
        *)
            error "알 수 없는 명령어: $COMMAND"
            ;;
    esac
    
    log "작업 완료!"
}

# 스크립트 실행
main "$@"
