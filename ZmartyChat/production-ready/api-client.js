// API Client for ZmartBot Backend Integration
const API_BASE_URL = 'http://localhost:8000';

// User Registration
async function registerUser(userData) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: userData.email,
                password: userData.password || generateTempPassword(),
                name: userData.name,
                country: userData.country,
                provider: userData.provider || 'email',
                tier: userData.tier || 'free'
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Registration failed');
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Registration error:', error);
        throw error;
    }
}

// User Login
async function loginUser(email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }

        const data = await response.json();
        // Store token
        if (data.access_token) {
            localStorage.setItem('zmarty_token', data.access_token);
            localStorage.setItem('zmarty_user', JSON.stringify(data.user));
        }
        return data;
    } catch (error) {
        console.error('Login error:', error);
        throw error;
    }
}

// Send Verification Email
async function sendVerificationEmail(email) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/send-verification`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to send verification email');
        }

        return await response.json();
    } catch (error) {
        console.error('Send verification error:', error);
        // For demo, generate local code
        const code = Math.floor(100000 + Math.random() * 900000).toString();
        localStorage.setItem('zmarty_verification_code', code);
        return { code, demo: true };
    }
}

// Verify Email Code
async function verifyEmailCode(email, code) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/verify-email`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, code })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Invalid verification code');
        }

        return await response.json();
    } catch (error) {
        console.error('Verification error:', error);
        // For demo, check local code
        const savedCode = localStorage.getItem('zmarty_verification_code');
        if (code === savedCode) {
            return { verified: true, demo: true };
        }
        throw new Error('Invalid verification code');
    }
}

// OAuth Login (Google/Apple)
async function oauthLogin(provider, token) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/oauth/${provider}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ token })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'OAuth login failed');
        }

        const data = await response.json();
        // Store token
        if (data.access_token) {
            localStorage.setItem('zmarty_token', data.access_token);
            localStorage.setItem('zmarty_user', JSON.stringify(data.user));
        }
        return data;
    } catch (error) {
        console.error('OAuth error:', error);
        // For demo, create temporary session
        return {
            access_token: 'demo_token_' + Date.now(),
            user: {
                provider,
                email: `demo@${provider}.com`,
                verified: true
            }
        };
    }
}

// Update User Profile
async function updateUserProfile(userId, profileData) {
    try {
        const token = localStorage.getItem('zmarty_token');
        const response = await fetch(`${API_BASE_URL}/api/users/${userId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(profileData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to update profile');
        }

        const data = await response.json();
        // Update local storage
        localStorage.setItem('zmarty_user', JSON.stringify(data));
        return data;
    } catch (error) {
        console.error('Update profile error:', error);
        // For demo, update local storage
        const user = JSON.parse(localStorage.getItem('zmarty_user') || '{}');
        Object.assign(user, profileData);
        localStorage.setItem('zmarty_user', JSON.stringify(user));
        return user;
    }
}

// Helper function to generate temporary password
function generateTempPassword() {
    return 'Temp@' + Math.random().toString(36).substr(2, 9);
}

// Check if user is logged in
function isLoggedIn() {
    return !!localStorage.getItem('zmarty_token');
}

// Get current user
function getCurrentUser() {
    const userStr = localStorage.getItem('zmarty_user');
    return userStr ? JSON.parse(userStr) : null;
}

// Logout
function logout() {
    localStorage.removeItem('zmarty_token');
    localStorage.removeItem('zmarty_user');
    localStorage.removeItem('zmarty_onboarding_complete');
    window.location.href = 'index.html';
}

// Export functions for use in other files
window.zmartAPI = {
    registerUser,
    loginUser,
    sendVerificationEmail,
    verifyEmailCode,
    oauthLogin,
    updateUserProfile,
    isLoggedIn,
    getCurrentUser,
    logout
};