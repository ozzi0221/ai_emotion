// 전역 변수들
let isListening = false;
let isSpeaking = false;
let speechRecognition = null;
let speechSynthesis = window.speechSynthesis;
let currentUtterance = null;
let eventSource = null;
let ttsQueue = [];
let isProcessingTTS = false;
let isAvatarSpeaking = false;

// iOS 감지 및 호환성 관리
let isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
let isIOSChrome = isIOS && /CriOS/.test(navigator.userAgent);
let isIOSSafari = isIOS && /Safari/.test(navigator.userAgent) && !/CriOS/.test(navigator.userAgent);

// 음성 기능 지원 여부 확인
let speechRecognitionSupported = false;
let speechSynthesisSupported = false;

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
    detectDeviceCapabilities();
    initializeApp();
    setupEventListeners();
    initializeSpeechRecognition();
    initializeSpeechSynthesis();
    loadSettings();
    checkVideoFiles();
    showIOSNoticeIfNeeded();
});

// 디바이스 기능 감지
function detectDeviceCapabilities() {
    console.log('디바이스 정보:', {
        userAgent: navigator.userAgent,
        isIOS: isIOS,
        isIOSChrome: isIOSChrome,
        isIOSSafari: isIOSSafari
    });

    // Speech Recognition 지원 여부 확인
    speechRecognitionSupported = ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) && !isIOS;
    
    // Speech Synthesis 지원 여부 확인
    speechSynthesisSupported = 'speechSynthesis' in window;
    
    console.log('음성 기능 지원:', {
        speechRecognition: speechRecognitionSupported,
        speechSynthesis: speechSynthesisSupported
    });
}

