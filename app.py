import os
import json
import re
from flask import Flask, render_template, request, Response, jsonify
import google.generativeai as genai
from datetime import datetime
import time
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-this')

# CSP 헤더 설정을 위한 데코레이터
@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
        "font-src 'self' https://cdnjs.cloudflare.com; "
        "img-src 'self' data: https:; "
        "media-src 'self' data: blob:; "
        "connect-src 'self' https: wss: ws:;"
    )
    return response

# Google Gemini API 설정
API_KEY = os.getenv('GEMINI_API_KEY', 'your-gemini-api-key-here')
if API_KEY == 'your-gemini-api-key-here':
    print("⚠️  경고: GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
    print("   .env.example 파일을 참고하여 .env 파일을 생성하고 API 키를 설정하세요.")

genai.configure(api_key=API_KEY)

# 회상치료 AI 아바타 시스템 프롬프트 - 이모티콘 금지만 추가
SYSTEM_PROMPT = """당신은 고령자, 특히 치매 예방과 정서 케어를 위한 회상치료 AI 아바타입니다.

[중요한 응답 규칙]
- 절대로 이모티콘을 사용하지 마세요 (😊, 🎵, 💖 등 모든 이모티콘 금지)
- 순수한 한글 텍스트로만 응답하세요
- 감정 표현은 말로 표현하세요 (예: "기뻐요", "따뜻해요", "그리워요" 등)

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
- 검색어는 "유튜브에서 ~ 검색해줘" 형태로 변환하여 응답에 포함하세요.
- 예: 사용자가 "고향의 봄 들려줘"라고 하면  
→ "이 노래 들어보실래요. 유튜브에서 '고향의 봄 노래'를 검색해보세요."

[감정 기반 응답 가이드]
- 어르신의 반응이 긍정적이면 그 감정을 강화해주는 말을 해주세요.  
  예: "그때 정말 행복하셨겠어요.", "정말 소중한 기억이네요."
- 기억이 안 난다고 하면 절대 억지로 끌어내려 하지 말고 부드럽게 넘어가세요.  
  예: "괜찮아요. 생각이 안 나셔도 괜찮아요. 다음에 또 떠오를 수 있어요."

[응답 형식 가이드]
- 매 응답에는 회상 질문 + 감정 공감 표현 + (필요시) 유튜브 검색어 안내를 포함합니다.
- 예시:
  - "그 시절 집 앞 풍경이 떠오르시나요. 유튜브에서 '70년대 고향마을 사진'을 찾아보셔도 좋아요."
  - "이 노래 기억나세요. 유튜브에서 '정미조 개여울'을 검색해보세요."

항상 존댓말을 사용하고, 따뜻하고 친근한 톤으로 대화하세요. 어르신의 감정과 기억을 소중히 여기며, 절대 서두르지 말고 천천히 대화를 이어가세요. 다시 한번 강조하지만 이모티콘은 절대 사용하지 마세요."""

# 설정값들
CONFIG = {
    'MAX_HISTORY': int(os.getenv('MAX_CONVERSATION_HISTORY', 4)),
    'RESPONSE_MAX_SENTENCES': int(os.getenv('RESPONSE_MAX_SENTENCES', 3)),
    'STREAMING_DELAY': float(os.getenv('STREAMING_DELAY', 0.1)),
    'AVATAR_IDLE_VIDEO': os.getenv('AVATAR_IDLE_VIDEO', 'avatar_idle.mp4'),
    'AVATAR_SPEAKING_VIDEO': os.getenv('AVATAR_SPEAKING_VIDEO', 'avatar_speaking.mp4')
}

# Gemini 모델 초기화
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("✅ Google Gemini 모델이 성공적으로 초기화되었습니다.")
except Exception as e:
    print(f"❌ Gemini 모델 초기화 실패: {e}")
    model = None

# 대화 기록을 저장할 리스트
conversation_history = []

def extract_youtube_search(text):
    """응답에서 유튜브 검색어를 추출하는 함수"""
    patterns = [
        r"유튜브에서\s*['\"]([^'\"]+)['\"].*?검색",
        r"유튜브에서\s*['\"]([^'\"]+)['\"]",
        r"'([^']+)'\s*(?:을|를)?\s*검색",
        r"검색어:\s*['\"]([^'\"]+)['\"]"
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            return matches[0].strip()
    return None

def extract_memory_keywords(text):
    """대화에서 추억 관련 키워드를 추출하는 함수"""
    memory_keywords = {
        '음악': ['노래', '음악', '가요', '곡', '멜로디', '가사'],
        '장소': ['고향', '집', '마을', '학교', '시장', '교회'],
        '음식': ['음식', '요리', '반찬', '간식', '떡', '김치'],
        '가족': ['어머니', '아버지', '자식', '형제', '가족', '부모'],
        '시대': ['어릴때', '젊을때', '옛날', '그때', '시절']
    }
    
    found_keywords = {}
    for category, keywords in memory_keywords.items():
        for keyword in keywords:
            if keyword in text:
                if category not in found_keywords:
                    found_keywords[category] = []
                found_keywords[category].append(keyword)
    
    return found_keywords

def generate_streaming_response(prompt):
    """스트리밍 응답을 생성하는 함수 - 원래 버전 복원"""
    if not model:
        yield json.dumps({
            'type': 'error',
            'message': 'AI 모델이 초기화되지 않았습니다. API 키를 확인해주세요.'
        }, ensure_ascii=False) + '\n'
        return
    
    try:
        # 대화 히스토리 포함한 전체 컨텍스트 구성
        full_context = SYSTEM_PROMPT + "\n\n"
        
        # 최근 대화만 포함 (메모리 효율성)
        recent_history = conversation_history[-CONFIG['MAX_HISTORY']:]
        for msg in recent_history:
            full_context += f"사용자: {msg['user']}\n아바타: {msg['assistant']}\n\n"
        
        full_context += f"사용자: {prompt}\n아바타: "
        
        # Gemini API 호출
        response = model.generate_content(
            full_context, 
            stream=True,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=500,
                temperature=0.7,
                top_p=0.8,
                top_k=40
            )
        )
        
        full_response = ""
        sentence_buffer = ""
        sentence_count = 0
        
        for chunk in response:
            if chunk.text:
                full_response += chunk.text
                sentence_buffer += chunk.text
                
                # 문장 완성 체크 (. ! ? 로 끝나는 경우)
                if re.search(r'[.!?]\s*$', sentence_buffer.strip()):
                    sentence_count += 1
                    
                    # 최대 문장 수 제한
                    if sentence_count > CONFIG['RESPONSE_MAX_SENTENCES']:
                        break
                    
                    # 유튜브 검색어 추출
                    youtube_search = extract_youtube_search(sentence_buffer)
                    
                    # 추억 키워드 추출
                    memory_keywords = extract_memory_keywords(sentence_buffer)
                    
                    yield json.dumps({
                        'type': 'sentence',
                        'content': sentence_buffer.strip(),
                        'youtube_search': youtube_search,
                        'memory_keywords': memory_keywords,
                        'timestamp': datetime.now().isoformat()
                    }, ensure_ascii=False) + '\n'
                    
                    sentence_buffer = ""
                    time.sleep(CONFIG['STREAMING_DELAY'])  # 자연스러운 텀
        
        # 마지막 남은 텍스트 처리
        if sentence_buffer.strip():
            youtube_search = extract_youtube_search(sentence_buffer)
            memory_keywords = extract_memory_keywords(sentence_buffer)
            
            yield json.dumps({
                'type': 'sentence',
                'content': sentence_buffer.strip(),
                'youtube_search': youtube_search,
                'memory_keywords': memory_keywords,
                'timestamp': datetime.now().isoformat()
            }, ensure_ascii=False) + '\n'
        
        # 대화 기록 저장
        conversation_history.append({
            'user': prompt,
            'assistant': full_response.strip(),
            'timestamp': datetime.now().isoformat(),
            'memory_keywords': extract_memory_keywords(prompt + ' ' + full_response)
        })
        
        # 히스토리 크기 관리
        if len(conversation_history) > CONFIG['MAX_HISTORY'] * 2:
            conversation_history[:] = conversation_history[-CONFIG['MAX_HISTORY']:]
        
        # 완료 신호
        yield json.dumps({
            'type': 'complete',
            'full_response': full_response.strip(),
            'conversation_count': len(conversation_history)
        }, ensure_ascii=False) + '\n'
        
    except Exception as e:
        error_message = f'죄송합니다. 잠시 문제가 생겼네요. 다시 말씀해 주시겠어요? (오류: {str(e)})'
        yield json.dumps({
            'type': 'error',
            'message': error_message
        }, ensure_ascii=False) + '\n'

@app.route('/')
def index():
    return render_template('index.html', config=CONFIG)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': '메시지를 입력해 주세요.'}), 400
        
        if len(user_message) > 500:
            return jsonify({'error': '메시지가 너무 깁니다. 500자 이내로 입력해 주세요.'}), 400
        
        def generate():
            yield "data: "
            for chunk in generate_streaming_response(user_message):
                yield f"data: {chunk}\n"
            yield "data: [DONE]\n\n"
        
        return Response(generate(), mimetype='text/event-stream')
        
    except Exception as e:
        return jsonify({'error': f'서버 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/youtube_search')
def youtube_search():
    """유튜브 검색 결과를 반환하는 엔드포인트"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': '검색어를 입력해 주세요.'}), 400
    
    # 안전한 검색어 처리
    safe_query = re.sub(r'[^\w\s가-힣]', '', query)
    if not safe_query:
        return jsonify({'error': '유효한 검색어가 아닙니다.'}), 400
    
    # YouTube 검색 URL 생성
    youtube_url = f"https://www.youtube.com/results?search_query={safe_query.replace(' ', '+')}"
    
    return jsonify({
        'search_url': youtube_url,
        'query': safe_query,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/clear_history', methods=['POST'])
def clear_history():
    """대화 기록 초기화"""
    global conversation_history
    conversation_history = []
    return jsonify({
        'message': '대화 기록이 초기화되었습니다.',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/conversation_stats')
def conversation_stats():
    """대화 통계 반환"""
    total_messages = len(conversation_history)
    if total_messages == 0:
        return jsonify({
            'total_messages': 0,
            'memory_topics': {},
            'last_conversation': None
        })
    
    # 메모리 주제 통계
    all_keywords = {}
    for conv in conversation_history:
        keywords = conv.get('memory_keywords', {})
        for category, words in keywords.items():
            if category not in all_keywords:
                all_keywords[category] = {}
            for word in words:
                all_keywords[category][word] = all_keywords[category].get(word, 0) + 1
    
    return jsonify({
        'total_messages': total_messages,
        'memory_topics': all_keywords,
        'last_conversation': conversation_history[-1]['timestamp'] if conversation_history else None
    })

@app.route('/health')
def health_check():
    """서버 상태 확인"""
    return jsonify({
        'status': 'healthy',
        'model_ready': model is not None,
        'conversation_count': len(conversation_history),
        'timestamp': datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

if __name__ == '__main__':
    print("🚀 회상치료 AI 아바타 서버를 시작합니다...")
    print(f"📊 설정: 최대 히스토리 {CONFIG['MAX_HISTORY']}개, 최대 문장 {CONFIG['RESPONSE_MAX_SENTENCES']}개")
    
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(
        debug=debug_mode, 
        host='0.0.0.0', 
        port=5000,
        threaded=True
    )
