#!/bin/bash
# 회상치료 AI 아바타 데이터 복원 스크립트

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 설정
BACKUP_DIR="${BACKUP_DIR:-./backups}"
RESTORE_DIR="${RESTORE_DIR:-.}"

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
    echo "회상치료 AI 아바타 복원 스크립트"
    echo ""
    echo "사용법: $0 [옵션] [백업파일]"
    echo ""
    echo "옵션:"
    echo "  -h, --help              이 도움말 표시"
    echo "  -b, --backup-dir DIR    백업 디렉토리 (기본: ./backups)"
    echo "  -r, --restore-dir DIR   복원 대상 디렉토리 (기본: .)"
    echo "  -l, --list              사용 가능한 백업 목록 표시"
    echo "  -i, --info FILE         백업 파일 정보 표시"
    echo "  -f, --force             기존 데이터 덮어쓰기 (확인 없이)"
    echo "  --dry-run              실제 복원 없이 테스트 실행"
    echo "  --verify-only          백업 파일 검증만 수행"
    echo ""
    echo "인수:"
    echo "  백업파일               복원할 백업 파일명 (없으면 최신 백업 사용)"
    echo ""
    echo "예시:"
    echo "  $0                      최신 백업으로 복원"
    echo "  $0 -l                   백업 목록 표시"
    echo "  $0 backup_20241229.tar.gz  특정 백업으로 복원"
    echo "  $0 --dry-run            테스트 실행"
}

# 매개변수 파싱
BACKUP_FILE=""
LIST_ONLY=false
SHOW_INFO=false
FORCE=false
DRY_RUN=false
VERIFY_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -b|--backup-dir)
            BACKUP_DIR="$2"
            shift 2
            ;;
        -r|--restore-dir)
            RESTORE_DIR="$2"
            shift 2
            ;;
        -l|--list)
            LIST_ONLY=true
            shift
            ;;
        -i|--info)
            SHOW_INFO=true
            BACKUP_FILE="$2"
            shift 2
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --verify-only)
            VERIFY_ONLY=true
            shift
            ;;
        -*)
            error "알 수 없는 옵션: $1"
            ;;
        *)
            BACKUP_FILE="$1"
            shift
            ;;
    esac
done

# 백업 목록 표시
list_backups() {
    log "사용 가능한 백업 목록:"
    
    if [[ ! -d "$BACKUP_DIR" ]]; then
        error "백업 디렉토리가 없습니다: $BACKUP_DIR"
    fi
    
    local backup_files=$(find "$BACKUP_DIR" -name "avatar_backup_*.tar.gz" | sort -r)
    
    if [[ -z "$backup_files" ]]; then
        log "백업 파일이 없습니다."
        return 1
    fi
    
    local count=0
    echo "$backup_files" | while read -r file; do
        count=$((count + 1))
        local basename=$(basename "$file")
        local size=$(du -h "$file" | cut -f1)
        local date=$(stat -c %y "$file" | cut -d' ' -f1,2 | cut -d'.' -f1)
        
        # 메타데이터 파일 확인
        local metadata_file="${file%.tar.gz}.json"
        local metadata_info=""
        if [[ -f "$metadata_file" ]]; then
            metadata_info=" ✓"
        else
            metadata_info=" ✗"
        fi
        
        log "  $count. $basename ($size, $date)$metadata_info"
    done
    
    return 0
}

# 백업 정보 표시
show_backup_info() {
    local backup_path="$1"
    
    log "백업 파일 정보: $(basename "$backup_path")"
    
    # 파일 존재 확인
    if [[ ! -f "$backup_path" ]]; then
        error "백업 파일이 존재하지 않습니다: $backup_path"
    fi
    
    # 기본 정보
    local size=$(du -h "$backup_path" | cut -f1)
    local date=$(stat -c %y "$backup_path" | cut -d'.' -f1)
    log "  파일 크기: $size"
    log "  생성 날짜: $date"
    
    # 메타데이터 정보
    local metadata_file="${backup_path%.tar.gz}.json"
    if [[ -f "$metadata_file" ]]; then
        log "  메타데이터: 있음"
        
        # JSON 파싱 (jq가 있는 경우)
        if command -v jq >/dev/null 2>&1; then
            local hostname=$(jq -r '.hostname // "unknown"' "$metadata_file")
            local user=$(jq -r '.user // "unknown"' "$metadata_file")
            local version=$(jq -r '.version // "unknown"' "$metadata_file")
            
            log "    호스트명: $hostname"
            log "    사용자: $user"
            log "    버전: $version"
        fi
    else
        warn "  메타데이터: 없음"
    fi
    
    # 백업 내용 확인
    log "  백업 내용:"
    if tar -tzf "$backup_path" | head -10 | while read -r item; do
        log "    - $item"
    done; then
        local total_files=$(tar -tzf "$backup_path" | wc -l)
        if [[ $total_files -gt 10 ]]; then
            log "    ... 총 $total_files개 항목"
        fi
    else
        error "백업 파일을 읽을 수 없습니다"
    fi
}

# 최신 백업 파일 찾기
find_latest_backup() {
    local latest=$(find "$BACKUP_DIR" -name "avatar_backup_*.tar.gz" -printf '%T@ %p\n' | sort -nr | head -1 | cut -d' ' -f2-)
    
    if [[ -z "$latest" ]]; then
        error "백업 파일을 찾을 수 없습니다"
    fi
    
    echo "$latest"
}

# 백업 파일 검증
verify_backup() {
    local backup_path="$1"
    
    log "백업 파일 검증 중: $(basename "$backup_path")"
    
    # 파일 존재 확인
    if [[ ! -f "$backup_path" ]]; then
        error "백업 파일이 존재하지 않습니다: $backup_path"
    fi
    
    # tar 파일 무결성 검사
    if tar -tzf "$backup_path" >/dev/null 2>&1; then
        log "백업 파일 검증 완료: 무결성 양호"
        return 0
    else
        error "백업 파일이 손상되었습니다: $backup_path"
    fi
}

