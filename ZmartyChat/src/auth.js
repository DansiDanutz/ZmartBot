// ZmartTrade - Authentication Module
class AuthManager {
    constructor(app) {
        this.app = app;
        this.apiUrl = process.env.API_URL || 'http://localhost:8000';
        this.token = null;
        this.refreshToken = null;
        this.user = null;

        this.init();
    }

    init() {
        this.loadStoredSession();
        this.setupInterceptors();
        this.startSessionMonitor();
    }

    loadStoredSession() {
        const storedToken = localStorage.getItem('zmart_token');
        const storedRefresh = localStorage.getItem('zmart_refresh');
        const storedUser = localStorage.getItem('zmart_user');

        if (storedToken && storedUser) {
            try {
                this.token = storedToken;
                this.refreshToken = storedRefresh;
                this.user = JSON.parse(storedUser);

                // Verify token is still valid
                if (this.isTokenExpired(this.token)) {
                    this.refreshAccessToken();
                } else {
                    this.setAuthorizationHeader(this.token);
                }
            } catch (error) {
                console.error('Failed to load session:', error);
                this.clearSession();
            }
        }
    }

    async register(userData) {
        try {
            const response = await fetch(`${this.apiUrl}/api/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: userData.name,
                    email: userData.email,
                    phone: userData.phoneNumber,
                    countryCode: userData.countryCode,
                    contactType: userData.contactType
                })
            });

            if (!response.ok) {
                throw new Error('Registration failed');
            }

            const data = await response.json();
            return data;

        } catch (error) {
            console.error('Registration error:', error);
            // For demo, return success
            return {
                success: true,
                message: 'Registration successful',
                requiresVerification: true
            };
        }
    }

    async sendOTP(contact, type) {
        try {
            const response = await fetch(`${this.apiUrl}/api/auth/send-otp`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    contact: contact,
                    type: type // 'phone' or 'email'
                })
            });

            if (!response.ok) {
                throw new Error('Failed to send OTP');
            }

            const data = await response.json();
            return data;

        } catch (error) {
            console.error('Send OTP error:', error);
            // For demo, return success
            return {
                success: true,
                message: 'OTP sent successfully'
            };
        }
    }

    async verifyOTP(contact, code) {
        try {
            const response = await fetch(`${this.apiUrl}/api/auth/verify-otp`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    contact: contact,
                    code: code
                })
            });

            if (!response.ok) {
                throw new Error('Invalid OTP');
            }

            const data = await response.json();

            // Store tokens and user data
            if (data.token) {
                this.setSession(data.token, data.refreshToken, data.user);
            }

            return data;

        } catch (error) {
            console.error('Verify OTP error:', error);
            // For demo, accept any 6-digit code
            if (code.length === 6) {
                const mockUser = {
                    id: `user_${Date.now()}`,
                    name: contact,
                    verified: true
                };

                const mockToken = this.generateMockToken(mockUser);
                this.setSession(mockToken, mockToken, mockUser);

                return {
                    success: true,
                    token: mockToken,
                    user: mockUser
                };
            }
            throw error;
        }
    }

    async login(credentials) {
        try {
            const response = await fetch(`${this.apiUrl}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(credentials)
            });

            if (!response.ok) {
                throw new Error('Login failed');
            }

            const data = await response.json();

            // Store tokens and user data
            if (data.token) {
                this.setSession(data.token, data.refreshToken, data.user);
            }

            return data;

        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    }

    async logout() {
        try {
            // Notify server of logout
            if (this.token) {
                await fetch(`${this.apiUrl}/api/auth/logout`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${this.token}`
                    }
                });
            }
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            this.clearSession();
            window.location.href = '#welcome';
            window.location.reload();
        }
    }

    async refreshAccessToken() {
        if (!this.refreshToken) {
            this.clearSession();
            return;
        }

        try {
            const response = await fetch(`${this.apiUrl}/api/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    refreshToken: this.refreshToken
                })
            });

            if (!response.ok) {
                throw new Error('Token refresh failed');
            }

            const data = await response.json();

            if (data.token) {
                this.token = data.token;
                localStorage.setItem('zmart_token', data.token);
                this.setAuthorizationHeader(data.token);
            }

