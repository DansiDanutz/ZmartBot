// ZmartTrade - Onboarding Flow Controller
class OnboardingController {
    constructor(app) {
        this.app = app;
        this.userData = {
            name: '',
            contactType: 'phone',
            phoneNumber: '',
            countryCode: '+1',
            email: '',
            verificationCode: ''
        };
        this.verificationTimer = null;
        this.resendCooldown = 60;

        this.init();
    }

    init() {
        this.bindWelcomeScreen();
        this.bindNameScreen();
        this.bindContactScreen();
        this.bindVerificationScreen();
        this.setupCountryCodeSelector();
    }

    bindWelcomeScreen() {
        const getStartedBtn = document.getElementById('getStartedBtn');
        const features = document.querySelectorAll('.feature-card');

        // Animate features on load
        features.forEach((feature, index) => {
            setTimeout(() => {
                feature.classList.add('animate-fadeIn');
            }, index * 100);
        });

        getStartedBtn?.addEventListener('click', () => {
            this.app.showScreen('name');
            this.playButtonSound();
        });

        // Add hover effects
        getStartedBtn?.addEventListener('mouseenter', () => {
            getStartedBtn.classList.add('hover-grow');
        });

        getStartedBtn?.addEventListener('mouseleave', () => {
            getStartedBtn.classList.remove('hover-grow');
        });
    }

