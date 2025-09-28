/**
 * Implementation Script for Password Protection
 * Use this in your signup/login components
 */

import { createClient } from '@supabase/supabase-js';
import { validatePasswordComplete, generateStrongPassword } from './password-validation.js';
import { parseAuthError, getErrorDisplay } from './auth-error-handler.js';

// Initialize Supabase
const supabaseUrl = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
const supabase = createClient(supabaseUrl, supabaseAnonKey);

/**
 * Enhanced Sign Up with Password Protection
 * @param {string} email - User email
 * @param {string} password - User password
 * @param {Object} metadata - Additional user metadata
 * @returns {Promise<Object>} Signup result
 */
export async function secureSignUp(email, password, metadata = {}) {
    try {
        // Step 1: Validate password locally
        console.log('Validating password security...');
        const validation = await validatePasswordComplete(password, email);

        if (!validation.valid) {
            return {
                success: false,
                error: {
                    type: validation.compromised ? 'compromised' : 'weak',
                    message: validation.errors[0],
                    suggestions: validation.compromised ? [
                        'This password has been exposed in a data breach',
                        'Use a unique password not used elsewhere',
                        'Consider using a password manager'
                    ] : validation.errors,
                    showPasswordGenerator: true
                }
            };
        }

        // Step 2: Attempt signup with Supabase
        console.log('Creating account...');
        const { data, error } = await supabase.auth.signUp({
            email,
            password,
            options: {
                data: {
                    ...metadata,
                    password_strength: validation.strength.level,
                    password_score: validation.strength.score
                }
            }
        });

        if (error) {
            // Parse Supabase error
            const parsedError = parseAuthError(error);
            return {
                success: false,
                error: parsedError
            };
        }

        // Step 3: Log successful signup
        console.log('Account created successfully');

        // Track in analytics if available
        if (typeof window !== 'undefined' && window.analytics) {
            window.analytics.track('Signup Success', {
                email: email,
                password_strength: validation.strength.level
            });
        }

        return {
            success: true,
            data: data,
            message: 'Account created! Please check your email to verify your account.'
        };

    } catch (error) {
        console.error('Signup error:', error);
        return {
            success: false,
            error: {
                type: 'system',
                message: 'An error occurred during signup. Please try again.',
                originalError: error.message
            }
        };
    }
}

/**
 * Enhanced Password Reset with Security Check
 * @param {string} email - User email
 * @param {string} newPassword - New password
 * @returns {Promise<Object>} Reset result
 */
export async function securePasswordReset(email, newPassword) {
    try {
        // Validate new password
        const validation = await validatePasswordComplete(newPassword, email);

        if (!validation.valid) {
            return {
                success: false,
                error: {
                    type: validation.compromised ? 'compromised' : 'weak',
                    message: validation.errors[0],
                    showPasswordGenerator: true
                }
            };
        }

        // Update password in Supabase
        const { data, error } = await supabase.auth.updateUser({
            password: newPassword
        });

        if (error) {
            const parsedError = parseAuthError(error);
            return {
                success: false,
                error: parsedError
            };
        }

        return {
            success: true,
            message: 'Password updated successfully!'
        };

    } catch (error) {
        console.error('Password reset error:', error);
        return {
            success: false,
            error: {
                type: 'system',
                message: 'Failed to reset password. Please try again.'
            }
        };
    }
}

/**
 * React Component Example
 */
export function SignUpForm() {
    const [email, setEmail] = React.useState('');
    const [password, setPassword] = React.useState('');
    const [confirmPassword, setConfirmPassword] = React.useState('');
    const [error, setError] = React.useState(null);
    const [success, setSuccess] = React.useState(false);
    const [loading, setLoading] = React.useState(false);
    const [showGenerator, setShowGenerator] = React.useState(false);
    const [passwordStrength, setPasswordStrength] = React.useState(null);

    // Real-time password validation
    React.useEffect(() => {
        if (password) {
            const timer = setTimeout(async () => {
                const validation = await validatePasswordComplete(password, email);
                setPasswordStrength(validation.strength);

                if (!validation.valid && validation.errors.length > 0) {
                    setError({
                        message: validation.errors[0],
                        type: validation.compromised ? 'compromised' : 'validation'
                    });
                } else {
                    setError(null);
                }
            }, 500);

            return () => clearTimeout(timer);
        } else {
            setPasswordStrength(null);
            setError(null);
        }
    }, [password, email]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        // Check passwords match
        if (password !== confirmPassword) {
            setError({ message: 'Passwords do not match' });
            setLoading(false);
            return;
        }

        // Attempt signup
        const result = await secureSignUp(email, password);

        if (result.success) {
            setSuccess(true);
            setError(null);
        } else {
            setError(result.error);
            if (result.error.showPasswordGenerator) {
                setShowGenerator(true);
            }
        }

        setLoading(false);
    };

    const handleGeneratePassword = () => {
        const newPassword = generateStrongPassword(16);
        setPassword(newPassword);
        setConfirmPassword(newPassword);
        setShowGenerator(false);
    };

    if (success) {
        return (
            <div className="success-message">
                <h2>Welcome to ZmartyChat!</h2>
                <p>Please check your email to verify your account.</p>
            </div>
        );
    }

    return (
        <form onSubmit={handleSubmit} className="signup-form">
            <h2>Create Your Account</h2>

            {error && (
                <div className={`alert alert-${error.type === 'compromised' ? 'warning' : 'error'}`}>
                    {error.type === 'compromised' && <span className="icon">⚠️</span>}
                    <p>{error.message}</p>
                    {error.suggestions && (
                        <ul>
                            {error.suggestions.map((suggestion, i) => (
                                <li key={i}>{suggestion}</li>
                            ))}
                        </ul>
                    )}
                </div>
            )}

            <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                    type="email"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    disabled={loading}
                />
            </div>

            <div className="form-group">
                <label htmlFor="password">Password</label>
                <input
                    type="password"
                    id="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    disabled={loading}
                    minLength={12}
                />

                {passwordStrength && (
                    <div className="password-strength">
                        <div
                            className="strength-bar"
                            style={{
                                width: `${passwordStrength.score}%`,
                                backgroundColor: passwordStrength.color
                            }}
                        />
                        <span className="strength-label">
                            Strength: {passwordStrength.level}
                        </span>
                    </div>
                )}

                <small className="help-text">
                    Minimum 12 characters with uppercase, lowercase, numbers, and symbols
                </small>
            </div>

            <div className="form-group">
                <label htmlFor="confirmPassword">Confirm Password</label>
                <input
                    type="password"
                    id="confirmPassword"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    disabled={loading}
                />
            </div>

            {showGenerator && (
                <div className="password-generator">
                    <p>Need a strong password?</p>
                    <button
                        type="button"
                        onClick={handleGeneratePassword}
                        className="btn-secondary"
                    >
                        Generate Secure Password
                    </button>
                </div>
            )}

            <button
                type="submit"
                disabled={loading || (error && error.type === 'compromised')}
                className="btn-primary"
            >
                {loading ? 'Creating Account...' : 'Sign Up'}
            </button>

            <p className="privacy-note">
                <small>
                    We check passwords against known breaches to keep your account secure.
                    Your password is never shared with third parties.
                </small>
            </p>
        </form>
    );
}

/**
 * Usage in your app
 */
export default {
    secureSignUp,
    securePasswordReset,
    SignUpForm
};