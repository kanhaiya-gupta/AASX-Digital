/**
 * Animation Controls Module
 * Handles physics simulation animations, playback controls, and timeline management
 */

import PhysicsModelingAPI from '../../shared/api.js';
import PhysicsModelingUtils from '../../shared/utils.js';

class PhysicsAnimation {
    constructor() {
        this.api = new PhysicsModelingAPI();
        this.utils = new PhysicsModelingUtils();
        
        // Animation state
        this.animationState = {
            isPlaying: false,
            isPaused: false,
            currentFrame: 0,
            totalFrames: 0,
            fps: 30,
            speed: 1.0,
            loop: true,
            direction: 'forward' // 'forward' or 'reverse'
        };
        
        // Animation data
        this.animationData = {
            frames: [],
            metadata: {},
            keyframes: [],
            transitions: []
        };
        
        // Animation instances
        this.animations = new Map();
        
        // Event listeners
        this.eventListeners = new Map();
        
        // Animation loop
        this.animationLoop = null;
        this.lastFrameTime = 0;
        
        // Performance monitoring
        this.performance = {
            frameCount: 0,
            averageFPS: 0,
            droppedFrames: 0,
            lastUpdate: Date.now()
        };
    }

    /**
     * Initialize animation system
     */
    async init() {
        try {
            console.log('Initializing Physics Animation...');
            
            // Setup animation loop
            this.setupAnimationLoop();
            
            // Setup event system
            this.setupEventSystem();
            
            console.log('Physics Animation initialized successfully');
            
        } catch (error) {
            console.error('Error initializing Physics Animation:', error);
            this.utils.handleError(error, 'PhysicsAnimation.init');
        }
    }

    /**
     * Setup animation loop
     */
    setupAnimationLoop() {
        const animate = (currentTime) => {
            if (this.animationState.isPlaying && !this.animationState.isPaused) {
                this.updateAnimation(currentTime);
            }
            this.animationLoop = requestAnimationFrame(animate);
        };
        
        this.animationLoop = requestAnimationFrame(animate);
    }

    /**
     * Setup event system
     */
    setupEventSystem() {
        // Animation events
        this.eventListeners.set('play', []);
        this.eventListeners.set('pause', []);
        this.eventListeners.set('stop', []);
        this.eventListeners.set('frameUpdate', []);
        this.eventListeners.set('complete', []);
        this.eventListeners.set('error', []);
    }

    /**
     * Load animation data from simulation
     */
    async loadAnimation(simulationId, options = {}) {
        try {
            this.utils.showProgress('Loading animation data...');
            
            // Get simulation results
            const results = await this.api.getSimulationResults(simulationId);
            
            if (!results.success) {
                throw new Error('Failed to load simulation results');
            }

            // Process animation data
            const animationData = this.processAnimationData(results.data, options);
            
            // Store animation data
            this.animationData = animationData;
            this.animationState.totalFrames = animationData.frames.length;
            this.animationState.currentFrame = 0;
            
            // Create animation instance
            const animationId = `animation_${simulationId}_${Date.now()}`;
            this.animations.set(animationId, {
                id: animationId,
                simulationId: simulationId,
                data: animationData,
                state: { ...this.animationState }
            });
            
            this.utils.hideProgress();
            this.utils.showSuccess('Animation data loaded successfully');
            
            // Trigger animation loaded event
            this.triggerEvent('animationLoaded', { animationId, data: animationData });
            
            return animationId;
            
        } catch (error) {
            this.utils.hideProgress();
            console.error('Error loading animation:', error);
            this.utils.handleError(error, 'PhysicsAnimation.loadAnimation');
            return null;
        }
    }

