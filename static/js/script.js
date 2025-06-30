// 전역 변수들
let isListening = false;
let isSpeaking = false;
let speechRecognition = null;
let speechSynthesis = window.speechSynthesis;
let currentUtterance = null;
let eventSource = null;
let ttsQueue = [];
let isProcessingTTS = false;
let isAvatarSpeaking = false; // 아바타 상태 추적용

// 설정값들
let voiceSettings = {
    rate: 0.8,
    pitch: 1.0,
    volume: 0.8,
    lang: 'ko-KR'
};

// DOM 요소들
const elements = {
    micBtn: document.getElementById('micBtn'),
    speakerBtn: document.getElementById('speakerBtn'),
    sendBtn: document.getElementById('sendBtn'),
    clearBtn: document.getElementById('clearBtn'),
    settingsBtn: document.getElementById('settingsBtn'),
    messageInput: document.getElementById('messageInput'),
    chatContainer: document.getElementById('chatContainer'),
    avatarVideo: document.getElementById('avatarVideo'),
    statusIndicator: document.getElementById('statusIndicator'),
    audioVisualizer: document.getElementById('audioVisualizer'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    youtubeModal: document.getElementById('youtubeModal'),
    settingsModal: document.getElementById('settingsModal')
};

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    initializeSpeechRecognition();
    loadSettings();
    checkVideoFiles();
});

// 비디오 파일 존재 확인
function checkVideoFiles() {
    const video = elements.avatarVideo;
    
    // 비디오 로드 이벤트
    video.addEventListener('loadeddata', function() {
        console.log('아바타 비디오 로드 완료');
    });
    
    // 비디오 에러 이벤트
    video.addEventListener('error', function() {
        console.log('비디오 파일이 없습니다. 대체 화면을 표시합니다.');
        showAvatarFallback('idle');
    });
    
    // 초기 비디오 재생 시도
    playIdleVideo();
}

// 앱 초기화
function initializeApp() {
    console.log('회상치료 AI 아바타 시작');
    updateStatus('대기 중');
    
    // 웰컴 메시지 애니메이션
    setTimeout(() => {
        const welcomeMessage = document.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.style.opacity = '1';
            welcomeMessage.style.transform = 'translateY(0)';
        }
    }, 500);
}

// 이벤트 리스너 설정
function setupEventListeners() {
    // 마이크 버튼
    elements.micBtn.addEventListener('click', toggleSpeechRecognition);
    
    // 스피커 버튼
    elements.speakerBtn.addEventListener('click', toggleSpeaker);
    
    // 전송 버튼
    elements.sendBtn.addEventListener('click', sendMessage);
    
    // 입력 필드 엔터키
    elements.messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // 대화 초기화 버튼
    elements.clearBtn.addEventListener('click', clearChat);
    
    // 설정 버튼
    elements.settingsBtn.addEventListener('click', openSettingsModal);
    
    // 모달 외부 클릭 시 닫기
    window.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            closeModal(e.target);
        }
    });
    
    // 설정 슬라이더 이벤트
    setupSettingsListeners();
}

// 설정 관련 이벤트 리스너
function setupSettingsListeners() {
    const voiceSpeedSlider = document.getElementById('voiceSpeed');
    const voicePitchSlider = document.getElementById('voicePitch');
    const voiceVolumeSlider = document.getElementById('voiceVolume');
    
    if (voiceSpeedSlider) {
        voiceSpeedSlider.addEventListener('input', function() {
            voiceSettings.rate = parseFloat(this.value);
            document.getElementById('voiceSpeedValue').textContent = this.value + 'x';
            saveSettings();
        });
    }
    
    if (voicePitchSlider) {
        voicePitchSlider.addEventListener('input', function() {
            voiceSettings.pitch = parseFloat(this.value);
            document.getElementById('voicePitchValue').textContent = this.value;
            saveSettings();
        });
    }
    
    if (voiceVolumeSlider) {
        voiceVolumeSlider.addEventListener('input', function() {
            voiceSettings.volume = parseFloat(this.value);
            document.getElementById('voiceVolumeValue').textContent = this.value;
            saveSettings();
        });
    }
}

