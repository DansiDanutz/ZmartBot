/**
 * Auth Error Handler for Supabase with Enhanced Password Protection
 * Provides user-friendly error messages and handles compromised password scenarios
 */

/**
 * Map Supabase auth error codes to user-friendly messages
 */
const ERROR_MESSAGES = {
    // Password-related errors
    'weak_password': 'Password does not meet security requirements. Please use at least 12 characters with a mix of letters, numbers, and symbols.',
    'compromised_password': 'This password has been found in a data breach and cannot be used. Please choose a unique, strong password.',
    'password_leaked': 'For your security, this password cannot be used as it has appeared in known data breaches. Please create a unique password.',
    'password_strength': 'Password is too weak. Use a combination of uppercase, lowercase, numbers, and special characters.',

    // Registration errors
    'email_exists': 'An account with this email already exists. Please sign in or use a different email.',
    'invalid_email': 'Please enter a valid email address.',
    'signup_disabled': 'New registrations are temporarily disabled. Please try again later.',

    // Login errors
    'invalid_credentials': 'Invalid email or password. Please check your credentials and try again.',
    'email_not_confirmed': 'Please verify your email address before signing in. Check your inbox for the confirmation link.',
    'user_banned': 'This account has been suspended. Please contact support for assistance.',
    'too_many_attempts': 'Too many failed login attempts. Please wait a few minutes before trying again.',

    // Session errors
    'session_expired': 'Your session has expired. Please sign in again.',
    'refresh_token_expired': 'Please sign in again to continue.',
    'invalid_token': 'Authentication failed. Please sign in again.',

    // Network errors
    'network_error': 'Unable to connect to the server. Please check your internet connection.',
    'server_error': 'A server error occurred. Please try again later.',
    'timeout': 'Request timed out. Please check your connection and try again.',

    // Rate limiting
    'rate_limit': 'Too many requests. Please slow down and try again.',
    'email_rate_limit': 'Too many emails sent. Please wait before requesting another email.',

    // Default fallback
    'unknown_error': 'An unexpected error occurred. Please try again or contact support if the problem persists.'
};

/**
 * Parse Supabase auth error and return user-friendly message
 * @param {Error} error - Supabase auth error object
 * @returns {Object} Parsed error with user-friendly message and metadata
 */
export function parseAuthError(error) {
    if (!error) {
        return {
            message: ERROR_MESSAGES.unknown_error,
            code: 'unknown_error',
            type: 'generic',
            recoverable: true
        };
    }

    // Check for specific error patterns
    const errorString = error.message?.toLowerCase() || '';
    const errorCode = error.code?.toLowerCase() || '';

    // Check for compromised password
    if (errorString.includes('compromised') || errorString.includes('leaked') || errorString.includes('breached') || errorString.includes('pwned')) {
        return {
            message: ERROR_MESSAGES.compromised_password,
            code: 'compromised_password',
            type: 'security',
            recoverable: true,
            action: 'change_password',
            severity: 'high'
        };
    }

    // Check for weak password
    if (errorString.includes('weak') || errorString.includes('strength') || errorCode === 'weak_password') {
        return {
            message: ERROR_MESSAGES.weak_password,
            code: 'weak_password',
            type: 'validation',
            recoverable: true,
            action: 'strengthen_password'
        };
    }

    // Check for rate limiting
    if (errorString.includes('rate') || errorString.includes('too many')) {
        return {
            message: ERROR_MESSAGES.rate_limit,
            code: 'rate_limit',
            type: 'rate_limit',
            recoverable: true,
            retryAfter: 60 // seconds
        };
    }

    // Check for session issues
    if (errorString.includes('session') || errorString.includes('expired')) {
        return {
            message: ERROR_MESSAGES.session_expired,
            code: 'session_expired',
            type: 'session',
            recoverable: true,
            action: 'reauthenticate'
        };
    }

    // Check for network issues
    if (errorString.includes('network') || errorString.includes('fetch')) {
        return {
            message: ERROR_MESSAGES.network_error,
            code: 'network_error',
            type: 'network',
            recoverable: true,
            action: 'retry'
        };
    }

    // Check for invalid credentials
    if (errorString.includes('invalid') && (errorString.includes('credential') || errorString.includes('password'))) {
        return {
            message: ERROR_MESSAGES.invalid_credentials,
            code: 'invalid_credentials',
            type: 'authentication',
            recoverable: true,
            action: 'check_credentials'
        };
    }

    // Map known error codes
    const knownError = ERROR_MESSAGES[errorCode];
    if (knownError) {
        return {
            message: knownError,
            code: errorCode,
            type: 'known_error',
            recoverable: true
        };
    }

    // Default fallback
    return {
        message: ERROR_MESSAGES.unknown_error,
        code: 'unknown_error',
        type: 'generic',
        recoverable: true,
        originalError: error.message
    };
}

