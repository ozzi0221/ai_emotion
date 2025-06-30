#!/bin/bash
# 회상치료 AI 아바타 데이터 백업 스크립트

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 설정
BACKUP_DIR="${BACKUP_DIR:-./backups}"
DATA_DIR="${DATA_DIR:-./memory_data}"
LOGS_DIR="${LOGS_DIR:-./logs}"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="avatar_backup_${DATE}"
KEEP_DAYS="${KEEP_DAYS:-30}"

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

# 도움말 표시
show_help() {
    echo "회상치료 AI 아바타 백업 스크립트"
    echo ""
    echo "사용법: $0 [옵션]"
    echo ""
    echo "옵션:"
    echo "  -h, --help              이 도움말 표시"
    echo "  -d, --data-dir DIR      데이터 디렉토리 (기본: ./memory_data)"
    echo "  -l, --logs-dir DIR      로그 디렉토리 (기본: ./logs)"
    echo "  -o, --output-dir DIR    백업 저장 디렉토리 (기본: ./backups)"
    echo "  -k, --keep-days DAYS    보관할 백업 일수 (기본: 30)"
    echo "  -c, --compress          압축 수준 설정 (1-9, 기본: 6)"
    echo "  --dry-run              실제 백업 없이 테스트 실행"
    echo ""
    echo "예시:"
    echo "  $0                      기본 설정으로 백업"
    echo "  $0 -k 60               60일간 백업 보관"
    echo "  $0 --dry-run           테스트 실행"
}

# 매개변수 파싱
DRY_RUN=false
COMPRESS_LEVEL=6

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -d|--data-dir)
            DATA_DIR="$2"
            shift 2
            ;;
        -l|--logs-dir)
            LOGS_DIR="$2"
            shift 2
            ;;
        -o|--output-dir)
            BACKUP_DIR="$2"
            shift 2
            ;;
        -k|--keep-days)
            KEEP_DAYS="$2"
            shift 2
            ;;
        -c|--compress)
            COMPRESS_LEVEL="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            error "알 수 없는 옵션: $1"
            ;;
    esac
done

# 백업 디렉토리 생성
create_backup_dir() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: 백업 디렉토리 생성 확인: $BACKUP_DIR"
        return
    fi
    
    if [[ ! -d "$BACKUP_DIR" ]]; then
        mkdir -p "$BACKUP_DIR"
        log "백업 디렉토리 생성: $BACKUP_DIR"
    fi
}

# 디스크 공간 확인
check_disk_space() {
    log "디스크 공간 확인 중..."
    
    # 필요한 공간 계산 (데이터 + 로그 디렉토리 크기)
    local required_space=0
    
    if [[ -d "$DATA_DIR" ]]; then
        local data_size=$(du -sb "$DATA_DIR" 2>/dev/null | cut -f1)
        required_space=$((required_space + data_size))
    fi
    
    if [[ -d "$LOGS_DIR" ]]; then
        local logs_size=$(du -sb "$LOGS_DIR" 2>/dev/null | cut -f1)
        required_space=$((required_space + logs_size))
    fi
    
    # 압축을 고려하여 50% 여유 공간
    required_space=$((required_space * 3 / 2))
    
    # 사용 가능한 공간 확인
    local available_space=$(df "$BACKUP_DIR" | awk 'NR==2 {print $4*1024}')
    
    if [[ $required_space -gt $available_space ]]; then
        error "디스크 공간 부족: 필요 $(($required_space/1024/1024))MB, 사용가능 $(($available_space/1024/1024))MB"
    fi
    
    log "디스크 공간 확인 완료: $(($available_space/1024/1024))MB 사용 가능"
}

# 백업 실행
perform_backup() {
    local backup_file="$BACKUP_DIR/${BACKUP_NAME}.tar.gz"
    
    log "백업 시작: $backup_file"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: 백업 파일 생성 시뮬레이션"
        log "  - 데이터 디렉토리: $DATA_DIR"
        log "  - 로그 디렉토리: $LOGS_DIR"
        log "  - 백업 파일: $backup_file"
        return
    fi
    
    # tar 명령어 구성
    local tar_cmd="tar -czf"
    local tar_files=""
    
    # 압축 수준 설정
    export GZIP="-$COMPRESS_LEVEL"
    
    # 백업할 디렉토리 확인 및 추가
    if [[ -d "$DATA_DIR" ]]; then
        tar_files="$tar_files $DATA_DIR"
        log "데이터 디렉토리 추가: $DATA_DIR"
    else
        warn "데이터 디렉토리가 존재하지 않습니다: $DATA_DIR"
    fi
    
    if [[ -d "$LOGS_DIR" ]]; then
        tar_files="$tar_files $LOGS_DIR"
        log "로그 디렉토리 추가: $LOGS_DIR"
    else
        warn "로그 디렉토리가 존재하지 않습니다: $LOGS_DIR"
    fi
    
    # 설정 파일들도 백업에 포함
    local config_files=".env docker-compose.yml"
    for file in $config_files; do
        if [[ -f "$file" ]]; then
            tar_files="$tar_files $file"
            log "설정 파일 추가: $file"
        fi
    done
    
    if [[ -z "$tar_files" ]]; then
        error "백업할 파일이 없습니다."
    fi
    
    # 백업 실행
    if $tar_cmd "$backup_file" $tar_files; then
        local backup_size=$(du -h "$backup_file" | cut -f1)
        log "백업 완료: $backup_file ($backup_size)"
    else
        error "백업 실패"
    fi
}