// 음성 인식 초기화
function initializeSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        speechRecognition = new SpeechRecognition();
        
        speechRecognition.continuous = false;
        speechRecognition.interimResults = false;
        speechRecognition.lang = 'ko-KR';
        
        speechRecognition.onstart = function() {
            isListening = true;
            updateStatus('듣고 있습니다', 'listening');
            elements.micBtn.classList.add('active');
            showAudioVisualizer();
        };
        
        speechRecognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            elements.messageInput.value = transcript;
            sendMessage();
        };
        
        speechRecognition.onend = function() {
            isListening = false;
            updateStatus('대기 중');
            elements.micBtn.classList.remove('active');
            hideAudioVisualizer();
        };
        
        speechRecognition.onerror = function(event) {
            console.error('음성 인식 오류:', event.error);
            isListening = false;
            updateStatus('대기 중');
            elements.micBtn.classList.remove('active');
            hideAudioVisualizer();
        };
    } else {
        console.warn('이 브라우저는 음성 인식을 지원하지 않습니다.');
        elements.micBtn.style.display = 'none';
    }
}

// 음성 인식 토글
function toggleSpeechRecognition() {
    if (!speechRecognition) return;
    
    if (isListening) {
        speechRecognition.stop();
    } else {
        if (isSpeaking) {
            stopSpeaking();
        }
        speechRecognition.start();
    }
}

// 스피커 토글
function toggleSpeaker() {
    const isActive = elements.speakerBtn.classList.contains('active');
    
    if (isActive) {
        elements.speakerBtn.classList.remove('active');
        elements.speakerBtn.innerHTML = '<i class="fas fa-volume-mute"></i><span class="btn-text">음성 출력</span>';
        stopSpeaking();
    } else {
        elements.speakerBtn.classList.add('active');
        elements.speakerBtn.innerHTML = '<i class="fas fa-volume-up"></i><span class="btn-text">음성 출력</span>';
    }
}

// 메시지 전송
function sendMessage() {
    const message = elements.messageInput.value.trim();
    if (!message) return;
    
    // 사용자 메시지 추가
    addMessage(message, 'user');
    elements.messageInput.value = '';
    
    // 로딩 표시
    showLoading();
    
    // 서버에 메시지 전송
    sendToServer(message);
}

// 빠른 메시지 전송
function sendQuickMessage(message) {
    elements.messageInput.value = message;
    sendMessage();
}

// 서버로 메시지 전송 (스트리밍)
function sendToServer(message) {
    if (eventSource) {
        eventSource.close();
    }
    
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('서버 응답 오류');
        }
        
        hideLoading();
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let currentMessageElement = null;
        let fullResponse = '';
        
        function readStream() {
            reader.read().then(({ done, value }) => {
                if (done) {
                    if (currentMessageElement) {
                        // 모든 TTS가 끝났을 때 idle 상태로 전환
                        setTimeout(() => {
                            if (ttsQueue.length === 0 && !isProcessingTTS) {
                                updateStatus('대기 중');
                                playIdleVideo();
                            }
                        }, 500);
                    }
                    return;
                }
                
                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');
                
                lines.forEach(line => {
                    if (line.startsWith('data: ') && line !== 'data: [DONE]') {
                        try {
                            const jsonStr = line.substring(6);
                            if (jsonStr.trim()) {
                                const data = JSON.parse(jsonStr);
                                
                                if (data.type === 'sentence') {
                                    if (!currentMessageElement) {
                                        currentMessageElement = addMessage('', 'assistant');
                                    }
                                    
                                    const messageContent = currentMessageElement.querySelector('.message-content');
                                    fullResponse += data.content + ' ';
                                    messageContent.innerHTML = '<p>' + fullResponse + '</p>';
                                    
                                    // TTS 큐에 추가 (여기서는 상태 변경 안 함)
                                    if (elements.speakerBtn.classList.contains('active')) {
                                        addToTTSQueue(data.content);
                                    }
                                    
                                    // 감정 상태 분석 및 표시
                                    const emotion = analyzeResponseForEmotion(data.content);
                                    showEmotionIndicator(emotion);
                                    
                                    // 유튜브 검색어가 있으면 링크 생성
                                    if (data.youtube_search) {
                                        addYouTubeLink(messageContent, data.youtube_search);
                                    }
                                    
                                    // 메모리 키워드 표시
                                    if (data.memory_keywords && Object.keys(data.memory_keywords).length > 0) {
                                        addMemoryKeywords(messageContent, data.memory_keywords);
                                    }
                                    
                                    scrollToBottom();
                                }
                            }
                        } catch (e) {
                            console.error('JSON 파싱 오류:', e);
                        }
                    }
                });
                
                readStream();
            }).catch(error => {
                console.error('스트림 읽기 오류:', error);
                hideLoading();
                addMessage('죄송합니다. 오류가 발생했습니다.', 'assistant');
                updateStatus('대기 중');
                playIdleVideo();
            });
        }
        
        readStream();
    })
    .catch(error => {
        console.error('요청 오류:', error);
        hideLoading();
        addMessage('죄송합니다. 서버와 연결할 수 없습니다.', 'assistant');
        updateStatus('대기 중');
        playIdleVideo();
    });
}

