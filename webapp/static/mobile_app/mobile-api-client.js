/**
 * Mobile API Client for AASX Digital Twin Analytics
 * Optimized for mobile devices with offline support
 */

class MobileAPIClient {
    constructor() {
        this.baseURL = window.location.origin;
        this.timeout = 30000; // 30 seconds for mobile
        this.retryAttempts = 3;
        this.retryDelay = 1000;
        
        // Cache for offline support
        this.cache = new Map();
        this.offlineQueue = [];
        
        // Mobile-specific headers
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            'X-Mobile-App': 'true',
            'X-App-Version': '1.0.0'
        };
        
        this.init();
    }

    init() {
        console.log('📱 Mobile API Client: Initializing...');
        
        // Setup offline detection
        this.setupOfflineDetection();
        
        // Setup request interceptors
        this.setupInterceptors();
        
        // Process offline queue when back online
        this.setupOfflineQueue();
        
        console.log('✅ Mobile API Client: Initialized');
    }

    setupOfflineDetection() {
        window.addEventListener('online', () => {
            console.log('📱 Mobile API: Back online');
            this.processOfflineQueue();
        });

        window.addEventListener('offline', () => {
            console.log('📱 Mobile API: Going offline');
        });
    }

    setupInterceptors() {
        // Add authentication headers
        this.addAuthHeaders = (headers) => {
            if (window.authManager && window.authManager.authToken) {
                headers['Authorization'] = `Bearer ${window.authManager.authToken}`;
            }
            return headers;
        };
    }

    setupOfflineQueue() {
        // Process queued requests when back online
        if (navigator.onLine) {
            this.processOfflineQueue();
        }
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const method = options.method || 'GET';
        
        // Prepare headers
        const headers = {
            ...this.defaultHeaders,
            ...options.headers
        };
        
        // Add auth headers
        this.addAuthHeaders(headers);
        
        // Prepare request config
        const config = {
            method,
            headers,
            timeout: this.timeout,
            ...options
        };

        // Check cache for GET requests
        if (method === 'GET' && this.cache.has(url)) {
            const cached = this.cache.get(url);
            if (Date.now() - cached.timestamp < 5 * 60 * 1000) { // 5 minutes
                console.log('📱 Mobile API: Serving from cache:', endpoint);
                return cached.data;
            }
        }

        try {
            // Try network request
            const response = await this.makeRequest(url, config);
            
            // Cache successful GET responses
            if (method === 'GET' && response.ok) {
                const data = await response.json();
                this.cache.set(url, {
                    data,
                    timestamp: Date.now()
                });
                return data;
            }
            
            return response;
        } catch (error) {
            console.error('📱 Mobile API: Request failed:', error);
            
            // If offline, queue the request
            if (!navigator.onLine) {
                return this.queueOfflineRequest(url, config);
            }
            
            // Retry on network errors
            return this.retryRequest(url, config, error);
        }
    }

    async makeRequest(url, config) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), config.timeout);
        
        try {
            const response = await fetch(url, {
                ...config,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return response;
        } catch (error) {
            clearTimeout(timeoutId);
            throw error;
        }
    }

    async retryRequest(url, config, originalError, attempt = 1) {
        if (attempt >= this.retryAttempts) {
            throw originalError;
        }
        
        console.log(`📱 Mobile API: Retrying request (${attempt}/${this.retryAttempts})`);
        
        await new Promise(resolve => setTimeout(resolve, this.retryDelay * attempt));
        
        try {
            return await this.makeRequest(url, config);
        } catch (error) {
            return this.retryRequest(url, config, error, attempt + 1);
        }
    }

    queueOfflineRequest(url, config) {
        const request = {
            url,
            config,
            timestamp: Date.now(),
            id: Date.now() + Math.random()
        };
        
        this.offlineQueue.push(request);
        
        // Store in localStorage for persistence
        this.saveOfflineQueue();
        
        console.log('📱 Mobile API: Request queued for offline processing');
        
        return Promise.resolve({
            ok: false,
            status: 503,
            statusText: 'Service Unavailable (Offline)',
            data: {
                error: 'offline',
                message: 'Request queued for when you\'re back online',
                queued: true,
                queueId: request.id
            }
        });
    }

    async processOfflineQueue() {
        if (this.offlineQueue.length === 0) {
            return;
        }
        
        console.log(`📱 Mobile API: Processing ${this.offlineQueue.length} queued requests`);
        
        const queue = [...this.offlineQueue];
        this.offlineQueue = [];
        
        for (const request of queue) {
            try {
                await this.makeRequest(request.url, request.config);
                console.log('📱 Mobile API: Queued request processed successfully');
            } catch (error) {
                console.error('📱 Mobile API: Failed to process queued request:', error);
                // Re-queue failed requests
                this.offlineQueue.push(request);
            }
        }
        
        this.saveOfflineQueue();
    }

    saveOfflineQueue() {
        try {
            localStorage.setItem('mobile_offline_queue', JSON.stringify(this.offlineQueue));
        } catch (error) {
            console.error('📱 Mobile API: Failed to save offline queue:', error);
        }
    }

    loadOfflineQueue() {
        try {
            const saved = localStorage.getItem('mobile_offline_queue');
            if (saved) {
                this.offlineQueue = JSON.parse(saved);
            }
        } catch (error) {
            console.error('📱 Mobile API: Failed to load offline queue:', error);
        }
    }

    // API Methods for different modules
    async getDashboard() {
        return this.request('/api/dashboard');
    }

    async getTwinRegistry() {
        return this.request('/api/twin-registry');
    }

    async getAIRAG() {
        return this.request('/api/ai-rag');
    }

    async getCertificates() {
        return this.request('/api/certificate-manager');
    }

    async getFederatedLearning() {
        return this.request('/api/federated-learning');
    }

    async getPhysicsModeling() {
        return this.request('/api/physics-modeling');
    }

    async getHealth() {
        return this.request('/api/health');
    }

    // File upload with progress tracking
    async uploadFile(endpoint, file, onProgress) {
        const formData = new FormData();
        formData.append('file', file);
        
        const headers = {
            ...this.defaultHeaders
        };
        delete headers['Content-Type']; // Let browser set for FormData
        
        this.addAuthHeaders(headers);
        
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable && onProgress) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    onProgress(percentComplete);
                }
            });
            
            xhr.addEventListener('load', () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        resolve(response);
                    } catch (error) {
                        resolve(xhr.responseText);
                    }
                } else {
                    reject(new Error(`Upload failed: ${xhr.status}`));
                }
            });
            
            xhr.addEventListener('error', () => {
                reject(new Error('Upload failed'));
            });
            
            xhr.open('POST', `${this.baseURL}${endpoint}`);
            
            // Add headers
            Object.keys(headers).forEach(key => {
                xhr.setRequestHeader(key, headers[key]);
            });
            
            xhr.send(formData);
        });
    }

    // Batch requests for mobile optimization
    async batchRequests(requests) {
        const promises = requests.map(req => 
            this.request(req.endpoint, req.options)
        );
        
        return Promise.allSettled(promises);
    }

    // Clear cache
    clearCache() {
        this.cache.clear();
        console.log('📱 Mobile API: Cache cleared');
    }

    // Get cache stats
    getCacheStats() {
        return {
            size: this.cache.size,
            entries: Array.from(this.cache.keys())
        };
    }

    // Get offline queue stats
    getOfflineQueueStats() {
        return {
            pending: this.offlineQueue.length,
            requests: this.offlineQueue.map(req => ({
                url: req.url,
                timestamp: req.timestamp,
                age: Date.now() - req.timestamp
            }))
        };
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.mobileAPIClient = new MobileAPIClient();
});

// Export for global access
window.MobileAPIClient = MobileAPIClient;
