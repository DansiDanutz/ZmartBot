// Enhanced Social Authentication Handler
async function handleSocialAuth(provider) {
    console.log(`Starting ${provider} OAuth authentication...`);
    
    try {
        // Check if Supabase is properly initialized
        if (!window.supabase) {
            throw new Error('Supabase client not initialized');
        }

        // Check if already logged in
        const { data: { session } } = await supabase.auth.getSession();
        if (session) {
            console.log('Already logged in as', session.user.email);
            goToSlide(6); // Go to tier selection
            return;
        }

        // Track OAuth attempt
        trackEvent('social_auth_started', { provider: provider });

        // Show loading state
        const button = event.target;
        const originalText = button.innerHTML;
        button.innerHTML = `<span style="display: inline-block; width: 20px; height: 20px; border: 2px solid #fff; border-top: 2px solid transparent; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 8px;"></span>Connecting...`;
        button.disabled = true;

        // Configure OAuth options based on provider
        const oauthOptions = {
            redirectTo: `${window.location.origin}/auth/callback`,
            queryParams: {
                access_type: 'offline',
                prompt: 'consent'
            },
            // Enable PKCE for secure OAuth flow
            flowType: 'pkce'
        };

        // Google OAuth scopes
        if (provider === 'google') {
            oauthOptions.scopes = 'email profile';
        }

        console.log('OAuth options:', oauthOptions);

        // Initiate OAuth flow
        const { data, error } = await supabase.auth.signInWithOAuth({
            provider: provider,
            options: oauthOptions
        });
        
        if (error) {
            throw error;
        }
        
        console.log('OAuth redirect initiated successfully');
        trackEvent('social_auth_redirecting', { provider: provider });
        
        // The user will be redirected to the OAuth provider
        // The callback will be handled by auth/callback/index.html
        
    } catch (error) {
        console.error('Social auth error:', error);
        trackError('social_auth_failed', error);
        
        // Restore button state
        if (event && event.target) {
            event.target.innerHTML = originalText;
            event.target.disabled = false;
        }
        
        // Show user-friendly error message
        let errorMessage = 'Authentication failed. Please try again.';
        
        if (error.message.includes('not configured')) {
            errorMessage = `${provider.charAt(0).toUpperCase() + provider.slice(1)} authentication is not configured. Please try email registration.`;
        } else if (error.message.includes('network')) {
            errorMessage = 'Network error. Please check your connection and try again.';
        } else if (error.message.includes('popup')) {
            errorMessage = 'Popup blocked. Please allow popups and try again.';
        }
        
        showNotification(errorMessage, 'error');
    }
}

// Add CSS for spin animation if not present
if (!document.querySelector('#oauth-styles')) {
    const styles = document.createElement('style');
    styles.id = 'oauth-styles';
    styles.textContent = `
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(styles);
}

// Enhanced notification system
function showNotification(message, type = 'info', duration = 5000) {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(n => n.remove());
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;
    
    // Add styles if not already present
    if (!document.querySelector('#notification-styles')) {
        const styles = document.createElement('style');
        styles.id = 'notification-styles';
        styles.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                max-width: 400px;
                padding: 16px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                z-index: 10000;
                animation: slideIn 0.3s ease-out;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            
            .notification-info {
                background: #3b82f6;
                color: white;
            }
            
            .notification-success {
                background: #10b981;
                color: white;
            }
            
            .notification-error {
                background: #ef4444;
                color: white;
            }
            
            .notification-warning {
                background: #f59e0b;
                color: white;
            }
            
            .notification-content {
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            
            .notification-message {
                flex: 1;
                margin-right: 12px;
            }
            
            .notification-close {
                background: none;
                border: none;
                color: inherit;
                font-size: 20px;
                cursor: pointer;
                padding: 0;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 4px;
                opacity: 0.8;
            }
            
            .notification-close:hover {
                opacity: 1;
                background: rgba(255, 255, 255, 0.2);
            }
            
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @media (max-width: 480px) {
                .notification {
                    left: 20px;
                    right: 20px;
                    max-width: none;
                }
            }
        `;
        document.head.appendChild(styles);
    }
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after duration
    if (duration > 0) {
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.animation = 'slideIn 0.3s ease-out reverse';
                setTimeout(() => notification.remove(), 300);
            }
        }, duration);
    }
}

// Placeholder functions for compatibility
function trackEvent(eventName, properties = {}) {
    console.log('Track Event:', eventName, properties);
}

function trackError(errorType, error) {
    console.error('Track Error:', errorType, error);
}

function goToSlide(slideNumber) {
    console.log('Go to slide:', slideNumber);
    // This would be implemented in the main onboarding.js
}

console.log('Enhanced OAuth handler loaded');