    /**
     * Process simulation data into animation frames
     */
    processAnimationData(simulationData, options = {}) {
        const { frameRate = 30, interpolation = 'linear', smoothing = true } = options;
        
        const animationData = {
            frames: [],
            metadata: {
                frameRate: frameRate,
                totalFrames: 0,
                duration: 0,
                interpolation: interpolation,
                smoothing: smoothing
            },
            keyframes: [],
            transitions: []
        };

        // Process time series data
        if (simulationData.time_series) {
            animationData.frames = this.processTimeSeriesToFrames(
                simulationData.time_series,
                frameRate,
                interpolation
            );
        }

        // Process scalar results
        if (simulationData.scalar_results) {
            animationData.frames = this.processScalarResultsToFrames(
                simulationData.scalar_results,
                frameRate
            );
        }

        // Apply smoothing if enabled
        if (smoothing && animationData.frames.length > 0) {
            animationData.frames = this.applySmoothing(animationData.frames, options);
        }

        // Extract keyframes
        animationData.keyframes = this.extractKeyframes(animationData.frames, options);
        
        // Generate transitions
        animationData.transitions = this.generateTransitions(animationData.keyframes, options);

        // Update metadata
        animationData.metadata.totalFrames = animationData.frames.length;
        animationData.metadata.duration = animationData.frames.length / frameRate;

        return animationData;
    }

    /**
     * Process time series data to animation frames
     */
    processTimeSeriesToFrames(timeSeries, frameRate, interpolation = 'linear') {
        if (!Array.isArray(timeSeries) || timeSeries.length === 0) {
            return [];
        }

        const frames = [];
        
        // Find time range
        const allTimes = timeSeries.flatMap(series => series.data.map(point => point.time));
        const startTime = Math.min(...allTimes);
        const endTime = Math.max(...allTimes);
        const duration = endTime - startTime;
        
        // Calculate frame interval
        const frameInterval = 1 / frameRate;
        const totalFrames = Math.ceil(duration * frameRate);
        
        // Generate frames
        for (let frameIndex = 0; frameIndex < totalFrames; frameIndex++) {
            const currentTime = startTime + (frameIndex * frameInterval);
            const frame = {
                frameIndex: frameIndex,
                time: currentTime,
                data: {},
                metadata: {
                    timestamp: currentTime,
                    progress: frameIndex / totalFrames
                }
            };
            
            // Interpolate values for each series
            timeSeries.forEach(series => {
                const interpolatedValue = this.interpolateValue(
                    series.data,
                    currentTime,
                    interpolation
                );
                frame.data[series.name] = interpolatedValue;
            });
            
            frames.push(frame);
        }

        return frames;
    }

    /**
     * Process scalar results to animation frames
     */
    processScalarResultsToFrames(scalarResults, frameRate) {
        if (!Array.isArray(scalarResults) || scalarResults.length === 0) {
            return [];
        }

        const frames = [];
        const totalFrames = Math.max(scalarResults.length, frameRate);
        
        for (let frameIndex = 0; frameIndex < totalFrames; frameIndex++) {
            const progress = frameIndex / totalFrames;
            const frame = {
                frameIndex: frameIndex,
                time: progress,
                data: {},
                metadata: {
                    timestamp: progress,
                    progress: progress
                }
            };
            
            // Interpolate scalar values
            scalarResults.forEach(result => {
                const interpolatedValue = this.interpolateScalarValue(
                    result,
                    progress,
                    totalFrames
                );
                frame.data[result.parameter] = interpolatedValue;
            });
            
            frames.push(frame);
        }

        return frames;
    }

    /**
     * Interpolate value at specific time
     */
    interpolateValue(data, targetTime, interpolation = 'linear') {
        if (!Array.isArray(data) || data.length === 0) return 0;
        
        // Find surrounding data points
        let before = null;
        let after = null;
        
        for (let i = 0; i < data.length; i++) {
            if (data[i].time <= targetTime) {
                before = data[i];
            } else {
                after = data[i];
                break;
            }
        }
        
        // Handle edge cases
        if (!before && !after) return 0;
        if (!before) return after.value;
        if (!after) return before.value;
        if (before.time === after.time) return before.value;
        
        // Interpolate based on method
        switch (interpolation) {
            case 'linear':
                return this.linearInterpolation(before, after, targetTime);
            case 'cubic':
                return this.cubicInterpolation(data, targetTime);
            case 'step':
                return before.value;
            default:
                return this.linearInterpolation(before, after, targetTime);
        }
    }