# 기존 데이터 백업
backup_existing_data() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local temp_backup="$RESTORE_DIR/pre_restore_backup_$timestamp.tar.gz"
    
    log "기존 데이터 백업 중: $(basename "$temp_backup")"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: 기존 데이터 백업 시뮬레이션"
        return
    fi
    
    local backup_items=""
    
    # 백업할 항목들 확인
    for item in memory_data logs .env; do
        if [[ -e "$RESTORE_DIR/$item" ]]; then
            backup_items="$backup_items $item"
        fi
    done
    
    if [[ -n "$backup_items" ]]; then
        if tar -czf "$temp_backup" -C "$RESTORE_DIR" $backup_items 2>/dev/null; then
            log "기존 데이터 백업 완료: $(basename "$temp_backup")"
        else
            warn "기존 데이터 백업 실패"
        fi
    else
        log "백업할 기존 데이터가 없습니다"
    fi
}

# 복원 실행
perform_restore() {
    local backup_path="$1"
    
    log "복원 시작: $(basename "$backup_path")"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: 복원 시뮬레이션"
        log "  백업 파일: $backup_path"
        log "  복원 위치: $RESTORE_DIR"
        
        # 복원될 내용 표시
        log "  복원될 내용:"
        tar -tzf "$backup_path" | head -10 | while read -r item; do
            log "    - $item"
        done
        return
    fi
    
    # 복원 실행
    if tar -xzf "$backup_path" -C "$RESTORE_DIR"; then
        log "복원 완료"
    else
        error "복원 실패"
    fi
    
    # 권한 설정 (필요시)
    if [[ -d "$RESTORE_DIR/memory_data" ]]; then
        chmod -R 755 "$RESTORE_DIR/memory_data" 2>/dev/null || true
    fi
    
    if [[ -d "$RESTORE_DIR/logs" ]]; then
        chmod -R 755 "$RESTORE_DIR/logs" 2>/dev/null || true
    fi
}

# 복원 후 검증
verify_restore() {
    log "복원 후 검증 중..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: 복원 검증 시뮬레이션"
        return
    fi
    
    local errors=0
    
    # 필수 디렉토리 확인
    for dir in memory_data logs; do
        if [[ ! -d "$RESTORE_DIR/$dir" ]]; then
            warn "디렉토리가 없습니다: $dir"
            ((errors++))
        else
            log "디렉토리 확인됨: $dir"
        fi
    done
    
    # 설정 파일 확인
    if [[ -f "$RESTORE_DIR/.env" ]]; then
        log "설정 파일 확인됨: .env"
    else
        warn "설정 파일이 없습니다: .env"
    fi
    
    if [[ $errors -gt 0 ]]; then
        warn "복원 검증 중 $errors개의 경고가 발생했습니다"
    else
        log "복원 검증 완료: 모든 항목 정상"
    fi
}

# 확인 요청
confirm_restore() {
    if [[ "$FORCE" == "true" ]]; then
        return 0
    fi
    
    warn "복원 작업은 기존 데이터를 덮어씁니다!"
    warn "복원 위치: $RESTORE_DIR"
    
    echo -n "계속하시겠습니까? [y/N]: "
    read -r response
    
    case $response in
        [yY]|[yY][eE][sS])
            return 0
            ;;
        *)
            log "복원이 취소되었습니다"
            exit 0
            ;;
    esac
}

# 메인 실행
main() {
    log "회상치료 AI 아바타 복원 스크립트 시작"
    
    # 백업 디렉토리 확인
    if [[ ! -d "$BACKUP_DIR" ]]; then
        error "백업 디렉토리가 없습니다: $BACKUP_DIR"
    fi
    
    # 목록만 표시하고 종료
    if [[ "$LIST_ONLY" == "true" ]]; then
        list_backups
        exit 0
    fi
    
    # 백업 파일 결정
    if [[ -z "$BACKUP_FILE" ]]; then
        BACKUP_FILE=$(find_latest_backup)
        log "최신 백업 파일 사용: $(basename "$BACKUP_FILE")"
    else
        # 상대 경로인 경우 백업 디렉토리 추가
        if [[ ! "$BACKUP_FILE" =~ ^/ ]]; then
            BACKUP_FILE="$BACKUP_DIR/$BACKUP_FILE"
        fi
    fi
    
    # 백업 정보만 표시하고 종료
    if [[ "$SHOW_INFO" == "true" ]]; then
        show_backup_info "$BACKUP_FILE"
        exit 0
    fi
    
    # 백업 파일 검증
    verify_backup "$BACKUP_FILE"
    
    # 검증만 수행하고 종료
    if [[ "$VERIFY_ONLY" == "true" ]]; then
        log "백업 파일 검증 완료"
        exit 0
    fi
    
    # DRY RUN 모드 표시
    if [[ "$DRY_RUN" == "true" ]]; then
        warn "DRY RUN 모드: 실제 변경사항 없음"
    fi
    
    # 복원 확인
    if [[ "$DRY_RUN" != "true" ]]; then
        confirm_restore
    fi
    
    # 기존 데이터 백업
    if [[ "$DRY_RUN" != "true" ]]; then
        backup_existing_data
    fi
    
    # 복원 실행
    perform_restore "$BACKUP_FILE"
    
    # 복원 후 검증
    verify_restore
    
    log "복원 완료!"
    
    if [[ "$DRY_RUN" != "true" ]]; then
        log "서비스를 재시작하여 변경사항을 적용하세요."
    fi
}

# 스크립트 실행
main "$@"
