# 기여하기 (Contributing)

회상치료 AI 아바타 - 감정비서 프로젝트에 관심을 가져주셔서 감사합니다! 💝

이 문서는 프로젝트에 기여하는 방법을 안내합니다. 모든 기여를 환영하며, 다음 가이드라인을 따라주시면 됩니다.

## 🤝 기여 방법

### 1. 이슈 보고하기

버그를 발견하거나 새로운 기능을 제안하고 싶으시다면:

1. **기존 이슈 확인**: 동일한 이슈가 이미 보고되었는지 확인해주세요.
2. **새 이슈 생성**: [Issues](https://github.com/your-org/avatar-emotion-assistant/issues) 페이지에서 새 이슈를 생성합니다.
3. **상세한 정보 제공**: 아래 템플릿을 참고하여 상세한 정보를 제공해주세요.

#### 버그 리포트 템플릿

```markdown
## 버그 설명
간단하고 명확한 버그 설명

## 재현 단계
1. '...' 페이지로 이동
2. '...' 버튼 클릭
3. '...' 입력
4. 오류 발생

## 예상 동작
무엇이 일어날 것으로 예상했는지 설명

## 실제 동작
실제로 무엇이 일어났는지 설명

## 스크린샷
가능하다면 스크린샷 첨부

## 환경 정보
- OS: [예: Windows 10]
- 브라우저: [예: Chrome 91.0]
- Python 버전: [예: 3.9.0]
- 프로젝트 버전: [예: 1.0.0]

## 추가 정보
다른 관련 정보나 컨텍스트
```

#### 기능 요청 템플릿

```markdown
## 기능 요청 배경
이 기능이 필요한 이유를 설명

## 원하는 해결책
어떤 기능을 원하는지 명확하고 간결하게 설명

## 대안 고려사항
고려해본 대안이나 해결 방법들

## 추가 컨텍스트
이 기능 요청에 대한 추가 컨텍스트나 스크린샷
```

### 2. 코드 기여하기

#### 개발 환경 설정

1. **저장소 포크**: GitHub에서 저장소를 포크합니다.

2. **로컬에 클론**:
   ```bash
   git clone https://github.com/your-username/avatar-emotion-assistant.git
   cd avatar-emotion-assistant
   ```

3. **개발 환경 설정**:
   ```bash
   make init          # 프로젝트 초기 설정
   make dev-install   # 개발 의존성 설치
   ```

4. **환경 변수 설정**:
   ```bash
   cp .env.example .env
   # .env 파일을 편집하여 필요한 API 키 설정
   ```

#### 개발 워크플로우

1. **새 브랜치 생성**:
   ```bash
   git checkout -b feature/새로운-기능-이름
   ```

2. **코드 작성**: 변경사항을 구현합니다.

3. **코드 품질 검사**:
   ```bash
   make format     # 코드 포매팅
   make lint       # 린팅 검사
   make security   # 보안 검사
   ```

4. **테스트 실행**:
   ```bash
   make test       # 모든 테스트 실행
   make test-coverage  # 커버리지와 함께 테스트
   ```

5. **커밋**: 의미 있는 커밋 메시지로 변경사항을 커밋합니다.
   ```bash
   git commit -m "feat: 새로운 회상치료 주제 추가"
   ```

6. **푸시 및 풀 리퀘스트**:
   ```bash
   git push origin feature/새로운-기능-이름
   ```
   GitHub에서 Pull Request를 생성합니다.

## 📝 코딩 가이드라인

### Python 코드 스타일

- **PEP 8** 준수
- **Black** 포매터 사용 (줄 길이: 100자)
- **Type Hints** 사용 권장
- **Docstrings** 작성 (Google 스타일)

```python
def extract_memory_keywords(text: str) -> Dict[str, List[str]]:
    """텍스트에서 회상치료 관련 키워드를 추출합니다.
    
    Args:
        text: 분석할 텍스트
        
    Returns:
        카테고리별로 분류된 키워드 딕셔너리
        
    Example:
        >>> extract_memory_keywords("어릴 때 고향에서 살았어요")
        {'시간대': ['어릴때'], '장소': ['고향']}
    """
    # 구현 코드
```

### JavaScript 코드 스타일

- **ES6+** 문법 사용
- **camelCase** 변수명
- **JSDoc** 주석 작성
- **Vanilla JavaScript** 사용 (라이브러리 최소화)

```javascript
/**
 * 사용자 입력을 안전하게 정리합니다.
 * @param {string} text - 정리할 텍스트
 * @returns {string} 정리된 텍스트
 */
function sanitizeUserInput(text) {
    // 구현 코드
}
```

### CSS 스타일

- **BEM** 방법론 사용
- **모바일 우선** 반응형 디자인
- **CSS Grid/Flexbox** 활용
- **CSS 변수** 사용

```css
/* BEM 예시 */
.avatar-container__video--speaking {
    transform: scale(1.02);
}

/* CSS 변수 예시 */
:root {
    --primary-color: #ff6b9d;
    --secondary-color: #ffa8cc;
}
```

## 🧪 테스트 가이드라인

### 테스트 작성

- **모든 새 기능**에 대해 테스트 작성
- **버그 수정** 시 회귀 테스트 추가
- **테스트 커버리지** 80% 이상 유지

### 테스트 구조

```python
class TestMemoryManager:
    """메모리 관리자 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        # 설정 코드
    
    def test_save_conversation_success(self):
        """대화 저장 성공 테스트"""
        # Given
        # When
        # Then
```

### 테스트 실행

```bash
# 모든 테스트
make test

# 특정 테스트만
make test-unit
make test-integration
make test-security

# 커버리지와 함께
make test-coverage
```

## 🔒 보안 가이드라인

### 보안 원칙

1. **입력 검증**: 모든 사용자 입력을 검증하고 정리
2. **출력 이스케이프**: XSS 방지를 위한 출력 이스케이프
3. **인증/인가**: 적절한 접근 제어
4. **HTTPS**: 프로덕션에서 HTTPS 사용
5. **비밀 정보**: 환경 변수나 안전한 저장소 사용

### 보안 검사

```bash
make security  # bandit + safety 실행
```

### 민감한 정보 처리

- **API 키**: 환경 변수로 관리
- **비밀번호**: 해싱 후 저장
- **로그**: 민감한 정보 로깅 금지

## 📚 문서화 가이드라인

### 코드 문서화

- **함수/클래스**: Docstring 필수
- **복잡한 로직**: 인라인 주석 추가
- **API**: 상세한 파라미터와 반환값 설명

### README 업데이트

새로운 기능이나 변경사항이 있으면 README.md를 업데이트해주세요:

- 설치 방법
- 사용법
- 예시 코드
- FAQ

## 🌍 다국어 지원

현재는 한국어를 주로 지원하지만, 다국어 지원 기여를 환영합니다:

- **메시지**: 다국어 메시지 파일 추가
- **문서**: 영어 문서 번역
- **UI**: 다국어 UI 지원

## 🎯 회상치료 전문성

이 프로젝트의 핵심인 회상치료 관련 기여 시 고려사항:

### 회상치료 원칙

1. **비강제적 접근**: 기억을 강요하지 않음
2. **긍정적 강화**: 좋은 기억에 대한 적극적 지지
3. **감정 존중**: 어르신의 감정을 존중
4. **개인화**: 개인별 맞춤형 접근

### 콘텐츠 추가

새로운 회상치료 콘텐츠 추가 시:

```python
# utils/content_recommender.py에 추가
'새로운주제': {
    'title': '주제 제목',
    'description': '주제 설명',
    'keywords': ['관련', '키워드'],
    'emotions': ['관련감정'],
    'questions': [
        '관련 질문 1',
        '관련 질문 2'
    ]
}
```

## 📋 Pull Request 가이드라인

### PR 제출 전 체크리스트

- [ ] 코드 품질 검사 통과 (`make check`)
- [ ] 모든 테스트 통과 (`make test`)
- [ ] 적절한 테스트 추가
- [ ] 문서 업데이트 (필요시)
- [ ] CHANGELOG.md 업데이트

### PR 템플릿

```markdown
## 변경사항 요약
이 PR에서 변경한 내용을 간략히 설명

## 변경 유형
- [ ] 버그 수정
- [ ] 새로운 기능
- [ ] 문서 업데이트
- [ ] 리팩토링
- [ ] 성능 개선
- [ ] 기타

## 테스트
- [ ] 새로운 테스트 추가
- [ ] 기존 테스트 수정
- [ ] 모든 테스트 통과

## 체크리스트
- [ ] 코드 스타일 검사 통과
- [ ] 보안 검사 통과
- [ ] 문서 업데이트 완료
- [ ] CHANGELOG.md 업데이트

## 스크린샷 (UI 변경시)
변경된 UI의 스크린샷 첨부

## 추가 정보
기타 리뷰어가 알아야 할 정보
```

## 🏷️ 커밋 메시지 규칙

### 커밋 메시지 형식

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### 타입

- **feat**: 새로운 기능
- **fix**: 버그 수정
- **docs**: 문서 변경
- **style**: 코드 포매팅
- **refactor**: 리팩토링
- **test**: 테스트 추가/수정
- **chore**: 빌드 프로세스, 도구 변경

### 예시

```bash
feat(memory): 사용자 선호도 분석 기능 추가

회상치료 효과 개선을 위해 사용자의 대화 패턴을 분석하여
개인화된 콘텐츠 추천이 가능하도록 구현

Closes #123
```

## 🎉 기여자 인정

모든 기여자는 다음과 같이 인정받습니다:

1. **README.md** 기여자 섹션에 추가
2. **CHANGELOG.md**에 기여 내용 기록
3. **GitHub Contributors** 그래프에 자동 표시

## ❓ 질문이나 도움이 필요한 경우

- **이슈**: [GitHub Issues](https://github.com/your-org/avatar-emotion-assistant/issues)에 질문 이슈 생성
- **토론**: [GitHub Discussions](https://github.com/your-org/avatar-emotion-assistant/discussions) 활용
- **이메일**: [team@avatar.local](mailto:team@avatar.local)

## 📋 행동 강령

모든 기여자는 다음 원칙을 준수해야 합니다:

1. **존중**: 모든 참여자를 존중합니다
2. **포용**: 다양성을 인정하고 환영합니다
3. **협력**: 건설적인 피드백을 제공합니다
4. **전문성**: 전문적이고 예의 바른 소통을 합니다
5. **목적 집중**: 회상치료 개선이라는 공통 목표에 집중합니다

---

**다시 한번 기여에 관심을 가져주셔서 감사합니다! 함께 더 나은 회상치료 AI를 만들어가요.** 🌟