    /**
     * Linear interpolation
     */
    linearInterpolation(before, after, targetTime) {
        const t = (targetTime - before.time) / (after.time - before.time);
        return before.value + (after.value - before.value) * t;
    }

    /**
     * Cubic interpolation
     */
    cubicInterpolation(data, targetTime) {
        // Find four points for cubic interpolation
        const index = data.findIndex(point => point.time > targetTime);
        if (index < 2 || index >= data.length - 1) {
            return this.linearInterpolation(data[index - 1], data[index], targetTime);
        }
        
        const p0 = data[index - 2];
        const p1 = data[index - 1];
        const p2 = data[index];
        const p3 = data[index + 1];
        
        const t = (targetTime - p1.time) / (p2.time - p1.time);
        
        // Catmull-Rom spline
        const a0 = -0.5 * p0.value + 1.5 * p1.value - 1.5 * p2.value + 0.5 * p3.value;
        const a1 = p0.value - 2.5 * p1.value + 2 * p2.value - 0.5 * p3.value;
        const a2 = -0.5 * p0.value + 0.5 * p2.value;
        const a3 = p1.value;
        
        return a0 * Math.pow(t, 3) + a1 * Math.pow(t, 2) + a2 * t + a3;
    }

    /**
     * Interpolate scalar value
     */
    interpolateScalarValue(result, progress, totalFrames) {
        // For scalar results, we can create smooth transitions
        const value = result.value || 0;
        const variation = (result.variation || 0) * Math.sin(progress * Math.PI * 2);
        return value + variation;
    }

    /**
     * Apply smoothing to frames
     */
    applySmoothing(frames, options = {}) {
        const { smoothingFactor = 0.3, smoothingWindow = 3 } = options;
        
        if (frames.length < smoothingWindow) return frames;
        
        const smoothedFrames = [];
        
        for (let i = 0; i < frames.length; i++) {
            const smoothedFrame = { ...frames[i] };
            
            // Apply smoothing to each data series
            Object.keys(frames[i].data).forEach(seriesName => {
                const values = [];
                
                // Collect values in smoothing window
                for (let j = Math.max(0, i - smoothingWindow); j <= Math.min(frames.length - 1, i + smoothingWindow); j++) {
                    values.push(frames[j].data[seriesName]);
                }
                
                // Calculate smoothed value
                const average = values.reduce((sum, val) => sum + val, 0) / values.length;
                const currentValue = frames[i].data[seriesName];
                smoothedFrame.data[seriesName] = currentValue * (1 - smoothingFactor) + average * smoothingFactor;
            });
            
            smoothedFrames.push(smoothedFrame);
        }
        
        return smoothedFrames;
    }

    /**
     * Extract keyframes from animation
     */
    extractKeyframes(frames, options = {}) {
        const { keyframeThreshold = 0.1, maxKeyframes = 50 } = options;
        
        if (frames.length === 0) return [];
        
        const keyframes = [frames[0]]; // Always include first frame
        
        for (let i = 1; i < frames.length - 1; i++) {
            const frame = frames[i];
            const prevFrame = frames[i - 1];
            const nextFrame = frames[i + 1];
            
            let isKeyframe = false;
            
            // Check if this frame represents a significant change
            Object.keys(frame.data).forEach(seriesName => {
                const currentValue = frame.data[seriesName];
                const prevValue = prevFrame.data[seriesName];
                const nextValue = nextFrame.data[seriesName];
                
                const changeFromPrev = Math.abs(currentValue - prevValue);
                const changeToNext = Math.abs(nextValue - currentValue);
                
                if (changeFromPrev > keyframeThreshold || changeToNext > keyframeThreshold) {
                    isKeyframe = true;
                }
            });
            
            if (isKeyframe && keyframes.length < maxKeyframes) {
                keyframes.push(frame);
            }
        }
        
        keyframes.push(frames[frames.length - 1]); // Always include last frame
        
        return keyframes;
    }

