/**
 * 3D Viewer Module
 * Handles 3D visualization of physics models using Three.js
 */

import PhysicsModelingAPI from '../../shared/api.js';
import PhysicsModelingUtils from '../../shared/utils.js';

class ThreeDViewer {
    constructor(containerId = '3d-viewer-container') {
        this.containerId = containerId;
        this.container = null;
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.currentModel = null;
        this.animationId = null;
        this.isInitialized = false;
        
        this.api = new PhysicsModelingAPI();
        this.utils = new PhysicsModelingUtils();
        
        // Scene objects
        this.modelGroup = null;
        this.gridHelper = null;
        this.axesHelper = null;
        this.lights = [];
        
        // Animation state
        this.animationState = {
            isPlaying: false,
            currentFrame: 0,
            totalFrames: 0,
            speed: 1.0
        };
        
        this.init();
    }

    /**
     * Initialize the 3D viewer
     */
    async init() {
        try {
            console.log('Initializing 3D Viewer...');
            
            // Get container
            this.container = document.getElementById(this.containerId);
            if (!this.container) {
                throw new Error(`Container with ID '${this.containerId}' not found`);
            }

            // Initialize Three.js components
            this.initScene();
            this.initCamera();
            this.initRenderer();
            this.initControls();
            this.initLights();
            this.initHelpers();
            this.initEventListeners();
            
            // Start render loop
            this.animate();
            
            this.isInitialized = true;
            console.log('3D Viewer initialized successfully');
            
        } catch (error) {
            console.error('Error initializing 3D Viewer:', error);
            this.utils.handleError(error, 'ThreeDViewer.init');
        }
    }