// 메시지 추가
function addMessage(content, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    
    if (type === 'user') {
        avatarDiv.innerHTML = '<i class="fas fa-user"></i>';
    } else {
        avatarDiv.innerHTML = '<i class="fas fa-heart"></i>';
    }
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = `<p>${content}</p>`;
    
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    
    elements.chatContainer.appendChild(messageDiv);
    scrollToBottom();
    
    return messageDiv;
}

// 유튜브 링크 추가
function addYouTubeLink(messageElement, searchQuery) {
    const linkDiv = document.createElement('div');
    linkDiv.className = 'youtube-link';
    linkDiv.innerHTML = `
        <button onclick="searchYouTube('${searchQuery}')" class="youtube-btn">
            <i class="fab fa-youtube"></i> "${searchQuery}" 영상 보기
        </button>
    `;
    messageElement.appendChild(linkDiv);
}

// 메모리 키워드 추가
function addMemoryKeywords(messageElement, keywords) {
    const keywordDiv = document.createElement('div');
    keywordDiv.className = 'memory-keywords';
    
    let keywordHTML = '<h4><i class="fas fa-heart"></i> 이야기 속 추억들</h4><div class="keyword-tags">';
    
    for (const [category, words] of Object.entries(keywords)) {
        for (const word of words) {
            keywordHTML += `<span class="keyword-tag">${word}</span>`;
        }
    }
    
    keywordHTML += '</div>';
    keywordDiv.innerHTML = keywordHTML;
    messageElement.appendChild(keywordDiv);
}

// 감정 상태 표시
function showEmotionIndicator(emotion) {
    const avatarContainer = document.querySelector('.avatar-container');
    let emotionIndicator = avatarContainer.querySelector('.emotion-indicator');
    
    if (!emotionIndicator) {
        emotionIndicator = document.createElement('div');
        emotionIndicator.className = 'emotion-indicator';
        avatarContainer.appendChild(emotionIndicator);
    }
    
    const emotionTexts = {
        'happy': '기뻐하며',
        'sad': '슬퍼하며', 
        'thoughtful': '생각하며',
        'nostalgic': '추억에 잠겨',
        'warm': '따뜻하게'
    };
    
    emotionIndicator.innerHTML = `
        <i class="fas fa-heart"></i>
        <span>${emotionTexts[emotion] || '공감하며'}</span>
    `;
    
    emotionIndicator.classList.add('show');
    
    // 3초 후 숨기기
    setTimeout(() => {
        emotionIndicator.classList.remove('show');
    }, 3000);
}

// 회상치료 특화 응답 분석
function analyzeResponseForEmotion(text) {
    const emotionKeywords = {
        'nostalgic': ['추억', '그때', '옛날', '어릴', '젊을', '시절'],
        'happy': ['행복', '기뻐', '좋아', '즐거', '웃음'],
        'thoughtful': ['생각', '기억', '떠올', '회상'],
        'warm': ['따뜻', '정겨', '포근', '사랑']
    };
    
    for (const [emotion, keywords] of Object.entries(emotionKeywords)) {
        for (const keyword of keywords) {
            if (text.includes(keyword)) {
                return emotion;
            }
        }
    }
    
    return 'warm'; // 기본값
}

// 유튜브 검색
function searchYouTube(query) {
    const youtubeSearchUrl = `https://www.youtube.com/results?search_query=${encodeURIComponent(query)}`;
    
    // 모달에 검색 링크와 설명 표시
    const youtubeContainer = document.getElementById('youtubeContainer');
    youtubeContainer.innerHTML = `
        <div class="youtube-search-container">
            <div class="youtube-icon">
                <i class="fab fa-youtube"></i>
            </div>
            <h3>"${query}" 검색 결과</h3>
            <p>아래 버튼을 클릭하면 유튜브에서 관련 영상을 보실 수 있어요</p>
            <a href="${youtubeSearchUrl}" target="_blank" class="youtube-link-btn">
                <i class="fab fa-youtube"></i>
                유튜브에서 보기
            </a>
            <div class="suggested-searches">
                <p>다른 검색어도 시도해보세요:</p>
                <button onclick="searchYouTube('${query} 옛날 버전')" class="suggestion-search-btn">${query} 옛날 버전</button>
                <button onclick="searchYouTube('${query} 추억')" class="suggestion-search-btn">${query} 추억</button>
                <button onclick="searchYouTube('${query} 클래식')" class="suggestion-search-btn">${query} 클래식</button>
            </div>
        </div>
    `;
    
    openYoutubeModal();
}