    /**
     * Generate transitions between keyframes
     */
    generateTransitions(keyframes, options = {}) {
        const { transitionType = 'easeInOut', transitionDuration = 0.5 } = options;
        
        const transitions = [];
        
        for (let i = 0; i < keyframes.length - 1; i++) {
            const fromKeyframe = keyframes[i];
            const toKeyframe = keyframes[i + 1];
            
            transitions.push({
                from: fromKeyframe.frameIndex,
                to: toKeyframe.frameIndex,
                duration: (toKeyframe.frameIndex - fromKeyframe.frameIndex) / this.animationState.fps,
                type: transitionType,
                easing: this.getEasingFunction(transitionType)
            });
        }
        
        return transitions;
    }

    /**
     * Get easing function
     */
    getEasingFunction(type) {
        const easingFunctions = {
            linear: (t) => t,
            easeIn: (t) => t * t,
            easeOut: (t) => 1 - Math.pow(1 - t, 2),
            easeInOut: (t) => t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2,
            bounce: (t) => {
                if (t < 1 / 2.75) return 7.5625 * t * t;
                if (t < 2 / 2.75) return 7.5625 * (t -= 1.5 / 2.75) * t + 0.75;
                if (t < 2.5 / 2.75) return 7.5625 * (t -= 2.25 / 2.75) * t + 0.9375;
                return 7.5625 * (t -= 2.625 / 2.75) * t + 0.984375;
            }
        };
        
        return easingFunctions[type] || easingFunctions.linear;
    }

    /**
     * Play animation
     */
    play(animationId = null) {
        if (animationId && !this.animations.has(animationId)) {
            console.error(`Animation not found: ${animationId}`);
            return;
        }

        this.animationState.isPlaying = true;
        this.animationState.isPaused = false;
        
        // Trigger play event
        this.triggerEvent('play', { animationId, state: this.animationState });
        
        console.log('Animation started');
    }

    /**
     * Pause animation
     */
    pause(animationId = null) {
        this.animationState.isPaused = true;
        
        // Trigger pause event
        this.triggerEvent('pause', { animationId, state: this.animationState });
        
        console.log('Animation paused');
    }

    /**
     * Stop animation
     */
    stop(animationId = null) {
        this.animationState.isPlaying = false;
        this.animationState.isPaused = false;
        this.animationState.currentFrame = 0;
        
        // Trigger stop event
        this.triggerEvent('stop', { animationId, state: this.animationState });
        
        console.log('Animation stopped');
    }

    /**
     * Seek to specific frame
     */
    seekToFrame(frameIndex, animationId = null) {
        const clampedFrame = Math.max(0, Math.min(frameIndex, this.animationState.totalFrames - 1));
        this.animationState.currentFrame = clampedFrame;
        
        // Trigger frame update event
        this.triggerEvent('frameUpdate', { 
            animationId, 
            frameIndex: clampedFrame,
            frame: this.animationData.frames[clampedFrame]
        });
        
        console.log(`Seeked to frame ${clampedFrame}`);
    }

    /**
     * Seek to specific time
     */
    seekToTime(time, animationId = null) {
        if (this.animationData.frames.length === 0) return;
        
        // Find frame closest to target time
        const targetFrame = this.animationData.frames.findIndex(frame => frame.time >= time);
        const frameIndex = targetFrame >= 0 ? targetFrame : this.animationData.frames.length - 1;
        
        this.seekToFrame(frameIndex, animationId);
    }

    /**
     * Set animation speed
     */
    setSpeed(speed, animationId = null) {
        this.animationState.speed = Math.max(0.1, Math.min(5.0, speed));
        
        console.log(`Animation speed set to ${this.animationState.speed}x`);
    }

    /**
     * Set animation direction
     */
    setDirection(direction, animationId = null) {
        if (direction === 'forward' || direction === 'reverse') {
            this.animationState.direction = direction;
            console.log(`Animation direction set to ${direction}`);
        }
    }

