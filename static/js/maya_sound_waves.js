/**
 * Maya Sound Waves Visualizer
 * Fallback animation for when particle globe doesn't load
 * Provides visual feedback during AI speaking assessments
 */

class MayaSoundWaves {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.isActive = false;
        this.currentState = 'idle';
        this.animationIntensity = 1;
    }

    /**
     * Initialize the sound waves visualization
     */
    init() {
        if (!this.container) {
            console.error('Container not found for Maya Sound Waves');
            return;
        }

        // Create the HTML structure
        this.container.innerHTML = `
            <div class="maya-sound-waves-wrapper">
                <div class="sound-waves-container">
                    <div class="sound-wave" data-wave="1"></div>
                    <div class="sound-wave" data-wave="2"></div>
                    <div class="sound-wave" data-wave="3"></div>
                    <div class="sound-wave" data-wave="4"></div>
                    <div class="sound-wave" data-wave="5"></div>
                    <div class="sound-wave" data-wave="6"></div>
                    <div class="sound-wave" data-wave="7"></div>
                </div>
                <div class="maya-status-text">
                    <span class="status-message">Initializing Maya...</span>
                    <span class="status-indicator"></span>
                </div>
                <div class="maya-info-card">
                    <div class="info-icon">🎤</div>
                    <p class="info-text">Speak clearly into your microphone</p>
                </div>
            </div>
        `;

        // Inject styles if not already present
        this.injectStyles();
        
        // Set initial state
        this.setState('ready');
    }

    /**
     * Inject CSS styles for the sound waves animation
     */
    injectStyles() {
        if (document.getElementById('maya-sound-waves-styles')) {
            return; // Styles already injected
        }

        const styleSheet = document.createElement('style');
        styleSheet.id = 'maya-sound-waves-styles';
        styleSheet.textContent = `
            /* Container Styles */
            .maya-sound-waves-wrapper {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 40px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
                min-height: 300px;
                position: relative;
                overflow: hidden;
            }

            .maya-sound-waves-wrapper::before {
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                animation: rotate 20s linear infinite;
            }

            @keyframes rotate {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            /* Sound Waves Container */
            .sound-waves-container {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                height: 80px;
                margin-bottom: 30px;
                z-index: 1;
                position: relative;
            }

            /* Individual Sound Wave */
            .sound-wave {
                width: 6px;
                height: 40px;
                background: linear-gradient(to top, rgba(255,255,255,0.9), rgba(255,255,255,0.6));
                border-radius: 3px;
                transition: all 0.3s ease;
                box-shadow: 0 0 20px rgba(255,255,255,0.5);
            }

            /* Idle State - Gentle Pulse */
            .maya-sound-waves-wrapper[data-state="idle"] .sound-wave {
                animation: idle-pulse 2s ease-in-out infinite;
                opacity: 0.5;
            }

            @keyframes idle-pulse {
                0%, 100% { transform: scaleY(0.3); opacity: 0.5; }
                50% { transform: scaleY(0.5); opacity: 0.7; }
            }

            /* Ready State - Waiting Animation */
            .maya-sound-waves-wrapper[data-state="ready"] .sound-wave {
                animation: ready-wave 1.4s ease-in-out infinite;
            }

            .maya-sound-waves-wrapper[data-state="ready"] .sound-wave:nth-child(1) { animation-delay: 0s; }
            .maya-sound-waves-wrapper[data-state="ready"] .sound-wave:nth-child(2) { animation-delay: 0.1s; }
            .maya-sound-waves-wrapper[data-state="ready"] .sound-wave:nth-child(3) { animation-delay: 0.2s; }
            .maya-sound-waves-wrapper[data-state="ready"] .sound-wave:nth-child(4) { animation-delay: 0.3s; }
            .maya-sound-waves-wrapper[data-state="ready"] .sound-wave:nth-child(5) { animation-delay: 0.2s; }
            .maya-sound-waves-wrapper[data-state="ready"] .sound-wave:nth-child(6) { animation-delay: 0.1s; }
            .maya-sound-waves-wrapper[data-state="ready"] .sound-wave:nth-child(7) { animation-delay: 0s; }

            @keyframes ready-wave {
                0%, 100% { 
                    transform: scaleY(0.4); 
                    background: linear-gradient(to top, rgba(255,255,255,0.9), rgba(255,255,255,0.6));
                }
                50% { 
                    transform: scaleY(1); 
                    background: linear-gradient(to top, #4facfe, #00f2fe);
                }
            }

            /* Listening State - Active Recording */
            .maya-sound-waves-wrapper[data-state="listening"] .sound-wave {
                animation: listening-wave 0.8s ease-in-out infinite;
                background: linear-gradient(to top, #fa709a, #fee140);
            }

            .maya-sound-waves-wrapper[data-state="listening"] .sound-wave:nth-child(1) { animation-delay: 0s; animation-duration: 0.8s; }
            .maya-sound-waves-wrapper[data-state="listening"] .sound-wave:nth-child(2) { animation-delay: 0.15s; animation-duration: 0.85s; }
            .maya-sound-waves-wrapper[data-state="listening"] .sound-wave:nth-child(3) { animation-delay: 0.3s; animation-duration: 0.9s; }
            .maya-sound-waves-wrapper[data-state="listening"] .sound-wave:nth-child(4) { animation-delay: 0.45s; animation-duration: 0.85s; }
            .maya-sound-waves-wrapper[data-state="listening"] .sound-wave:nth-child(5) { animation-delay: 0.3s; animation-duration: 0.9s; }
            .maya-sound-waves-wrapper[data-state="listening"] .sound-wave:nth-child(6) { animation-delay: 0.15s; animation-duration: 0.85s; }
            .maya-sound-waves-wrapper[data-state="listening"] .sound-wave:nth-child(7) { animation-delay: 0s; animation-duration: 0.8s; }

            @keyframes listening-wave {
                0%, 100% { 
                    transform: scaleY(0.2); 
                    filter: brightness(1);
                }
                25% { 
                    transform: scaleY(1.2); 
                    filter: brightness(1.2);
                }
                50% { 
                    transform: scaleY(0.8); 
                    filter: brightness(1.1);
                }
                75% { 
                    transform: scaleY(1.5); 
                    filter: brightness(1.3);
                }
            }

            /* Speaking State - Maya is Talking */
            .maya-sound-waves-wrapper[data-state="speaking"] .sound-wave {
                animation: speaking-wave 0.6s ease-in-out infinite;
                background: linear-gradient(to top, #30cfd0, #330867);
            }

            .maya-sound-waves-wrapper[data-state="speaking"] .sound-wave:nth-child(1) { animation-delay: 0s; }
            .maya-sound-waves-wrapper[data-state="speaking"] .sound-wave:nth-child(2) { animation-delay: 0.05s; }
            .maya-sound-waves-wrapper[data-state="speaking"] .sound-wave:nth-child(3) { animation-delay: 0.1s; }
            .maya-sound-waves-wrapper[data-state="speaking"] .sound-wave:nth-child(4) { animation-delay: 0.15s; }
            .maya-sound-waves-wrapper[data-state="speaking"] .sound-wave:nth-child(5) { animation-delay: 0.1s; }
            .maya-sound-waves-wrapper[data-state="speaking"] .sound-wave:nth-child(6) { animation-delay: 0.05s; }
            .maya-sound-waves-wrapper[data-state="speaking"] .sound-wave:nth-child(7) { animation-delay: 0s; }

            @keyframes speaking-wave {
                0%, 100% { 
                    transform: scaleY(0.3) scaleX(1); 
                    filter: brightness(1);
                }
                20% { 
                    transform: scaleY(1.8) scaleX(1.1); 
                    filter: brightness(1.3);
                }
                40% { 
                    transform: scaleY(0.5) scaleX(0.95); 
                }
                60% { 
                    transform: scaleY(2) scaleX(1.05); 
                    filter: brightness(1.4);
                }
                80% { 
                    transform: scaleY(0.8) scaleX(1); 
                }
            }

            /* Processing State */
            .maya-sound-waves-wrapper[data-state="processing"] .sound-wave {
                animation: processing-wave 1.5s ease-in-out infinite;
                background: linear-gradient(to top, #f093fb, #f5576c);
            }

            @keyframes processing-wave {
                0%, 100% { 
                    transform: scaleY(0.5) rotate(0deg); 
                    opacity: 0.6;
                }
                50% { 
                    transform: scaleY(1.5) rotate(180deg); 
                    opacity: 1;
                }
            }

            /* Status Text */
            .maya-status-text {
                display: flex;
                align-items: center;
                gap: 10px;
                color: white;
                font-size: 18px;
                font-weight: 500;
                margin-bottom: 20px;
                z-index: 1;
                position: relative;
            }

            .status-message {
                text-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }

            .status-indicator {
                width: 8px;
                height: 8px;
                background: #4ade80;
                border-radius: 50%;
                animation: blink 2s ease-in-out infinite;
                box-shadow: 0 0 10px rgba(74, 222, 128, 0.5);
            }

            @keyframes blink {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.3; }
            }

            /* Info Card */
            .maya-info-card {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                padding: 15px 25px;
                display: flex;
                align-items: center;
                gap: 12px;
                z-index: 1;
                position: relative;
            }

            .info-icon {
                font-size: 24px;
            }

            .info-text {
                color: white;
                font-size: 14px;
                margin: 0;
                opacity: 0.9;
            }

            /* Responsive Design */
            @media (max-width: 768px) {
                .maya-sound-waves-wrapper {
                    padding: 30px 20px;
                    min-height: 250px;
                }

                .sound-waves-container {
                    height: 60px;
                    gap: 6px;
                }

                .sound-wave {
                    width: 4px;
                    height: 30px;
                }

                .maya-status-text {
                    font-size: 16px;
                }

                .maya-info-card {
                    padding: 12px 20px;
                    flex-direction: column;
                    text-align: center;
                }
            }

            /* Error State */
            .maya-sound-waves-wrapper[data-state="error"] .sound-wave {
                background: linear-gradient(to top, #ff4444, #ff6666);
                animation: error-shake 0.3s ease-in-out;
            }

            @keyframes error-shake {
                0%, 100% { transform: translateX(0); }
                25% { transform: translateX(-5px); }
                75% { transform: translateX(5px); }
            }
        `;

        document.head.appendChild(styleSheet);
    }

    /**
     * Set the current state of the visualization
     * @param {string} state - One of: idle, ready, listening, speaking, processing, error
     */
    setState(state) {
        this.currentState = state;
        const wrapper = this.container.querySelector('.maya-sound-waves-wrapper');
        if (wrapper) {
            wrapper.setAttribute('data-state', state);
            this.updateStatusMessage(state);
        }
    }

    /**
     * Update status message based on state
     */
    updateStatusMessage(state) {
        const messages = {
            'idle': 'Initializing Maya...',
            'ready': 'Maya is ready. Click to start!',
            'listening': 'Listening... Speak now',
            'speaking': 'Maya is speaking...',
            'processing': 'Processing your response...',
            'error': 'Connection issue. Please refresh.'
        };

        const messageElement = this.container.querySelector('.status-message');
        if (messageElement) {
            messageElement.textContent = messages[state] || 'Ready';
        }

        // Update info text based on state
        const infoText = this.container.querySelector('.info-text');
        if (infoText) {
            const infoMessages = {
                'listening': 'Speak clearly into your microphone',
                'speaking': 'Listen carefully to Maya',
                'processing': 'Please wait a moment',
                'ready': 'Click the start button when ready',
                'error': 'Check your connection and try again'
            };
            infoText.textContent = infoMessages[state] || 'Ready for assessment';
        }
    }

    /**
     * Animate based on audio input levels
     * @param {number} audioLevel - Audio level from 0 to 1
     */
    updateAudioLevel(audioLevel) {
        if (this.currentState !== 'listening' && this.currentState !== 'speaking') {
            return;
        }

        const waves = this.container.querySelectorAll('.sound-wave');
        waves.forEach((wave, index) => {
            // Create varied heights based on audio level
            const variance = Math.random() * 0.3 + 0.7; // 0.7 to 1.0
            const height = Math.max(0.2, Math.min(2, audioLevel * variance * 2));
            wave.style.transform = `scaleY(${height})`;
        });
    }

    /**
     * Cleanup and destroy the visualization
     */
    destroy() {
        if (this.container) {
            this.container.innerHTML = '';
        }
        this.isActive = false;
    }
}

// Export for use in other scripts
window.MayaSoundWaves = MayaSoundWaves;