// TTS 큐에 추가
function addToTTSQueue(text) {
    ttsQueue.push(text);
    if (!isProcessingTTS) {
        processTTSQueue();
    }
}

// TTS 큐 처리 - 비디오 동기화 개선
function processTTSQueue() {
    if (ttsQueue.length === 0) {
        isProcessingTTS = false;
        isSpeaking = false;
        
        // TTS 큐가 완전히 비었을 때만 idle 상태로 전환
        setTimeout(() => {
            if (ttsQueue.length === 0 && !isProcessingTTS) {
                updateStatus('대기 중');
                playIdleVideo();
            }
        }, 200);
        return;
    }
    
    isProcessingTTS = true;
    const text = ttsQueue.shift();
    
    if (speechSynthesis.speaking) {
        speechSynthesis.cancel();
    }
    
    currentUtterance = new SpeechSynthesisUtterance(text);
    currentUtterance.lang = voiceSettings.lang;
    currentUtterance.rate = voiceSettings.rate;
    currentUtterance.pitch = voiceSettings.pitch;
    currentUtterance.volume = voiceSettings.volume;
    
    // 음성 시작 시 speaking 비디오로 전환
    currentUtterance.onstart = function() {
        console.log('TTS 시작 - speaking 비디오로 전환');
        isSpeaking = true;
        updateStatus('말하고 있습니다', 'speaking');
        playSpeakingVideo();
    };
    
    // 음성 종료 시 다음 큐 처리
    currentUtterance.onend = function() {
        console.log('TTS 종료 - 다음 큐 처리');
        isSpeaking = false;
        
        // 잠시 대기 후 다음 큐 처리
        setTimeout(() => {
            processTTSQueue();
        }, 300);
    };
    
    currentUtterance.onerror = function(event) {
        console.error('TTS 오류:', event);
        isSpeaking = false;
        setTimeout(() => {
            processTTSQueue();
        }, 300);
    };
    
    console.log('TTS 시작:', text);
    speechSynthesis.speak(currentUtterance);
}

// 음성 정지
function stopSpeaking() {
    console.log('음성 정지');
    if (speechSynthesis.speaking) {
        speechSynthesis.cancel();
    }
    ttsQueue = [];
    isProcessingTTS = false;
    isSpeaking = false;
    
    // 즉시 idle 상태로 전환
    updateStatus('대기 중');
    playIdleVideo();
}

// 상태 업데이트
function updateStatus(text, type = 'idle') {
    const statusText = elements.statusIndicator.querySelector('.status-text');
    statusText.textContent = text;
    
    elements.statusIndicator.className = `status-indicator ${type}`;
}

// 아바타 비디오 제어 - 개선된 버전
function playIdleVideo() {
    console.log('Idle 비디오 재생');
    const video = elements.avatarVideo;
    video.src = '/static/videos/avatar_idle.mp4';
    video.classList.remove('speaking');
    isAvatarSpeaking = false;
    
    video.play().catch(e => {
        console.log('비디오 재생 오류:', e);
        // 비디오 파일이 없으면 정적 이미지로 대체
        showAvatarFallback('idle');
    });
}

function playSpeakingVideo() {
    console.log('Speaking 비디오 재생');
    const video = elements.avatarVideo;
    video.src = '/static/videos/avatar_speaking.mp4';
    video.classList.add('speaking');
    isAvatarSpeaking = true;
    
    video.play().catch(e => {
        console.log('비디오 재생 오류:', e);
        // 비디오 파일이 없으면 정적 이미지로 대체
        showAvatarFallback('speaking');
    });
}

// 비디오 대체 처리
function showAvatarFallback(state) {
    const avatarContainer = document.querySelector('.avatar-container');
    const existingFallback = avatarContainer.querySelector('.avatar-fallback');
    
    if (!existingFallback) {
        const fallbackDiv = document.createElement('div');
        fallbackDiv.className = 'avatar-fallback';
        fallbackDiv.innerHTML = `
            <div class="avatar-placeholder ${state}">
                <div class="avatar-icon">
                    <i class="fas fa-heart"></i>
                </div>
                <div class="avatar-name">감정비서</div>
                <div class="avatar-status">${state === 'speaking' ? '말하고 있습니다' : '대기 중입니다'}</div>
            </div>
        `;
        
        // 비디오 숨기고 fallback 표시
        elements.avatarVideo.style.display = 'none';
        avatarContainer.appendChild(fallbackDiv);
    } else {
        // 기존 fallback 상태 업데이트
        const placeholder = existingFallback.querySelector('.avatar-placeholder');
        const statusText = existingFallback.querySelector('.avatar-status');
        
        placeholder.className = `avatar-placeholder ${state}`;
        statusText.textContent = state === 'speaking' ? '말하고 있습니다' : '대기 중입니다';
    }
}