    bindNameScreen() {
        const nameInput = document.getElementById('nameInput');
        const namePreview = document.getElementById('namePreview');
        const continueNameBtn = document.getElementById('continueNameBtn');

        // Real-time preview
        nameInput?.addEventListener('input', (e) => {
            const name = e.target.value.trim();
            this.userData.name = name;

            // Update preview
            if (namePreview) {
                if (name) {
                    namePreview.innerHTML = `
                        <div class="preview-message animate-fadeIn">
                            <span class="preview-emoji">👋</span>
                            <span>Hi <strong>${name}</strong>, I'm Zmarty!</span>
                        </div>
                    `;
                } else {
                    namePreview.innerHTML = '';
                }
            }

            // Enable/disable continue button
            if (continueNameBtn) {
                continueNameBtn.disabled = !name;
                continueNameBtn.classList.toggle('opacity-50', !name);
            }
        });

        // Continue to contact screen
        continueNameBtn?.addEventListener('click', () => {
            if (this.userData.name) {
                this.app.showScreen('contact');
                this.playButtonSound();
            }
        });

        // Enter key to continue
        nameInput?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && this.userData.name) {
                continueNameBtn?.click();
            }
        });
    }

    bindContactScreen() {
        const contactToggle = document.getElementById('contactToggle');
        const phoneSection = document.getElementById('phoneSection');
        const emailSection = document.getElementById('emailSection');
        const phoneInput = document.getElementById('phoneInput');
        const emailInput = document.getElementById('emailInput');
        const countryCode = document.getElementById('countryCode');
        const sendOtpBtn = document.getElementById('sendOtpBtn');

        // Toggle between phone and email
        contactToggle?.addEventListener('change', (e) => {
            this.userData.contactType = e.target.checked ? 'email' : 'phone';

            if (this.userData.contactType === 'phone') {
                phoneSection?.classList.remove('hidden');
                emailSection?.classList.add('hidden');
                phoneInput?.focus();
            } else {
                emailSection?.classList.remove('hidden');
                phoneSection?.classList.add('hidden');
                emailInput?.focus();
            }

            this.validateContactInput();
        });

        // Phone input formatting
        phoneInput?.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, '');

            // Format as US phone number (XXX) XXX-XXXX
            if (value.length > 0) {
                if (value.length <= 3) {
                    value = `(${value}`;
                } else if (value.length <= 6) {
                    value = `(${value.slice(0, 3)}) ${value.slice(3)}`;
                } else {
                    value = `(${value.slice(0, 3)}) ${value.slice(3, 6)}-${value.slice(6, 10)}`;
                }
            }

            e.target.value = value;
            this.userData.phoneNumber = value;
            this.validateContactInput();
        });

        // Email validation
        emailInput?.addEventListener('input', (e) => {
            this.userData.email = e.target.value;
            this.validateContactInput();
        });

        // Country code selection
        countryCode?.addEventListener('change', (e) => {
            this.userData.countryCode = e.target.value;
        });

        // Send OTP
        sendOtpBtn?.addEventListener('click', async () => {
            if (this.isContactValid()) {
                await this.sendVerificationCode();
            }
        });
    }

    bindVerificationScreen() {
        const otpInputs = document.querySelectorAll('.otp-input');
        const resendBtn = document.getElementById('resendOtpBtn');
        const resendTimer = document.getElementById('resendTimer');
        const verifyBtn = document.getElementById('verifyBtn');

        // Auto-focus first input
        otpInputs[0]?.focus();

        // Handle OTP input
        otpInputs.forEach((input, index) => {
            input.addEventListener('input', (e) => {
                const value = e.target.value;

                if (value && index < otpInputs.length - 1) {
                    // Move to next input
                    otpInputs[index + 1].focus();
                }

                // Check if all inputs are filled
                this.checkOtpComplete(otpInputs);
            });

            input.addEventListener('keydown', (e) => {
                if (e.key === 'Backspace' && !e.target.value && index > 0) {
                    // Move to previous input
                    otpInputs[index - 1].focus();
                }
            });

            // Only allow digits
            input.addEventListener('keypress', (e) => {
                if (!/\d/.test(e.key)) {
                    e.preventDefault();
                }
            });

            // Paste handling
            input.addEventListener('paste', (e) => {
                e.preventDefault();
                const pastedData = e.clipboardData.getData('text').replace(/\D/g, '');

                if (pastedData.length === 6) {
                    pastedData.split('').forEach((digit, i) => {
                        if (otpInputs[i]) {
                            otpInputs[i].value = digit;
                        }
                    });
                    this.checkOtpComplete(otpInputs);
                }
            });
        });

        // Resend OTP
        resendBtn?.addEventListener('click', async () => {
            if (!resendBtn.disabled) {
                await this.sendVerificationCode();
            }
        });

        // Manual verify button
        verifyBtn?.addEventListener('click', () => {
            this.verifyOtp();
        });

        // Update contact display
        this.updateVerificationDisplay();
    }

    setupCountryCodeSelector() {
        const countryCode = document.getElementById('countryCode');
        if (!countryCode) return;

        // Popular country codes
        const countries = [
            { code: '+1', country: 'US/CA', flag: '🇺🇸' },
            { code: '+44', country: 'UK', flag: '🇬🇧' },
            { code: '+91', country: 'India', flag: '🇮🇳' },
            { code: '+86', country: 'China', flag: '🇨🇳' },
            { code: '+81', country: 'Japan', flag: '🇯🇵' },
            { code: '+49', country: 'Germany', flag: '🇩🇪' },
            { code: '+33', country: 'France', flag: '🇫🇷' },
            { code: '+39', country: 'Italy', flag: '🇮🇹' },
            { code: '+34', country: 'Spain', flag: '🇪🇸' },
            { code: '+61', country: 'Australia', flag: '🇦🇺' },
            { code: '+55', country: 'Brazil', flag: '🇧🇷' },
            { code: '+7', country: 'Russia', flag: '🇷🇺' }
        ];

        countryCode.innerHTML = countries.map(c =>
            `<option value="${c.code}">${c.flag} ${c.code} ${c.country}</option>`
        ).join('');
    }

    validateContactInput() {
        const sendOtpBtn = document.getElementById('sendOtpBtn');
        const isValid = this.isContactValid();

        if (sendOtpBtn) {
            sendOtpBtn.disabled = !isValid;
            sendOtpBtn.classList.toggle('opacity-50', !isValid);
        }

        return isValid;
    }

    isContactValid() {
        if (this.userData.contactType === 'phone') {
            // Check if phone number is complete (14 chars for formatted US number)
            return this.userData.phoneNumber.length >= 14;
        } else {
            // Basic email validation
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(this.userData.email);
        }
    }

    async sendVerificationCode() {
        const sendOtpBtn = document.getElementById('sendOtpBtn');
        const contact = this.userData.contactType === 'phone'
            ? `${this.userData.countryCode} ${this.userData.phoneNumber}`
            : this.userData.email;

        // Show loading state
        if (sendOtpBtn) {
            sendOtpBtn.disabled = true;
            sendOtpBtn.innerHTML = '<span class="animate-rotate">⏳</span> Sending...';
        }

        try {
            // Simulate API call
            await this.simulateApiCall(1000);

            // For demo, generate a random code
            const code = Math.floor(100000 + Math.random() * 900000).toString();
            console.log(`Verification code for ${contact}: ${code}`);

            // In production, this would be sent via SMS/Email
            // For demo, we'll auto-fill after 2 seconds
            setTimeout(() => {
                if (window.location.hash === '#verify') {
                    this.autoFillOtp(code);
                }
            }, 2000);

            // Show verification screen
            this.app.showScreen('verify');
            this.startResendTimer();

            // Show success message
            this.showNotification(`Verification code sent to ${contact}`, 'success');

        } catch (error) {
            console.error('Error sending OTP:', error);
            this.showNotification('Failed to send verification code. Please try again.', 'error');
        } finally {
            // Reset button
            if (sendOtpBtn) {
                sendOtpBtn.disabled = false;
                sendOtpBtn.innerHTML = 'Send OTP';
            }
        }
    }

    updateVerificationDisplay() {
        const contactDisplay = document.getElementById('verificationContact');

        if (contactDisplay) {
            const contact = this.userData.contactType === 'phone'
                ? `${this.userData.countryCode} ${this.userData.phoneNumber}`
                : this.userData.email;

            contactDisplay.innerHTML = `
                <p>Enter the 6-digit code sent to</p>
                <p class="font-bold text-orange">${contact}</p>
            `;
        }
    }

    checkOtpComplete(inputs) {
        const code = Array.from(inputs).map(i => i.value).join('');
        this.userData.verificationCode = code;

        if (code.length === 6) {
            // Auto-verify when complete
            this.verifyOtp();
        }
    }

    autoFillOtp(code) {
        const otpInputs = document.querySelectorAll('.otp-input');
        code.split('').forEach((digit, index) => {
            if (otpInputs[index]) {
                otpInputs[index].value = digit;
                // Add animation
                otpInputs[index].classList.add('animate-pop');
                setTimeout(() => {
                    otpInputs[index].classList.remove('animate-pop');
                }, 300);
            }
        });

        this.userData.verificationCode = code;
        setTimeout(() => this.verifyOtp(), 500);
    }

    async verifyOtp() {
        const verifyBtn = document.getElementById('verifyBtn');
        const otpInputs = document.querySelectorAll('.otp-input');

        // Show loading
        if (verifyBtn) {
            verifyBtn.disabled = true;
            verifyBtn.innerHTML = '<span class="animate-rotate">⏳</span> Verifying...';
        }

        // Disable inputs
        otpInputs.forEach(input => input.disabled = true);

        try {
            // Simulate API verification
            await this.simulateApiCall(1500);

            // For demo, accept any 6-digit code
            if (this.userData.verificationCode.length === 6) {
                // Success animation
                otpInputs.forEach((input, index) => {
                    setTimeout(() => {
                        input.classList.add('verified');
                        input.innerHTML = '✓';
                    }, index * 100);
                });

                // Show success message
                this.showNotification('Verification successful! Welcome to ZmartTrade!', 'success');

                // Create user session
                await this.createUserSession();

                // Navigate to chat
                setTimeout(() => {
                    this.app.currentUser = {
                        name: this.userData.name,
                        contact: this.userData.contactType === 'phone'
                            ? this.userData.phoneNumber
                            : this.userData.email,
                        contactType: this.userData.contactType,
                        id: this.generateUserId()
                    };

                    // Save session
                    localStorage.setItem('zmart_session', JSON.stringify({
                        user: this.app.currentUser,
                        expiresAt: Date.now() + (30 * 24 * 60 * 60 * 1000) // 30 days
                    }));

                    this.app.showScreen('chat');
                    this.app.initializeChat();
                }, 1500);

            } else {
                throw new Error('Invalid verification code');
            }

        } catch (error) {
            console.error('Verification error:', error);

            // Show error
            this.showNotification('Invalid verification code. Please try again.', 'error');

            // Clear inputs and shake animation
            otpInputs.forEach(input => {
                input.value = '';
                input.disabled = false;
                input.classList.add('animate-shake', 'border-red-500');
                setTimeout(() => {
                    input.classList.remove('animate-shake', 'border-red-500');
                }, 500);
            });

            // Focus first input
            otpInputs[0]?.focus();

        } finally {
            // Reset verify button
            if (verifyBtn) {
                verifyBtn.disabled = false;
                verifyBtn.innerHTML = 'Verify';
            }
        }
    }

    startResendTimer() {
        const resendBtn = document.getElementById('resendOtpBtn');
        const resendTimer = document.getElementById('resendTimer');
        let timeLeft = this.resendCooldown;

        if (resendBtn) resendBtn.disabled = true;

        // Clear existing timer
        if (this.verificationTimer) {
            clearInterval(this.verificationTimer);
        }

        this.verificationTimer = setInterval(() => {
            timeLeft--;

            if (resendTimer) {
                resendTimer.textContent = `Resend in ${timeLeft}s`;
            }

            if (timeLeft <= 0) {
                clearInterval(this.verificationTimer);
                if (resendTimer) resendTimer.textContent = '';
                if (resendBtn) resendBtn.disabled = false;
            }
        }, 1000);
    }

    async createUserSession() {
        // In production, this would create a user account on the backend
        try {
            await this.simulateApiCall(500);

            // User created successfully
            console.log('User session created:', this.userData);

        } catch (error) {
            console.error('Error creating user session:', error);
            throw error;
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type} animate-slideDown`;
        notification.innerHTML = `
            <div class="notification-content">
                ${this.getNotificationIcon(type)}
                <span>${message}</span>
            </div>
        `;

        // Add to body
        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.classList.add('animate-fadeOut');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    getNotificationIcon(type) {
        switch(type) {
            case 'success': return '✅';
            case 'error': return '❌';
            case 'warning': return '⚠️';
            default: return 'ℹ️';
        }
    }

    playButtonSound() {
        // Add button click sound effect
        // Audio file to be added
    }

    simulateApiCall(delay = 1000) {
        return new Promise(resolve => setTimeout(resolve, delay));
    }

    generateUserId() {
        return `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
}

// Initialize onboarding when app is ready
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        if (window.zmartApp) {
            window.zmartOnboarding = new OnboardingController(window.zmartApp);
        }
    }, 100);
});