/**
 * Display error message to user with appropriate styling
 * @param {Object} parsedError - Parsed error object from parseAuthError
 * @returns {Object} Display configuration for UI
 */
export function getErrorDisplay(parsedError) {
    const baseConfig = {
        message: parsedError.message,
        icon: '⚠️',
        color: 'red',
        duration: 5000
    };

    switch (parsedError.type) {
        case 'security':
            return {
                ...baseConfig,
                icon: '🔒',
                color: 'orange',
                duration: 10000,
                showHelp: true,
                helpText: 'Use a password manager to generate and store strong, unique passwords.'
            };

        case 'validation':
            return {
                ...baseConfig,
                icon: '✋',
                color: 'yellow',
                duration: 7000,
                showHelp: true,
                helpText: 'A strong password has 12+ characters with uppercase, lowercase, numbers, and symbols.'
            };

        case 'rate_limit':
            return {
                ...baseConfig,
                icon: '⏰',
                color: 'blue',
                duration: parsedError.retryAfter ? parsedError.retryAfter * 1000 : 60000,
                showCountdown: true,
                retryAfter: parsedError.retryAfter
            };

        case 'network':
            return {
                ...baseConfig,
                icon: '📡',
                color: 'gray',
                duration: 5000,
                showRetry: true
            };

        case 'session':
            return {
                ...baseConfig,
                icon: '🔑',
                color: 'purple',
                duration: 5000,
                showAction: true,
                actionText: 'Sign In',
                actionType: 'reauthenticate'
            };

        default:
            return baseConfig;
    }
}

/**
 * Handle auth error with logging and user notification
 * @param {Error} error - Original error
 * @param {Object} context - Additional context (user action, component, etc.)
 * @returns {Promise<void>}
 */
export async function handleAuthError(error, context = {}) {
    // Parse the error
    const parsedError = parseAuthError(error);

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
        console.error('Auth Error:', {
            parsed: parsedError,
            original: error,
            context,
            timestamp: new Date().toISOString()
        });
    }

    // Log to analytics/monitoring service (if configured)
    if (typeof window !== 'undefined' && window.analytics) {
        window.analytics.track('Auth Error', {
            error_code: parsedError.code,
            error_type: parsedError.type,
            context: context.action || 'unknown',
            recoverable: parsedError.recoverable
        });
    }

    // Return parsed error for UI handling
    return parsedError;
}

/**
 * React hook for auth error handling
 * @returns {Object} Error state and handlers
 */
export function useAuthError() {
    const [error, setError] = React.useState(null);
    const [isLoading, setIsLoading] = React.useState(false);

    const handleError = React.useCallback(async (err, context) => {
        const parsedError = await handleAuthError(err, context);
        setError(parsedError);
        setIsLoading(false);

        // Auto-clear error after duration
        const display = getErrorDisplay(parsedError);
        setTimeout(() => {
            setError(null);
        }, display.duration);

        return parsedError;
    }, []);

    const clearError = React.useCallback(() => {
        setError(null);
    }, []);

    return {
        error,
        isLoading,
        handleError,
        clearError,
        setIsLoading
    };
}

/**
 * Password-specific error handler for registration/password change
 * @param {string} password - Password being validated
 * @param {Error} error - Supabase error
 * @returns {Object} Detailed password error information
 */
export function handlePasswordError(password, error) {
    const parsedError = parseAuthError(error);

    // If it's a compromised password error
    if (parsedError.code === 'compromised_password') {
        return {
            ...parsedError,
            suggestions: [
                'Use a unique password not used on other sites',
                'Try a passphrase with random words',
                'Use a password manager to generate a secure password'
            ],
            showPasswordGenerator: true
        };
    }

    // If it's a weak password error
    if (parsedError.code === 'weak_password') {
        const missingRequirements = [];

        if (password.length < 12) {
            missingRequirements.push('At least 12 characters');
        }
        if (!/[A-Z]/.test(password)) {
            missingRequirements.push('Uppercase letters');
        }
        if (!/[a-z]/.test(password)) {
            missingRequirements.push('Lowercase letters');
        }
        if (!/\d/.test(password)) {
            missingRequirements.push('Numbers');
        }
        if (!/[^a-zA-Z0-9]/.test(password)) {
            missingRequirements.push('Special characters');
        }

        return {
            ...parsedError,
            missingRequirements,
            showStrengthMeter: true
        };
    }

    return parsedError;
}

export default {
    parseAuthError,
    getErrorDisplay,
    handleAuthError,
    useAuthError,
    handlePasswordError,
    ERROR_MESSAGES
};