# 메타데이터 생성
create_metadata() {
    local metadata_file="$BACKUP_DIR/${BACKUP_NAME}.json"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: 메타데이터 파일 생성 시뮬레이션: $metadata_file"
        return
    fi
    
    log "메타데이터 생성: $metadata_file"
    
    cat > "$metadata_file" << EOF
{
  "backup_name": "$BACKUP_NAME",
  "timestamp": "$(date -Iseconds)",
  "hostname": "$(hostname)",
  "user": "$(whoami)",
  "data_directory": "$DATA_DIR",
  "logs_directory": "$LOGS_DIR",
  "backup_file": "${BACKUP_NAME}.tar.gz",
  "file_size": "$(du -b "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" 2>/dev/null | cut -f1)",
  "compress_level": $COMPRESS_LEVEL,
  "version": "1.0.0"
}
EOF
}

# 오래된 백업 정리
cleanup_old_backups() {
    log "오래된 백업 정리 중... (${KEEP_DAYS}일 이전)"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        local old_files=$(find "$BACKUP_DIR" -name "avatar_backup_*.tar.gz" -mtime +$KEEP_DAYS 2>/dev/null || true)
        if [[ -n "$old_files" ]]; then
            log "DRY RUN: 삭제될 파일들:"
            echo "$old_files" | while read -r file; do
                log "  - $file"
            done
        else
            log "DRY RUN: 삭제할 오래된 백업이 없습니다."
        fi
        return
    fi
    
    local deleted_count=0
    
    # tar.gz 파일들 정리
    while IFS= read -r -d '' file; do
        rm -f "$file"
        # 해당 메타데이터 파일도 삭제
        local metadata_file="${file%.tar.gz}.json"
        [[ -f "$metadata_file" ]] && rm -f "$metadata_file"
        
        log "삭제됨: $(basename "$file")"
        ((deleted_count++))
    done < <(find "$BACKUP_DIR" -name "avatar_backup_*.tar.gz" -mtime +$KEEP_DAYS -print0 2>/dev/null || true)
    
    if [[ $deleted_count -gt 0 ]]; then
        log "$deleted_count개의 오래된 백업을 삭제했습니다."
    else
        log "삭제할 오래된 백업이 없습니다."
    fi
}

# 백업 검증
verify_backup() {
    local backup_file="$BACKUP_DIR/${BACKUP_NAME}.tar.gz"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: 백업 파일 검증 시뮬레이션"
        return
    fi
    
    log "백업 파일 검증 중..."
    
    if [[ ! -f "$backup_file" ]]; then
        error "백업 파일이 존재하지 않습니다: $backup_file"
    fi
    
    # tar 파일 무결성 검사
    if tar -tzf "$backup_file" >/dev/null 2>&1; then
        log "백업 파일 검증 완료: 무결성 양호"
    else
        error "백업 파일이 손상되었습니다: $backup_file"
    fi
}

# 백업 목록 표시
list_backups() {
    log "기존 백업 목록:"
    
    if [[ ! -d "$BACKUP_DIR" ]]; then
        log "백업 디렉토리가 없습니다: $BACKUP_DIR"
        return
    fi
    
    local backup_files=$(find "$BACKUP_DIR" -name "avatar_backup_*.tar.gz" | sort -r)
    
    if [[ -z "$backup_files" ]]; then
        log "백업 파일이 없습니다."
        return
    fi
    
    echo "$backup_files" | while read -r file; do
        local size=$(du -h "$file" | cut -f1)
        local date=$(stat -c %y "$file" | cut -d' ' -f1)
        log "  - $(basename "$file") ($size, $date)"
    done
}

# 메인 실행
main() {
    log "회상치료 AI 아바타 백업 스크립트 시작"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        warn "DRY RUN 모드: 실제 변경사항 없음"
    fi
    
    # 백업 전 목록 표시
    list_backups
    
    # 백업 실행
    create_backup_dir
    check_disk_space
    perform_backup
    create_metadata
    verify_backup
    cleanup_old_backups
    
    log "백업 완료!"
    
    # 백업 후 목록 표시
    list_backups
}

# 스크립트 실행
main "$@"