    /**
     * Toggle loop
     */
    toggleLoop(animationId = null) {
        this.animationState.loop = !this.animationState.loop;
        console.log(`Animation loop ${this.animationState.loop ? 'enabled' : 'disabled'}`);
    }

    /**
     * Update animation
     */
    updateAnimation(currentTime) {
        if (this.animationData.frames.length === 0) return;
        
        // Calculate delta time
        const deltaTime = currentTime - this.lastFrameTime;
        this.lastFrameTime = currentTime;
        
        // Update frame based on speed and FPS
        const frameAdvance = (deltaTime / 1000) * this.animationState.fps * this.animationState.speed;
        
        if (this.animationState.direction === 'forward') {
            this.animationState.currentFrame += frameAdvance;
        } else {
            this.animationState.currentFrame -= frameAdvance;
        }
        
        // Handle loop and bounds
        if (this.animationState.currentFrame >= this.animationState.totalFrames) {
            if (this.animationState.loop) {
                this.animationState.currentFrame = 0;
            } else {
                this.animationState.currentFrame = this.animationState.totalFrames - 1;
                this.stop();
                this.triggerEvent('complete', { state: this.animationState });
                return;
            }
        } else if (this.animationState.currentFrame < 0) {
            if (this.animationState.loop) {
                this.animationState.currentFrame = this.animationState.totalFrames - 1;
            } else {
                this.animationState.currentFrame = 0;
                this.stop();
                this.triggerEvent('complete', { state: this.animationState });
                return;
            }
        }
        
        // Get current frame
        const frameIndex = Math.floor(this.animationState.currentFrame);
        const frame = this.animationData.frames[frameIndex];
        
        if (frame) {
            // Trigger frame update event
            this.triggerEvent('frameUpdate', { 
                frameIndex: frameIndex,
                frame: frame,
                progress: frameIndex / this.animationState.totalFrames
            });
        }
        
        // Update performance metrics
        this.updatePerformanceMetrics();
    }

    /**
     * Update performance metrics
     */
    updatePerformanceMetrics() {
        this.performance.frameCount++;
        
        const now = Date.now();
        const timeDiff = now - this.performance.lastUpdate;
        
        if (timeDiff >= 1000) { // Update every second
            this.performance.averageFPS = this.performance.frameCount / (timeDiff / 1000);
            this.performance.frameCount = 0;
            this.performance.lastUpdate = now;
        }
    }

    /**
     * Add event listener
     */
    addEventListener(event, callback) {
        if (!this.eventListeners.has(event)) {
            this.eventListeners.set(event, []);
        }
        this.eventListeners.get(event).push(callback);
    }

    /**
     * Remove event listener
     */
    removeEventListener(event, callback) {
        if (this.eventListeners.has(event)) {
            const listeners = this.eventListeners.get(event);
            const index = listeners.indexOf(callback);
            if (index > -1) {
                listeners.splice(index, 1);
            }
        }
    }

    /**
     * Trigger event
     */
    triggerEvent(event, data = {}) {
        if (this.eventListeners.has(event)) {
            this.eventListeners.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in animation event listener for ${event}:`, error);
                }
            });
        }
    }

    /**
     * Get current animation state
     */
    getAnimationState() {
        return { ...this.animationState };
    }

    /**
     * Get animation data
     */
    getAnimationData() {
        return { ...this.animationData };
    }

    /**
     * Get performance metrics
     */
    getPerformanceMetrics() {
        return { ...this.performance };
    }

    /**
     * Get animation instance
     */
    getAnimation(animationId) {
        return this.animations.get(animationId);
    }

    /**
     * Get all animations
     */
    getAllAnimations() {
        return Array.from(this.animations.keys());
    }

    /**
     * Dispose of animation
     */
    dispose(animationId = null) {
        if (animationId) {
            this.animations.delete(animationId);
        } else {
            this.animations.clear();
        }
        
        if (this.animationLoop) {
            cancelAnimationFrame(this.animationLoop);
            this.animationLoop = null;
        }
        
        this.eventListeners.clear();
        
        console.log('Animation disposed');
    }
}

// Export the animation class
export default PhysicsAnimation; 