// 음성 시각화 제어
function showAudioVisualizer() {
    elements.audioVisualizer.classList.add('active');
}

function hideAudioVisualizer() {
    elements.audioVisualizer.classList.remove('active');
}

// 로딩 표시
function showLoading() {
    elements.loadingOverlay.classList.add('show');
}

function hideLoading() {
    elements.loadingOverlay.classList.remove('show');
}

// 채팅 초기화
function clearChat() {
    if (confirm('대화 기록을 모두 삭제하시겠습니까?')) {
        // 음성 정지
        stopSpeaking();
        
        elements.chatContainer.innerHTML = `
            <div class="welcome-message">
                <div class="message assistant-message">
                    <div class="message-avatar">
                        <i class="fas fa-heart"></i>
                    </div>
                    <div class="message-content">
                        <p>안녕하세요. 저는 회상치료를 도와드리는 AI 아바타입니다.</p>
                        <p>옛날 추억이나 좋아하셨던 노래, 사진에 대해 이야기해보실까요.</p>
                        <div class="quick-suggestions">
                            <button class="suggestion-btn" onclick="sendQuickMessage('어린 시절 고향 이야기 들려주세요')">
                                <i class="fas fa-home"></i> 고향 이야기
                            </button>
                            <button class="suggestion-btn" onclick="sendQuickMessage('좋아하셨던 노래가 있나요?')">
                                <i class="fas fa-music"></i> 좋아하는 노래
                            </button>
                            <button class="suggestion-btn" onclick="sendQuickMessage('자녀분들과의 추억을 들려주세요')">
                                <i class="fas fa-users"></i> 가족 추억
                            </button>
                            <button class="suggestion-btn" onclick="sendQuickMessage('첫 월급 받으셨던 날 기억나세요?')">
                                <i class="fas fa-coins"></i> 첫 월급
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // 서버에 초기화 요청
        fetch('/clear_history', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        }).catch(e => console.error('히스토리 초기화 오류:', e));
    }
}

// 스크롤 하단으로
function scrollToBottom() {
    elements.chatContainer.scrollTop = elements.chatContainer.scrollHeight;
}

// 모달 제어
function openYoutubeModal() {
    elements.youtubeModal.classList.add('show');
}

function closeYoutubeModal() {
    elements.youtubeModal.classList.remove('show');
    const youtubeContainer = document.getElementById('youtubeContainer');
    youtubeContainer.innerHTML = '';
}

function openSettingsModal() {
    elements.settingsModal.classList.add('show');
}

function closeSettingsModal() {
    elements.settingsModal.classList.remove('show');
}

function closeModal(modal) {
    modal.classList.remove('show');
}

// 설정 저장/로드
function saveSettings() {
    localStorage.setItem('voiceSettings', JSON.stringify(voiceSettings));
}

function loadSettings() {
    const saved = localStorage.getItem('voiceSettings');
    if (saved) {
        voiceSettings = { ...voiceSettings, ...JSON.parse(saved) };
        
        // UI 업데이트
        const speedSlider = document.getElementById('voiceSpeed');
        const pitchSlider = document.getElementById('voicePitch');
        const volumeSlider = document.getElementById('voiceVolume');
        
        if (speedSlider) {
            speedSlider.value = voiceSettings.rate;
            document.getElementById('voiceSpeedValue').textContent = voiceSettings.rate + 'x';
        }
        
        if (pitchSlider) {
            pitchSlider.value = voiceSettings.pitch;
            document.getElementById('voicePitchValue').textContent = voiceSettings.pitch;
        }
        
        if (volumeSlider) {
            volumeSlider.value = voiceSettings.volume;
            document.getElementById('voiceVolumeValue').textContent = voiceSettings.volume;
        }
    }
}

// 전역 함수로 export (HTML에서 사용)
window.sendQuickMessage = sendQuickMessage;
window.searchYouTube = searchYouTube;
window.closeYoutubeModal = closeYoutubeModal;
window.closeSettingsModal = closeSettingsModal;