    /**
     * Initialize Three.js scene
     */
    initScene() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x1a1a1a);
        this.scene.fog = new THREE.Fog(0x1a1a1a, 10, 100);
        
        // Create model group
        this.modelGroup = new THREE.Group();
        this.scene.add(this.modelGroup);
    }

    /**
     * Initialize camera
     */
    initCamera() {
        const aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000);
        this.camera.position.set(10, 10, 10);
        this.camera.lookAt(0, 0, 0);
    }

    /**
     * Initialize renderer
     */
    initRenderer() {
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true,
            alpha: true,
            preserveDrawingBuffer: true
        });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.outputEncoding = THREE.sRGBEncoding;
        
        this.container.appendChild(this.renderer.domElement);
    }

    /**
     * Initialize camera controls
     */
    initControls() {
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.screenSpacePanning = false;
        this.controls.minDistance = 1;
        this.controls.maxDistance = 100;
        this.controls.maxPolarAngle = Math.PI;
    }

    /**
     * Initialize lighting
     */
    initLights() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        this.scene.add(ambientLight);
        this.lights.push(ambientLight);

        // Directional light (sun)
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 5);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        this.scene.add(directionalLight);
        this.lights.push(directionalLight);

        // Point light for highlights
        const pointLight = new THREE.PointLight(0xffffff, 0.5, 100);
        pointLight.position.set(-10, 10, -10);
        this.scene.add(pointLight);
        this.lights.push(pointLight);
    }

    /**
     * Initialize scene helpers
     */
    initHelpers() {
        // Grid helper
        this.gridHelper = new THREE.GridHelper(20, 20, 0x444444, 0x222222);
        this.scene.add(this.gridHelper);

        // Axes helper
        this.axesHelper = new THREE.AxesHelper(5);
        this.scene.add(this.axesHelper);
    }

    /**
     * Initialize event listeners
     */
    initEventListeners() {
        // Window resize
        window.addEventListener('resize', () => this.onWindowResize());

        // Container resize observer
        const resizeObserver = new ResizeObserver(() => this.onWindowResize());
        resizeObserver.observe(this.container);
    }

    /**
     * Handle window resize
     */
    onWindowResize() {
        if (!this.container || !this.camera || !this.renderer) return;

        const width = this.container.clientWidth;
        const height = this.container.clientHeight;

        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }

    /**
     * Load a physics model for visualization
     */
    async loadModel(modelId) {
        try {
            this.utils.showProgress('Loading 3D model...');
            
            // Get model data
            const modelData = await this.api.getModel(modelId);
            
            if (!modelData.success) {
                throw new Error('Failed to load model data');
            }

            // Clear existing model
            this.clearModel();
            
            // Create 3D representation
            await this.createModelGeometry(modelData.data);
            
            // Store current model
            this.currentModel = modelData.data;
            
            // Center camera on model
            this.centerCameraOnModel();
            
            this.utils.hideProgress();
            this.utils.showSuccess('3D model loaded successfully');
            
            // Trigger model loaded event
            this.triggerEvent('modelLoaded', { model: modelData.data });
            
        } catch (error) {
            this.utils.hideProgress();
            console.error('Error loading 3D model:', error);
            this.utils.handleError(error, 'ThreeDViewer.loadModel');
        }
    }

    /**
     * Create 3D geometry from model data
     */
    async createModelGeometry(modelData) {
        const geometry = modelData.geometry || {};
        const material = modelData.material || {};
        
        let mesh = null;

        // Create geometry based on type
        switch (geometry.type) {
            case 'box':
                mesh = this.createBoxGeometry(geometry, material);
                break;
            case 'sphere':
                mesh = this.createSphereGeometry(geometry, material);
                break;
            case 'cylinder':
                mesh = this.createCylinderGeometry(geometry, material);
                break;
            case 'custom':
                mesh = await this.createCustomGeometry(geometry, material);
                break;
            default:
                // Default to a simple box
                mesh = this.createBoxGeometry(geometry, material);
        }

        if (mesh) {
            // Apply transformations
            if (geometry.position) {
                mesh.position.set(geometry.position.x || 0, geometry.position.y || 0, geometry.position.z || 0);
            }
            if (geometry.rotation) {
                mesh.rotation.set(geometry.rotation.x || 0, geometry.rotation.y || 0, geometry.rotation.z || 0);
            }
            if (geometry.scale) {
                mesh.scale.set(geometry.scale.x || 1, geometry.scale.y || 1, geometry.scale.z || 1);
            }

            // Add to model group
            this.modelGroup.add(mesh);
        }
    }

    /**
     * Create box geometry
     */
    createBoxGeometry(geometry, material) {
        const boxGeometry = new THREE.BoxGeometry(
            geometry.width || 1,
            geometry.height || 1,
            geometry.depth || 1
        );
        
        const boxMaterial = new THREE.MeshPhongMaterial({
            color: material.color || 0x00ff00,
            transparent: true,
            opacity: material.opacity || 1.0,
            wireframe: material.wireframe || false
        });
        
        return new THREE.Mesh(boxGeometry, boxMaterial);
    }

    /**
     * Create sphere geometry
     */
    createSphereGeometry(geometry, material) {
        const sphereGeometry = new THREE.SphereGeometry(
            geometry.radius || 0.5,
            geometry.widthSegments || 32,
            geometry.heightSegments || 16
        );
        
        const sphereMaterial = new THREE.MeshPhongMaterial({
            color: material.color || 0x00ff00,
            transparent: true,
            opacity: material.opacity || 1.0,
            wireframe: material.wireframe || false
        });
        
        return new THREE.Mesh(sphereGeometry, sphereMaterial);
    }

    /**
     * Create cylinder geometry
     */
    createCylinderGeometry(geometry, material) {
        const cylinderGeometry = new THREE.CylinderGeometry(
            geometry.radiusTop || 0.5,
            geometry.radiusBottom || 0.5,
            geometry.height || 1,
            geometry.radialSegments || 32
        );
        
        const cylinderMaterial = new THREE.MeshPhongMaterial({
            color: material.color || 0x00ff00,
            transparent: true,
            opacity: material.opacity || 1.0,
            wireframe: material.wireframe || false
        });
        
        return new THREE.Mesh(cylinderGeometry, cylinderMaterial);
    }

    /**
     * Create custom geometry from mesh data
     */
    async createCustomGeometry(geometry, material) {
        // This would handle custom mesh data (vertices, faces, etc.)
        // For now, return a simple placeholder
        return this.createBoxGeometry({ width: 1, height: 1, depth: 1 }, material);
    }

    /**
     * Clear current model
     */
    clearModel() {
        if (this.modelGroup) {
            this.modelGroup.clear();
        }
        this.currentModel = null;
    }

    /**
     * Center camera on loaded model
     */
    centerCameraOnModel() {
        if (!this.modelGroup || this.modelGroup.children.length === 0) return;

        const box = new THREE.Box3().setFromObject(this.modelGroup);
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        
        const maxDim = Math.max(size.x, size.y, size.z);
        const fov = this.camera.fov * (Math.PI / 180);
        let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));
        
        cameraZ *= 1.5; // Add some padding
        
        this.camera.position.set(center.x + cameraZ, center.y + cameraZ, center.z + cameraZ);
        this.camera.lookAt(center);
        this.controls.target.copy(center);
        this.controls.update();
    }

    /**
     * Start animation playback
     */
    startAnimation() {
        if (this.animationState.isPlaying) return;
        
        this.animationState.isPlaying = true;
        this.animationState.currentFrame = 0;
        
        this.utils.showSuccess('Animation started');
        this.triggerEvent('animationStarted');
    }

    /**
     * Stop animation playback
     */
    stopAnimation() {
        this.animationState.isPlaying = false;
        this.utils.showSuccess('Animation stopped');
        this.triggerEvent('animationStopped');
    }

    /**
     * Set animation speed
     */
    setAnimationSpeed(speed) {
        this.animationState.speed = Math.max(0.1, Math.min(5.0, speed));
    }

    /**
     * Update animation frame
     */
    updateAnimation() {
        if (!this.animationState.isPlaying || !this.currentModel) return;

        // Update animation frame
        this.animationState.currentFrame += this.animationState.speed;
        
        if (this.animationState.currentFrame >= this.animationState.totalFrames) {
            this.animationState.currentFrame = 0;
        }

        // Apply animation to model
        this.applyAnimationFrame(this.animationState.currentFrame);
    }

    /**
     * Apply animation frame to model
     */
    applyAnimationFrame(frame) {
        if (!this.modelGroup || !this.currentModel.animation) return;

        // Apply transformations based on animation data
        const animationData = this.currentModel.animation[Math.floor(frame)];
        if (animationData) {
            this.modelGroup.children.forEach(child => {
                if (animationData.position) {
                    child.position.set(
                        animationData.position.x || 0,
                        animationData.position.y || 0,
                        animationData.position.z || 0
                    );
                }
                if (animationData.rotation) {
                    child.rotation.set(
                        animationData.rotation.x || 0,
                        animationData.rotation.y || 0,
                        animationData.rotation.z || 0
                    );
                }
            });
        }
    }

    /**
     * Take screenshot of current view
     */
    takeScreenshot() {
        if (!this.renderer) return null;

        this.renderer.render(this.scene, this.camera);
        return this.renderer.domElement.toDataURL('image/png');
    }

    /**
     * Export model as GLTF
     */
    async exportModel(format = 'gltf') {
        if (!this.modelGroup) {
            this.utils.showError('No model to export');
            return;
        }

        try {
            this.utils.showProgress('Exporting model...');
            
            // Use Three.js GLTFExporter
            const { GLTFExporter } = await import('three/examples/jsm/exporters/GLTFExporter.js');
            const exporter = new GLTFExporter();
            
            const result = await new Promise((resolve, reject) => {
                exporter.parse(this.modelGroup, resolve, reject, {
                    binary: format === 'glb',
                    includeCustomExtensions: true
                });
            });

            // Create download link
            const blob = new Blob([result], { type: 'application/octet-stream' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `physics_model.${format}`;
            link.click();
            
            URL.revokeObjectURL(url);
            this.utils.hideProgress();
            this.utils.showSuccess('Model exported successfully');
            
        } catch (error) {
            this.utils.hideProgress();
            console.error('Error exporting model:', error);
            this.utils.handleError(error, 'ThreeDViewer.exportModel');
        }
    }

    /**
     * Toggle wireframe mode
     */
    toggleWireframe() {
        if (!this.modelGroup) return;

        this.modelGroup.children.forEach(child => {
            if (child.material) {
                child.material.wireframe = !child.material.wireframe;
            }
        });
    }

    /**
     * Toggle grid visibility
     */
    toggleGrid() {
        if (this.gridHelper) {
            this.gridHelper.visible = !this.gridHelper.visible;
        }
    }

    /**
     * Toggle axes visibility
     */
    toggleAxes() {
        if (this.axesHelper) {
            this.axesHelper.visible = !this.axesHelper.visible;
        }
    }

    /**
     * Set background color
     */
    setBackgroundColor(color) {
        if (this.scene) {
            this.scene.background = new THREE.Color(color);
        }
    }

    /**
     * Trigger custom event
     */
    triggerEvent(eventName, data = {}) {
        const event = new CustomEvent(`3dviewer:${eventName}`, {
            detail: { viewer: this, ...data }
        });
        document.dispatchEvent(event);
    }

    /**
     * Animation loop
     */
    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());
        
        // Update controls
        if (this.controls) {
            this.controls.update();
        }
        
        // Update animation
        this.updateAnimation();
        
        // Render scene
        if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
        }
    }

    /**
     * Dispose of resources
     */
    dispose() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        
        if (this.renderer) {
            this.renderer.dispose();
        }
        
        if (this.controls) {
            this.controls.dispose();
        }
        
        // Clear scene
        if (this.scene) {
            this.scene.clear();
        }
        
        this.isInitialized = false;
    }

    /**
     * Get current model
     */
    getCurrentModel() {
        return this.currentModel;
    }

    /**
     * Get animation state
     */
    getAnimationState() {
        return { ...this.animationState };
    }

    /**
     * Get camera position
     */
    getCameraPosition() {
        return this.camera ? this.camera.position.clone() : null;
    }

    /**
     * Set camera position
     */
    setCameraPosition(position) {
        if (this.camera) {
            this.camera.position.copy(position);
            this.controls.update();
        }
    }
}

// Export the 3D viewer class
export default ThreeDViewer; 