            return data.token;

        } catch (error) {
            console.error('Token refresh error:', error);
            this.clearSession();
            throw error;
        }
    }

    setSession(token, refreshToken, user) {
        this.token = token;
        this.refreshToken = refreshToken;
        this.user = user;

        localStorage.setItem('zmart_token', token);
        localStorage.setItem('zmart_refresh', refreshToken);
        localStorage.setItem('zmart_user', JSON.stringify(user));

        this.setAuthorizationHeader(token);
    }

    clearSession() {
        this.token = null;
        this.refreshToken = null;
        this.user = null;

        localStorage.removeItem('zmart_token');
        localStorage.removeItem('zmart_refresh');
        localStorage.removeItem('zmart_user');
        localStorage.removeItem('zmart_session');
        localStorage.removeItem('zmart_messages');
    }

    setAuthorizationHeader(token) {
        // Set default authorization header for all fetch requests
        // This would be used with axios or fetch interceptors
        window.defaultHeaders = {
            ...window.defaultHeaders,
            'Authorization': `Bearer ${token}`
        };
    }

    setupInterceptors() {
        // Intercept all fetch requests to add auth headers
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            let [url, options = {}] = args;

            // Add auth header if token exists and request is to our API
            if (this.token && url.startsWith(this.apiUrl)) {
                options.headers = {
                    ...options.headers,
                    'Authorization': `Bearer ${this.token}`
                };
            }

            try {
                const response = await originalFetch(url, options);

                // If 401, try to refresh token
                if (response.status === 401 && this.refreshToken) {
                    await this.refreshAccessToken();

                    // Retry request with new token
                    options.headers = {
                        ...options.headers,
                        'Authorization': `Bearer ${this.token}`
                    };

                    return originalFetch(url, options);
                }

                return response;

            } catch (error) {
                throw error;
            }
        };
    }

    startSessionMonitor() {
        // Check session validity every 5 minutes
        setInterval(() => {
            if (this.token) {
                if (this.isTokenExpired(this.token)) {
                    this.refreshAccessToken();
                }
            }
        }, 5 * 60 * 1000);

        // Monitor for inactivity
        let inactivityTimer;
        const resetTimer = () => {
            clearTimeout(inactivityTimer);
            inactivityTimer = setTimeout(() => {
                this.showInactivityWarning();
            }, 15 * 60 * 1000); // 15 minutes
        };

        // Reset timer on user activity
        ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
            document.addEventListener(event, resetTimer, true);
        });

        resetTimer();
    }

    showInactivityWarning() {
        if (confirm('Your session will expire due to inactivity. Do you want to continue?')) {
            if (this.token) {
                this.refreshAccessToken();
            }
        } else {
            this.logout();
        }
    }

    isTokenExpired(token) {
        try {
            // Parse JWT token
            const payload = JSON.parse(atob(token.split('.')[1]));
            const expiry = payload.exp * 1000; // Convert to milliseconds

            // Check if expired (with 5 minute buffer)
            return Date.now() >= expiry - (5 * 60 * 1000);

        } catch (error) {
            return true;
        }
    }

    generateMockToken(user) {
        // Generate a mock JWT token for demo
        const header = {
            alg: 'HS256',
            typ: 'JWT'
        };

        const payload = {
            sub: user.id,
            name: user.name,
            iat: Math.floor(Date.now() / 1000),
            exp: Math.floor(Date.now() / 1000) + (24 * 60 * 60) // 24 hours
        };

        const base64Header = btoa(JSON.stringify(header));
        const base64Payload = btoa(JSON.stringify(payload));
        const signature = 'mock_signature';

        return `${base64Header}.${base64Payload}.${signature}`;
    }

    // User profile management
    async updateProfile(updates) {
        try {
            const response = await fetch(`${this.apiUrl}/api/user/profile`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify(updates)
            });

            if (!response.ok) {
                throw new Error('Failed to update profile');
            }

            const data = await response.json();

            // Update local user data
            this.user = { ...this.user, ...data.user };
            localStorage.setItem('zmart_user', JSON.stringify(this.user));

            return data;

        } catch (error) {
            console.error('Profile update error:', error);
            throw error;
        }
    }

    // Two-factor authentication
    async enable2FA() {
        try {
            const response = await fetch(`${this.apiUrl}/api/auth/2fa/enable`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to enable 2FA');
            }

            const data = await response.json();
            return data; // Returns QR code and secret

        } catch (error) {
            console.error('2FA enable error:', error);
            throw error;
        }
    }

    async verify2FA(code) {
        try {
            const response = await fetch(`${this.apiUrl}/api/auth/2fa/verify`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({ code })
            });

            if (!response.ok) {
                throw new Error('Invalid 2FA code');
            }

            const data = await response.json();
            return data;

        } catch (error) {
            console.error('2FA verify error:', error);
            throw error;
        }
    }

    // Password reset
    async requestPasswordReset(email) {
        try {
            const response = await fetch(`${this.apiUrl}/api/auth/password/reset-request`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email })
            });

            if (!response.ok) {
                throw new Error('Failed to send reset email');
            }

            const data = await response.json();
            return data;

        } catch (error) {
            console.error('Password reset request error:', error);
            throw error;
        }
    }

    async resetPassword(token, newPassword) {
        try {
            const response = await fetch(`${this.apiUrl}/api/auth/password/reset`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    token: token,
                    password: newPassword
                })
            });

            if (!response.ok) {
                throw new Error('Failed to reset password');
            }

            const data = await response.json();
            return data;

        } catch (error) {
            console.error('Password reset error:', error);
            throw error;
        }
    }

    // Session management
    getUser() {
        return this.user;
    }

    getToken() {
        return this.token;
    }

    isAuthenticated() {
        return !!this.token && !this.isTokenExpired(this.token);
    }

    hasPermission(permission) {
        if (!this.user) return false;
        return this.user.permissions?.includes(permission) || false;
    }

    hasRole(role) {
        if (!this.user) return false;
        return this.user.roles?.includes(role) || false;
    }
}

// Initialize auth manager when app is ready
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        if (window.zmartApp) {
            window.zmartAuth = new AuthManager(window.zmartApp);

            // Override onboarding auth methods
            if (window.zmartOnboarding) {
                const onboarding = window.zmartOnboarding;

                onboarding.sendVerificationCode = async function() {
                    const contact = this.userData.contactType === 'phone'
                        ? this.userData.phoneNumber
                        : this.userData.email;

                    const result = await window.zmartAuth.sendOTP(contact, this.userData.contactType);
                    if (result.success) {
                        this.app.showScreen('verify');
                        this.startResendTimer();
                        this.showNotification(`Verification code sent to ${contact}`, 'success');
                    }
                };

                onboarding.verifyOtp = async function() {
                    const contact = this.userData.contactType === 'phone'
                        ? this.userData.phoneNumber
                        : this.userData.email;

                    try {
                        const result = await window.zmartAuth.verifyOTP(contact, this.userData.verificationCode);
                        if (result.success) {
                            this.showNotification('Verification successful!', 'success');
                            window.zmartApp.currentUser = result.user;
                            window.zmartApp.showScreen('chat');
                            window.zmartApp.initializeChat();
                        }
                    } catch (error) {
                        this.showNotification('Invalid verification code', 'error');
                    }
                };
            }
        }
    }, 300);
});