/**
 * Maya Visualizer Manager
 * Handles particle globe with automatic fallback to sound waves
 */

class MayaVisualizerManager {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.currentVisualizer = null;
        this.useGlobe = true;
        this.globeLoadTimeout = 5000; // 5 seconds to load globe
        this.soundWaves = null;
    }

    /**
     * Initialize visualization with automatic fallback
     */
    async initialize() {
        if (!this.container) {
            console.error('Visualizer container not found');
            return false;
        }

        // Show loading state
        this.showLoading();

        // Try to load particle globe first
        const globeLoaded = await this.tryLoadParticleGlobe();
        
        if (globeLoaded) {
            console.log('✅ Particle globe loaded successfully');
            this.currentVisualizer = 'globe';
        } else {
            console.log('⚠️ Particle globe failed, loading sound waves fallback');
            this.loadSoundWavesFallback();
            this.currentVisualizer = 'soundwaves';
        }

        return true;
    }

    /**
     * Show loading indicator
     */
    showLoading() {
        this.container.innerHTML = `
            <div class="visualizer-loading">
                <div class="spinner"></div>
                <p>Preparing Maya...</p>
            </div>
            <style>
                .visualizer-loading {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    padding: 40px;
                    min-height: 300px;
                }
                .spinner {
                    width: 50px;
                    height: 50px;
                    border: 3px solid rgba(52, 152, 219, 0.3);
                    border-top: 3px solid #3498db;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        `;
    }

    /**
     * Attempt to load the particle globe
     */
    async tryLoadParticleGlobe() {
        return new Promise((resolve) => {
            // Check for WebGL support first
            if (!this.checkWebGLSupport()) {
                console.log('WebGL not supported, skipping globe');
                resolve(false);
                return;
            }

            // Set a timeout for globe loading
            const timeout = setTimeout(() => {
                console.log('Globe loading timeout');
                resolve(false);
            }, this.globeLoadTimeout);

            try {
                // Check if particle globe script exists
                if (typeof window.initParticleGlobe === 'function') {
                    // Try to initialize the globe
                    window.initParticleGlobe(this.containerId)
                        .then(() => {
                            clearTimeout(timeout);
                            resolve(true);
                        })
                        .catch((error) => {
                            console.error('Globe initialization failed:', error);
                            clearTimeout(timeout);
                            resolve(false);
                        });
                } else if (typeof window.ParticleGlobe !== 'undefined') {
                    // Alternative globe initialization
                    try {
                        const globe = new window.ParticleGlobe(this.containerId);
                        globe.init();
                        clearTimeout(timeout);
                        resolve(true);
                    } catch (error) {
                        console.error('Globe creation failed:', error);
                        clearTimeout(timeout);
                        resolve(false);
                    }
                } else {
                    // Globe script not loaded
                    console.log('Particle globe not available');
                    clearTimeout(timeout);
                    resolve(false);
                }
            } catch (error) {
                console.error('Error loading globe:', error);
                clearTimeout(timeout);
                resolve(false);
            }
        });
    }

    /**
     * Check if WebGL is supported
     */
    checkWebGLSupport() {
        try {
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            return !!gl;
        } catch (e) {
            return false;
        }
    }

    /**
     * Load sound waves fallback
     */
    loadSoundWavesFallback() {
        // Clear container
        this.container.innerHTML = '';
        
        // Initialize sound waves
        if (typeof window.MayaSoundWaves !== 'undefined') {
            this.soundWaves = new window.MayaSoundWaves(this.containerId);
            this.soundWaves.init();
            
            // Add smooth fade-in
            this.container.style.opacity = '0';
            this.container.style.transition = 'opacity 0.5s ease-in';
            setTimeout(() => {
                this.container.style.opacity = '1';
            }, 100);
        } else {
            // If sound waves script also failed, show basic fallback
            this.loadBasicFallback();
        }
    }

    /**
     * Load basic HTML fallback if everything else fails
     */
    loadBasicFallback() {
        this.container.innerHTML = `
            <div class="maya-basic-fallback">
                <div class="maya-avatar">
                    <div class="avatar-icon">🎙️</div>
                </div>
                <h3 class="maya-name">Maya AI Examiner</h3>
                <p class="maya-status">Ready for your speaking assessment</p>
                <div class="status-indicator active"></div>
            </div>
            <style>
                .maya-basic-fallback {
                    text-align: center;
                    padding: 40px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 20px;
                    color: white;
                }
                .maya-avatar {
                    width: 80px;
                    height: 80px;
                    margin: 0 auto 20px;
                    background: rgba(255,255,255,0.2);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .avatar-icon {
                    font-size: 40px;
                }
                .maya-name {
                    margin: 10px 0;
                    font-size: 24px;
                }
                .maya-status {
                    opacity: 0.9;
                    font-size: 16px;
                }
                .status-indicator {
                    width: 10px;
                    height: 10px;
                    background: #4ade80;
                    border-radius: 50%;
                    margin: 20px auto 0;
                    animation: pulse 2s ease-in-out infinite;
                }
                @keyframes pulse {
                    0%, 100% { transform: scale(1); opacity: 1; }
                    50% { transform: scale(1.2); opacity: 0.7; }
                }
            </style>
        `;
    }

    /**
     * Update visualization state based on Maya's status
     */
    setState(state) {
        if (this.currentVisualizer === 'soundwaves' && this.soundWaves) {
            this.soundWaves.setState(state);
        } else if (this.currentVisualizer === 'globe' && window.particleGlobeInstance) {
            // Update globe state if it has that capability
            if (typeof window.particleGlobeInstance.setState === 'function') {
                window.particleGlobeInstance.setState(state);
            }
        }
    }

    /**
     * Update audio levels for visualization
     */
    updateAudioLevel(level) {
        if (this.currentVisualizer === 'soundwaves' && this.soundWaves) {
            this.soundWaves.updateAudioLevel(level);
        } else if (this.currentVisualizer === 'globe' && window.particleGlobeInstance) {
            if (typeof window.particleGlobeInstance.updateAudioLevel === 'function') {
                window.particleGlobeInstance.updateAudioLevel(level);
            }
        }
    }

    /**
     * Clean up visualization
     */
    destroy() {
        if (this.soundWaves) {
            this.soundWaves.destroy();
        }
        if (window.particleGlobeInstance && typeof window.particleGlobeInstance.destroy === 'function') {
            window.particleGlobeInstance.destroy();
        }
        this.currentVisualizer = null;
    }

    /**
     * Get current visualizer type
     */
    getCurrentVisualizer() {
        return this.currentVisualizer;
    }

    /**
     * Check if visualization is ready
     */
    isReady() {
        return this.currentVisualizer !== null;
    }
}

// Make available globally
window.MayaVisualizerManager = MayaVisualizerManager;