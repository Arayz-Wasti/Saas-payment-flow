/**
 * API Wrapper for SaaS Backend
 */

const API_BASE = 'https://saas-payment-flow-production.up.railway.app/api';

const api = {
    /**
     * Helper to show alert messages in the UI
     */
    showAlert(type, message) {
        const el = document.getElementById(`alert-${type}`);
        if (el) {
            el.textContent = message;
            el.style.display = 'block';
            setTimeout(() => {
                el.style.display = 'none';
            }, 5000);
        } else {
            alert(message);
        }
    },

    /**
     * Execute HTTP request with JWT token handling
     */
    async request(endpoint, options = {}, isRetry = false) {
        const url = `${API_BASE}${endpoint}`;

        let headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            ...(options.headers || {})
        };

        const token = localStorage.getItem('access_token');
        if (token && !options.noAuth) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const config = {
            ...options,
            headers,
        };

        if (config.body && typeof config.body === 'object') {
            config.body = JSON.stringify(config.body);
        }

        try {
            const response = await fetch(url, config);

            // Handle 401 Unauthorized (Token might be expired)
            if (response.status === 401 && !isRetry && token) {
                const refreshed = await this.refreshToken();
                if (refreshed) {
                    // Retry original request
                    return this.request(endpoint, options, true);
                } else {
                    this.logout();
                    window.location.href = '/login.html';
                    throw new Error('Session expired. Please log in again.');
                }
            }

            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                const errorMsg = data.detail || data.error || data.email?.[0] || 'An error occurred';
                throw new Error(errorMsg);
            }

            return data;
        } catch (error) {
            throw error;
        }
    },

    /**
     * Attempt to refresh the JWT access token
     */
    async refreshToken() {
        const refresh = localStorage.getItem('refresh_token');
        if (!refresh) return false;

        try {
            const res = await fetch(`${API_BASE}/users/token/refresh/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh })
            });

            if (res.ok) {
                const data = await res.json();
                localStorage.setItem('access_token', data.access);
                if (data.refresh) localStorage.setItem('refresh_token', data.refresh);
                return true;
            }
            return false;
        } catch (e) {
            return false;
        }
    },

    // --- User Endpoints ---

    async login(email, password) {
        const data = await this.request('/users/token/', {
            method: 'POST',
            body: { email, password },
            noAuth: true
        });
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);
        return data;
    },

    async register(email, password, company_name) {
        return this.request('/users/register/', {
            method: 'POST',
            body: { email, password, company_name },
            noAuth: true
        });
    },

    logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    },

    async getUserProfile() {
        return this.request('/users/me/', { method: 'GET' });
    },

    isAuthenticated() {
        return !!localStorage.getItem('access_token');
    },

    // --- Subscription & Payment Endpoints ---

    async createCheckoutSession(planId) {
        return this.request('/payments/checkout/', {
            method: 'POST',
            body: { plan_id: planId }
        });
    },

    async createBillingPortal() {
        return this.request('/payments/portal/', {
            method: 'POST'
        });
    },

    // --- Dashboard Data ---

    async getPremiumData() {
        return this.request('/dashboard/premium-data/', { method: 'GET' });
    },

    async verifyCheckout(sessionId) {
        return this.request('/payments/verify-checkout/', {
            method: 'POST',
            body: { session_id: sessionId }
        });
    },

    async getSubscriptionStatus() {
        return this.request('/payments/subscription-status/', { method: 'GET' });
    }
};

window.api = api;