// iOS 사용자에게 안내 메시지 표시
function showIOSNoticeIfNeeded() {
    if (isIOS) {
        const noticeDiv = document.createElement('div');
        noticeDiv.id = 'iosNotice';
        noticeDiv.className = 'ios-notice';
        noticeDiv.innerHTML = `
            <div class="notice-content">
                <div class="notice-header">
                    <i class="fas fa-info-circle"></i>
                    <h3>iOS 사용자 안내</h3>
                    <button onclick="hideIOSBrowserNotice()" class="close-notice">×</button>
                </div>
                <div class="notice-body">
                    <p><strong>음성 인식:</strong> iOS에서는 보안상 음성 인식이 제한됩니다. 텍스트로 입력해주세요.</p>
                    <p><strong>음성 출력:</strong> ${speechSynthesisSupported ? 
                        '지원됩니다. 화면을 터치하여 음성을 활성화해주세요.' : 
                        '일부 제한이 있을 수 있습니다.'}</p>
                    <div class="notice-actions">
                        ${speechSynthesisSupported ? 
                            '<button onclick="activateIOSSpeech()" class="activate-speech-btn"><i class="fas fa-volume-up"></i> 음성 활성화</button>' : 
                            ''}
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(noticeDiv);
        
        // 3초 후 자동으로 숨기기 (음성 출력이 지원되는 경우)
        if (speechSynthesisSupported) {
            setTimeout(() => {
                noticeDiv.style.opacity = '0.8';
            }, 5000);
        }
    }
}

// iOS 안내 숨기기
function hideIOSBrowserNotice() {
    const notice = document.getElementById('iosNotice');
    if (notice) {
        notice.remove();
    }
}

// iOS 음성 활성화 (사용자 제스처로 음성 초기화)
function activateIOSSpeech() {
    if (isIOS && speechSynthesisSupported) {
        // 더미 음성으로 TTS 엔진 초기화
        const dummyUtterance = new SpeechSynthesisUtterance(' ');
        dummyUtterance.volume = 0.01;
        dummyUtterance.rate = 10;
        
        speechSynthesis.speak(dummyUtterance);
        
        // 초기화 완료 표시
        const activateBtn = document.querySelector('.activate-speech-btn');
        if (activateBtn) {
            activateBtn.innerHTML = '<i class="fas fa-check"></i> 음성 활성화 완료';
            activateBtn.disabled = true;
            activateBtn.style.backgroundColor = '#28a745';
        }
        
        console.log('iOS 음성 엔진 초기화 완료');
        
        // 3초 후 안내 메시지 숨기기
        setTimeout(() => {
            hideIOSBrowserNotice();
        }, 2000);
    }
}

// 비디오 파일 존재 확인
function checkVideoFiles() {
    const video = elements.avatarVideo;
    
    video.addEventListener('loadeddata', function() {
        console.log('아바타 비디오 로드 완료');
    });
    
    video.addEventListener('error', function() {
        console.log('비디오 파일이 없습니다. 대체 화면을 표시합니다.');
        showAvatarFallback('idle');
    });
    
    playIdleVideo();
}

// 앱 초기화
function initializeApp() {
    console.log('회상치료 AI 아바타 시작');
    updateStatus('대기 중');
    
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
    // 마이크 버튼 - iOS에서는 비활성화
    if (speechRecognitionSupported) {
        elements.micBtn.addEventListener('click', toggleSpeechRecognition);
    } else {
        elements.micBtn.style.opacity = '0.5';
        elements.micBtn.style.cursor = 'not-allowed';
        elements.micBtn.title = isIOS ? 'iOS에서는 음성 인식이 지원되지 않습니다' : '이 브라우저는 음성 인식을 지원하지 않습니다';
        elements.micBtn.addEventListener('click', function() {
            if (isIOS) {
                showIOSVoiceAlert('음성 인식은 iOS에서 지원되지 않습니다. 텍스트로 입력해주세요.');
            }
        });
    }
    
    // 스피커 버튼
    elements.speakerBtn.addEventListener('click', toggleSpeaker);
    
    // 전송 버튼
    elements.sendBtn.addEventListener('click', sendMessage);
    
    // 입력 필드
    elements.messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // iOS에서 입력 필드 포커스 시 안내
    if (isIOS) {
        elements.messageInput.addEventListener('focus', function() {
            const placeholder = '텍스트로 대화해보세요. 예: "어린 시절 고향 이야기 들려주세요"';
            if (this.placeholder.includes('음성')) {
                this.placeholder = placeholder;
            }
        });
    }
    
    elements.clearBtn.addEventListener('click', clearChat);
    elements.settingsBtn.addEventListener('click', openSettingsModal);
    
    window.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            closeModal(e.target);
        }
    });
    
    setupSettingsListeners();
}

// iOS 음성 관련 알림
function showIOSVoiceAlert(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'ios-voice-alert';
    alertDiv.innerHTML = `
        <div class="alert-content">
            <i class="fas fa-exclamation-triangle"></i>
            <p>${message}</p>
        </div>
    `;
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => alertDiv.remove(), 300);
    }, 3000);
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

// 음성 인식 초기화 (iOS 제외)
function initializeSpeechRecognition() {
    if (!speechRecognitionSupported) {
        console.warn('음성 인식이 지원되지 않습니다.');
        return;
    }
    
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
}

// 음성 합성 초기화 및 iOS 최적화
function initializeSpeechSynthesis() {
    if (!speechSynthesisSupported) {
        console.warn('음성 합성이 지원되지 않습니다.');
        elements.speakerBtn.style.display = 'none';
        return;
    }
    
    // iOS에서 음성 목록 로드
    if (isIOS) {
        // iOS에서는 speechSynthesis.getVoices()가 비동기적으로 로드됨
        let voices = speechSynthesis.getVoices();
        if (voices.length === 0) {
            speechSynthesis.addEventListener('voiceschanged', function() {
                voices = speechSynthesis.getVoices();
                console.log('iOS 음성 목록 로드됨:', voices.length, '개');
                
                // 한국어 음성 선택
                const koreanVoice = voices.find(voice => 
                    voice.lang.includes('ko') || voice.name.includes('Yuna')
                );
                if (koreanVoice) {
                    voiceSettings.voice = koreanVoice;
                    console.log('한국어 음성 선택:', koreanVoice.name);
                }
            });
        } else {
            const koreanVoice = voices.find(voice => 
                voice.lang.includes('ko') || voice.name.includes('Yuna')
            );
            if (koreanVoice) {
                voiceSettings.voice = koreanVoice;
            }
        }
        
        // iOS에서 음성 재생 최적화
        voiceSettings.rate = Math.max(0.5, Math.min(voiceSettings.rate, 2.0));
        voiceSettings.pitch = Math.max(0.5, Math.min(voiceSettings.pitch, 2.0));
    }
}

// 음성 인식 토글
function toggleSpeechRecognition() {
    if (!speechRecognitionSupported || !speechRecognition) {
        showIOSVoiceAlert('음성 인식을 사용할 수 없습니다.');
        return;
    }
    
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
        
        // iOS에서 처음 활성화할 때 안내
        if (isIOS && !localStorage.getItem('iosVoiceActivated')) {
            showIOSVoiceAlert('음성이 활성화되었습니다. 대화 응답을 들으실 수 있어요.');
            localStorage.setItem('iosVoiceActivated', 'true');
        }
    }
}

// 메시지 전송
function sendMessage() {
    const message = elements.messageInput.value.trim();
    if (!message) return;
    
    addMessage(message, 'user');
    elements.messageInput.value = '';
    
    showLoading();
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
                                    
                                    // TTS 큐에 추가
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
    
    return 'warm';
}

// 유튜브 검색
function searchYouTube(query) {
    const youtubeSearchUrl = `https://www.youtube.com/results?search_query=${encodeURIComponent(query)}`;
    
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
    if (!speechSynthesisSupported) return;
    
    ttsQueue.push(text);
    if (!isProcessingTTS) {
        processTTSQueue();
    }
}

// iOS 최적화된 TTS 큐 처리
function processTTSQueue() {
    if (ttsQueue.length === 0) {
        isProcessingTTS = false;
        isSpeaking = false;
        
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
    
    // iOS에서 이전 음성 정리
    if (speechSynthesis.speaking) {
        speechSynthesis.cancel();
        
        // iOS에서는 cancel 후 짧은 대기 시간 필요
        if (isIOS) {
            setTimeout(() => {
                speakText(text);
            }, 150);
            return;
        }
    }
    
    speakText(text);
}

// iOS 최적화된 음성 출력
function speakText(text) {
    if (!speechSynthesisSupported) {
        setTimeout(() => processTTSQueue(), 300);
        return;
    }
    
    currentUtterance = new SpeechSynthesisUtterance(text);
    currentUtterance.lang = voiceSettings.lang;
    currentUtterance.rate = voiceSettings.rate;
    currentUtterance.pitch = voiceSettings.pitch;
    currentUtterance.volume = voiceSettings.volume;
    
    // iOS에서 한국어 음성 설정
    if (isIOS && voiceSettings.voice) {
        currentUtterance.voice = voiceSettings.voice;
    }
    
    // iOS 특화 설정
    if (isIOS) {
        // iOS에서 더 안정적인 설정값 사용
        currentUtterance.rate = Math.max(0.5, Math.min(currentUtterance.rate, 1.5));
        currentUtterance.pitch = Math.max(0.8, Math.min(currentUtterance.pitch, 1.2));
    }
    
    currentUtterance.onstart = function() {
        console.log('TTS 시작:', text.substring(0, 20) + '...');
        isSpeaking = true;
        updateStatus('말하고 있습니다', 'speaking');
        playSpeakingVideo();
    };
    
    currentUtterance.onend = function() {
        console.log('TTS 종료');
        isSpeaking = false;
        
        // iOS에서는 더 긴 대기 시간 필요
        const delay = isIOS ? 500 : 300;
        setTimeout(() => {
            processTTSQueue();
        }, delay);
    };
    
    currentUtterance.onerror = function(event) {
        console.error('TTS 오류:', event);
        isSpeaking = false;
        
        // iOS에서 오류 발생 시 재시도 로직
        if (isIOS && event.error === 'interrupted' && ttsQueue.length > 0) {
            console.log('iOS TTS 인터럽트 - 재시도');
            setTimeout(() => {
                processTTSQueue();
            }, 800);
        } else {
            setTimeout(() => {
                processTTSQueue();
            }, 300);
        }
    };
    
    // iOS에서 음성 재생 전 추가 체크
    if (isIOS) {
        // speechSynthesis가 paused 상태인 경우 resume
        if (speechSynthesis.paused) {
            speechSynthesis.resume();
        }
        
        // iOS에서 음성 재생 전 짧은 대기
        setTimeout(() => {
            try {
                speechSynthesis.speak(currentUtterance);
            } catch (error) {
                console.error('iOS TTS 재생 오류:', error);
                setTimeout(() => processTTSQueue(), 500);
            }
        }, 100);
    } else {
        speechSynthesis.speak(currentUtterance);
    }
}

// 음성 정지 (iOS 최적화)
function stopSpeaking() {
    console.log('음성 정지');
    
    if (speechSynthesis.speaking) {
        speechSynthesis.cancel();
    }
    
    // iOS에서 더 확실한 정지를 위한 추가 처리
    if (isIOS) {
        setTimeout(() => {
            if (speechSynthesis.speaking) {
                speechSynthesis.cancel();
            }
        }, 100);
    }
    
    ttsQueue = [];
    isProcessingTTS = false;
    isSpeaking = false;
    
    updateStatus('대기 중');
    playIdleVideo();
}

// 상태 업데이트
function updateStatus(text, type = 'idle') {
    const statusText = elements.statusIndicator.querySelector('.status-text');
    statusText.textContent = text;
    
    elements.statusIndicator.className = `status-indicator ${type}`;
}

// 아바타 비디오 제어
function playIdleVideo() {
    console.log('Idle 비디오 재생');
    const video = elements.avatarVideo;
    video.src = '/static/videos/avatar_idle.mp4';
    video.classList.remove('speaking');
    isAvatarSpeaking = false;
    
    video.play().catch(e => {
        console.log('비디오 재생 오류:', e);
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
        
        elements.avatarVideo.style.display = 'none';
        avatarContainer.appendChild(fallbackDiv);
    } else {
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

// 전역 함수로 export
window.sendQuickMessage = sendQuickMessage;
window.searchYouTube = searchYouTube;
window.closeYoutubeModal = closeYoutubeModal;
window.closeSettingsModal = closeSettingsModal;
window.hideIOSBrowserNotice = hideIOSBrowserNotice;
window.activateIOSSpeech = activateIOSSpeech;
