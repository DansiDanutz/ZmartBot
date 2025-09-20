// ZmartyChat Onboarding JavaScript
class ZmartyChatOnboarding {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 6;
        this.formData = {
            accountType: '',
            personalInfo: {},
            documents: {},
            profile: {},
            security: {}
        };
        this.selectedDocumentType = '';
        this.cameraStream = null;

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.updateProgress();
        this.setupValidation();
        this.loadSavedData();
    }

    setupEventListeners() {
        // Navigation buttons
        const nextBtn = document.getElementById('nextBtn');
        const backBtn = document.getElementById('backBtn');

        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.handleNext());
        }

        if (backBtn) {
            backBtn.addEventListener('click', () => this.handleBack());
        }

        // Account type selection
        document.querySelectorAll('.select-plan-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const plan = btn.getAttribute('data-plan');
                this.selectPlan(plan);
            });
        });

        // Document type selection
        document.querySelectorAll('.document-type').forEach(card => {
            card.addEventListener('click', () => {
                this.selectDocumentType(card);
            });
        });

        // File upload handlers
        this.setupFileUploadHandlers();

        // Camera handlers
        this.setupCameraHandlers();

        // Form validation handlers
        this.setupFormHandlers();

        // 2FA toggle
        const enable2FA = document.getElementById('enable2FA');
        if (enable2FA) {
            enable2FA.addEventListener('change', (e) => {
                this.toggle2FA(e.target.checked);
            });
        }

        // Auth method selection
        document.querySelectorAll('.auth-method').forEach(method => {
            method.addEventListener('click', () => {
                this.selectAuthMethod(method);
            });
        });

        // Email verification
        const verifyEmail = document.getElementById('verifyEmail');
        if (verifyEmail) {
            verifyEmail.addEventListener('click', () => this.sendEmailVerification());
        }

        // Progress step clicks
        document.querySelectorAll('.step').forEach(step => {
            step.addEventListener('click', () => {
                const stepNum = parseInt(step.getAttribute('data-step'));
                if (stepNum <= this.currentStep) {
                    this.goToStep(stepNum);
                }
            });
        });
    }

    setupValidation() {
        // Real-time form validation
        const emailInput = document.getElementById('email');
        if (emailInput) {
            emailInput.addEventListener('blur', () => this.validateEmail(emailInput));
        }

        const passwordInput = document.getElementById('password');
        if (passwordInput) {
            passwordInput.addEventListener('input', () => this.checkPasswordStrength(passwordInput));
        }

        const confirmPasswordInput = document.getElementById('confirmPassword');
        if (confirmPasswordInput) {
            confirmPasswordInput.addEventListener('blur', () => this.validatePasswordMatch());
        }

        // Date of birth validation
        const dobInput = document.getElementById('dateOfBirth');
        if (dobInput) {
            dobInput.addEventListener('change', () => this.validateAge(dobInput));
        }
    }

    setupFormHandlers() {
        const accountForm = document.getElementById('accountForm');
        if (accountForm) {
            accountForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveAccountData();
            });
        }

        const profileForm = document.getElementById('profileForm');
        if (profileForm) {
            profileForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveProfileData();
            });
        }
    }

    setupFileUploadHandlers() {
        // Front document upload
        const frontUpload = document.getElementById('frontUpload');
        const frontFile = document.getElementById('frontFile');

        if (frontUpload && frontFile) {
            const uploadBtn = frontUpload.querySelector('.upload-btn');
            uploadBtn.addEventListener('click', () => frontFile.click());

            frontFile.addEventListener('change', (e) => {
                this.handleFileUpload(e, 'front');
            });

            // Drag and drop
            frontUpload.addEventListener('dragover', (e) => {
                e.preventDefault();
                frontUpload.classList.add('dragover');
            });

            frontUpload.addEventListener('dragleave', () => {
                frontUpload.classList.remove('dragover');
            });

            frontUpload.addEventListener('drop', (e) => {
                e.preventDefault();
                frontUpload.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.processFile(files[0], 'front');
                }
            });
        }

        // Back document upload (similar setup)
        const backUpload = document.getElementById('backUpload');
        const backFile = document.getElementById('backFile');

        if (backUpload && backFile) {
            const uploadBtn = backUpload.querySelector('.upload-btn');
            uploadBtn.addEventListener('click', () => backFile.click());

            backFile.addEventListener('change', (e) => {
                this.handleFileUpload(e, 'back');
            });

            backUpload.addEventListener('dragover', (e) => {
                e.preventDefault();
                backUpload.classList.add('dragover');
            });

            backUpload.addEventListener('dragleave', () => {
                backUpload.classList.remove('dragover');
            });

            backUpload.addEventListener('drop', (e) => {
                e.preventDefault();
                backUpload.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.processFile(files[0], 'back');
                }
            });
        }
    }

    setupCameraHandlers() {
        const startCamera = document.getElementById('startCamera');
        const captureBtn = document.getElementById('captureBtn');
        const retakeBtn = document.getElementById('retakeBtn');

        if (startCamera) {
            startCamera.addEventListener('click', () => this.startCamera());
        }

        if (captureBtn) {
            captureBtn.addEventListener('click', () => this.capturePhoto());
        }

        if (retakeBtn) {
            retakeBtn.addEventListener('click', () => this.retakePhoto());
        }
    }

    handleNext() {
        if (this.validateCurrentStep()) {
            this.saveCurrentStepData();

            if (this.currentStep === 3) {
                // Simulate KYC verification process
                this.processKYCVerification();
            } else if (this.currentStep < this.totalSteps) {
                this.currentStep++;
                this.updateView();
            }
        }
    }

    handleBack() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.updateView();
        }
    }

    goToStep(stepNum) {
        if (stepNum >= 1 && stepNum <= this.totalSteps && stepNum <= this.currentStep) {
            this.currentStep = stepNum;
            this.updateView();
        }
    }

    updateView() {
        // Hide all step contents
        document.querySelectorAll('.step-content').forEach(content => {
            content.classList.remove('active');
        });

        // Show current step content
        const currentContent = document.getElementById(`step-${this.currentStep}`);
        if (currentContent) {
            currentContent.classList.add('active');
        }

        // Update progress
        this.updateProgress();

        // Update navigation buttons
        this.updateNavigationButtons();

        // Update step indicators
        this.updateStepIndicators();
    }

    updateProgress() {
        const progressFill = document.getElementById('progressFill');
        if (progressFill) {
            const percentage = (this.currentStep / this.totalSteps) * 100;
            progressFill.style.width = `${percentage}%`;
        }
    }

    updateNavigationButtons() {
        const nextBtn = document.getElementById('nextBtn');
        const backBtn = document.getElementById('backBtn');

        // Update back button
        if (backBtn) {
            backBtn.style.display = this.currentStep === 1 ? 'none' : 'block';
        }

        // Update next button
        if (nextBtn) {
            if (this.currentStep === this.totalSteps) {
                nextBtn.style.display = 'none';
            } else {
                nextBtn.style.display = 'block';
                nextBtn.textContent = this.currentStep === this.totalSteps - 1 ? 'Complete' : 'Next →';
            }
        }
    }

    updateStepIndicators() {
        document.querySelectorAll('.step').forEach(step => {
            const stepNum = parseInt(step.getAttribute('data-step'));

            step.classList.remove('active', 'completed');

            if (stepNum < this.currentStep) {
                step.classList.add('completed');
            } else if (stepNum === this.currentStep) {
                step.classList.add('active');
            }
        });
    }

    selectPlan(plan) {
        this.formData.accountType = plan;

        // Visual feedback
        document.querySelectorAll('.account-type-card').forEach(card => {
            card.classList.remove('selected');
        });

        const selectedCard = document.querySelector(`.account-type-card[data-type="${plan}"]`);
        if (selectedCard) {
            selectedCard.classList.add('selected');
        }

        // Auto-advance to next step
        setTimeout(() => {
            this.handleNext();
        }, 300);
    }

    selectDocumentType(card) {
        // Remove previous selection
        document.querySelectorAll('.document-type').forEach(doc => {
            doc.classList.remove('selected');
        });

        // Add selection
        card.classList.add('selected');
        this.selectedDocumentType = card.getAttribute('data-type');

        // Show next KYC step
        document.getElementById('kycStep1').classList.remove('active');
        document.getElementById('kycStep2').classList.add('active');
    }

    handleFileUpload(event, side) {
        const file = event.target.files[0];
        if (file) {
            this.processFile(file, side);
        }
    }

    processFile(file, side) {
        if (!file.type.startsWith('image/')) {
            this.showError('Please upload an image file');
            return;
        }

        if (file.size > 10 * 1024 * 1024) { // 10MB limit
            this.showError('File size must be less than 10MB');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const uploadArea = document.getElementById(`${side}Upload`);
            const placeholder = uploadArea.querySelector('.upload-placeholder');
            const preview = uploadArea.querySelector('.upload-preview');
            const previewImg = document.getElementById(`${side}Preview`);

            placeholder.style.display = 'none';
            preview.style.display = 'block';
            previewImg.src = e.target.result;

            // Save file data
            this.formData.documents[side] = {
                data: e.target.result,
                name: file.name,
                size: file.size
            };

            // Check if both sides uploaded
            if (this.formData.documents.front && this.formData.documents.back) {
                setTimeout(() => {
                    document.getElementById('kycStep2').classList.remove('active');
                    document.getElementById('kycStep3').classList.add('active');
                }, 500);
            }
        };

        reader.readAsDataURL(file);
    }

    removeFile(side) {
        const uploadArea = document.getElementById(`${side}Upload`);
        const placeholder = uploadArea.querySelector('.upload-placeholder');
        const preview = uploadArea.querySelector('.upload-preview');

        placeholder.style.display = 'block';
        preview.style.display = 'none';

        delete this.formData.documents[side];
    }

    async startCamera() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'user' }
            });

            this.cameraStream = stream;

            const cameraFeed = document.getElementById('cameraFeed');
            const cameraPlaceholder = document.getElementById('cameraPlaceholder');
            const captureControls = document.getElementById('captureControls');

            if (cameraFeed) {
                cameraFeed.srcObject = stream;
                cameraFeed.style.display = 'block';
                cameraPlaceholder.style.display = 'none';
                captureControls.style.display = 'flex';
            }
        } catch (error) {
            console.error('Camera access error:', error);
            this.showError('Unable to access camera. Please check permissions.');
        }
    }

    capturePhoto() {
        const video = document.getElementById('cameraFeed');
        const canvas = document.getElementById('captureCanvas');
        const selfiePreview = document.getElementById('selfiePreview');
        const selfieImage = document.getElementById('selfieImage');
        const captureControls = document.getElementById('captureControls');

        if (video && canvas) {
            const context = canvas.getContext('2d');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            context.drawImage(video, 0, 0);

            const imageData = canvas.toDataURL('image/jpeg');

            // Save selfie
            this.formData.documents.selfie = {
                data: imageData,
                timestamp: new Date().toISOString()
            };

            // Show preview
            selfieImage.src = imageData;
            selfiePreview.style.display = 'block';
            captureControls.style.display = 'none';

            // Stop camera
            this.stopCamera();
        }
    }

    retakePhoto() {
        const selfiePreview = document.getElementById('selfiePreview');
        selfiePreview.style.display = 'none';

        delete this.formData.documents.selfie;

        this.startCamera();
    }

    confirmSelfie() {
        // Move to verification step
        document.getElementById('kycStep3').classList.remove('active');
        document.getElementById('kycStep4').classList.add('active');

        // Start verification animation
        this.simulateVerification();
    }

    stopCamera() {
        if (this.cameraStream) {
            this.cameraStream.getTracks().forEach(track => track.stop());
            this.cameraStream = null;

            const cameraFeed = document.getElementById('cameraFeed');
            if (cameraFeed) {
                cameraFeed.srcObject = null;
                cameraFeed.style.display = 'none';
            }
        }
    }

    processKYCVerification() {
        this.showLoadingOverlay(true);

        // Move to verification status step
        document.getElementById('kycStep3').classList.remove('active');
        document.getElementById('kycStep4').classList.add('active');

        // Simulate verification process
        this.simulateVerification();
    }

    simulateVerification() {
        const steps = [
            { id: 1, delay: 1000 },
            { id: 2, delay: 3000 },
            { id: 3, delay: 5000 },
            { id: 4, delay: 7000 }
        ];

        const statusSteps = document.querySelectorAll('.status-step');

        steps.forEach(({ id, delay }) => {
            setTimeout(() => {
                if (statusSteps[id - 1]) {
                    statusSteps[id - 1].classList.remove('active');
                    statusSteps[id - 1].classList.add('completed');
                }

                if (statusSteps[id] && id < 4) {
                    statusSteps[id].classList.add('active');
                }

                if (id === 4) {
                    this.showLoadingOverlay(false);
                    this.showSuccess('Verification Complete!');
                    setTimeout(() => {
                        this.currentStep++;
                        this.updateView();
                    }, 1500);
                }
            }, delay);
        });
    }

    toggle2FA(enabled) {
        const twoFASetup = document.getElementById('twoFASetup');
        if (twoFASetup) {
            twoFASetup.style.display = enabled ? 'block' : 'none';
        }

        this.formData.security.twoFAEnabled = enabled;
    }

    selectAuthMethod(method) {
        const methodType = method.getAttribute('data-method');

        // Remove previous selection
        document.querySelectorAll('.auth-method').forEach(m => {
            m.classList.remove('selected');
        });

        method.classList.add('selected');

        if (methodType === 'app') {
            // Show QR code setup
            const qrSetup = document.getElementById('qrSetup');
            if (qrSetup) {
                qrSetup.style.display = 'block';
                this.generateQRCode();
            }
        } else if (methodType === 'sms') {
            // Show SMS verification
            this.setupSMSVerification();
        }
    }

    generateQRCode() {
        // In production, this would generate an actual QR code
        console.log('Generating QR code for 2FA setup');
        this.formData.security.authMethod = 'app';
    }

    setupSMSVerification() {
        // In production, this would send SMS verification
        console.log('Setting up SMS verification');
        this.formData.security.authMethod = 'sms';
    }

    sendEmailVerification() {
        const verifyEmailBtn = document.getElementById('verifyEmail');
        const emailVerification = document.getElementById('emailVerification');
        const userEmail = document.getElementById('userEmail');

        if (verifyEmailBtn) {
            verifyEmailBtn.disabled = true;
            verifyEmailBtn.textContent = 'Sending...';
        }

        // Simulate sending email
        setTimeout(() => {
            if (emailVerification && userEmail) {
                const email = this.formData.personalInfo.email || 'your@email.com';
                userEmail.textContent = email;
                emailVerification.style.display = 'block';
            }

            if (verifyEmailBtn) {
                verifyEmailBtn.style.display = 'none';
            }

            this.showSuccess('Verification email sent!');
        }, 1500);
    }

    validateCurrentStep() {
        switch (this.currentStep) {
            case 1:
                return this.formData.accountType !== '';

            case 2:
                return this.validateAccountForm();

            case 3:
                return true; // KYC validation handled separately

            case 4:
                return this.validateProfileForm();

            case 5:
                return true; // Security setup is optional

            default:
                return true;
        }
    }

    validateAccountForm() {
        const form = document.getElementById('accountForm');
        if (!form) return true;

        const requiredFields = ['firstName', 'lastName', 'email', 'dateOfBirth', 'country', 'password', 'confirmPassword', 'terms'];
        let isValid = true;

        requiredFields.forEach(fieldName => {
            const field = form.elements[fieldName];
            if (field) {
                if (!field.value || (field.type === 'checkbox' && !field.checked)) {
                    this.showFieldError(field, 'This field is required');
                    isValid = false;
                } else {
                    this.clearFieldError(field);
                }
            }
        });

        // Additional validations
        if (isValid) {
            const email = form.elements['email'];
            if (email && !this.isValidEmail(email.value)) {
                this.showFieldError(email, 'Please enter a valid email address');
                isValid = false;
            }

            const password = form.elements['password'];
            const confirmPassword = form.elements['confirmPassword'];
            if (password && confirmPassword && password.value !== confirmPassword.value) {
                this.showFieldError(confirmPassword, 'Passwords do not match');
                isValid = false;
            }
        }

        return isValid;
    }

    validateProfileForm() {
        const form = document.getElementById('profileForm');
        if (!form) return true;

        const experience = form.elements['experience'];
        const investmentSize = form.elements['investmentSize'];

        let isValid = true;

        if (!experience || !this.getSelectedRadio('experience')) {
            isValid = false;
            this.showError('Please select your trading experience level');
        }

        if (!investmentSize || !investmentSize.value) {
            isValid = false;
            this.showError('Please select your investment size');
        }

        return isValid;
    }

    getSelectedRadio(name) {
        const radios = document.getElementsByName(name);
        for (const radio of radios) {
            if (radio.checked) {
                return radio.value;
            }
        }
        return null;
    }

    validateEmail(input) {
        const email = input.value;
        if (!this.isValidEmail(email)) {
            this.showFieldError(input, 'Please enter a valid email address');
            return false;
        }

        this.clearFieldError(input);
        return true;
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    checkPasswordStrength(input) {
        const password = input.value;
        const strengthBar = document.querySelector('.strength-fill');
        const strengthText = document.querySelector('.strength-text');

        if (!strengthBar || !strengthText) return;

        let strength = 0;

        // Check length
        if (password.length >= 8) strength++;
        if (password.length >= 12) strength++;

        // Check for uppercase
        if (/[A-Z]/.test(password)) strength++;

        // Check for lowercase
        if (/[a-z]/.test(password)) strength++;

        // Check for numbers
        if (/[0-9]/.test(password)) strength++;

        // Check for special characters
        if (/[^A-Za-z0-9]/.test(password)) strength++;

        // Update UI
        strengthBar.className = 'strength-fill';

        if (strength <= 2) {
            strengthBar.classList.add('weak');
            strengthText.textContent = 'Weak password';
        } else if (strength <= 4) {
            strengthBar.classList.add('medium');
            strengthText.textContent = 'Medium strength';
        } else {
            strengthBar.classList.add('strong');
            strengthText.textContent = 'Strong password';
        }
    }

    validatePasswordMatch() {
        const password = document.getElementById('password');
        const confirmPassword = document.getElementById('confirmPassword');

        if (!password || !confirmPassword) return;

        if (password.value !== confirmPassword.value) {
            this.showFieldError(confirmPassword, 'Passwords do not match');
            return false;
        }

        this.clearFieldError(confirmPassword);
        return true;
    }

    validateAge(input) {
        const dob = new Date(input.value);
        const today = new Date();
        const age = Math.floor((today - dob) / (365.25 * 24 * 60 * 60 * 1000));

        if (age < 18) {
            this.showFieldError(input, 'You must be at least 18 years old');
            return false;
        }

        this.clearFieldError(input);
        return true;
    }

    saveCurrentStepData() {
        switch (this.currentStep) {
            case 1:
                // Account type already saved
                break;

            case 2:
                this.saveAccountData();
                break;

            case 4:
                this.saveProfileData();
                break;

            case 5:
                this.saveSecurityData();
                break;
        }

        // Save to localStorage
        this.saveToLocalStorage();
    }

    saveAccountData() {
        const form = document.getElementById('accountForm');
        if (!form) return;

        const formData = new FormData(form);
        this.formData.personalInfo = {
            firstName: formData.get('firstName'),
            lastName: formData.get('lastName'),
            email: formData.get('email'),
            phone: formData.get('phone'),
            dateOfBirth: formData.get('dateOfBirth'),
            country: formData.get('country'),
            marketing: formData.get('marketing') === 'on'
        };
    }

    saveProfileData() {
        const form = document.getElementById('profileForm');
        if (!form) return;

        const formData = new FormData(form);
        this.formData.profile = {
            experience: this.getSelectedRadio('experience'),
            investmentSize: formData.get('investmentSize'),
            interests: this.getCheckedValues('interests'),
            notifications: this.getCheckedValues('notifications'),
            alertTypes: this.getCheckedValues('alertTypes'),
            referralCode: formData.get('referralCode')
        };
    }

    saveSecurityData() {
        // Security data is saved in real-time during setup
    }

    getCheckedValues(name) {
        const checkboxes = document.getElementsByName(name);
        const values = [];

        checkboxes.forEach(checkbox => {
            if (checkbox.checked) {
                values.push(checkbox.value);
            }
        });

        return values;
    }

    saveToLocalStorage() {
        localStorage.setItem('onboardingData', JSON.stringify(this.formData));
        localStorage.setItem('onboardingStep', this.currentStep.toString());
    }

    loadSavedData() {
        const savedData = localStorage.getItem('onboardingData');
        const savedStep = localStorage.getItem('onboardingStep');

        if (savedData) {
            this.formData = JSON.parse(savedData);
        }

        if (savedStep) {
            const step = parseInt(savedStep);
            if (step > 1 && step <= this.totalSteps) {
                // Ask if user wants to continue
                this.showContinueDialog(step);
            }
        }
    }

    showContinueDialog(savedStep) {
        const continueFromSaved = confirm(`You have a saved onboarding session at step ${savedStep}. Would you like to continue?`);

        if (continueFromSaved) {
            this.currentStep = savedStep;
            this.updateView();
        } else {
            this.clearSavedData();
        }
    }

    clearSavedData() {
        localStorage.removeItem('onboardingData');
        localStorage.removeItem('onboardingStep');
    }

    showFieldError(field, message) {
        const errorElement = document.getElementById(`${field.name}Error`);
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }

        field.classList.add('error');
    }

    clearFieldError(field) {
        const errorElement = document.getElementById(`${field.name}Error`);
        if (errorElement) {
            errorElement.textContent = '';
            errorElement.style.display = 'none';
        }

        field.classList.remove('error');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;

        document.body.appendChild(notification);

        // Add styles for notifications
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'error' ? '#ff4757' : type === 'success' ? '#00ff88' : '#0066ff'};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
            z-index: 10001;
            animation: slideIn 0.3s ease;
        `;

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }

    showLoadingOverlay(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = show ? 'flex' : 'none';
        }
    }
}

// Utility functions
function togglePassword(fieldId) {
    const field = document.getElementById(fieldId);
    if (field) {
        field.type = field.type === 'password' ? 'text' : 'password';
    }
}

function removeFile(side) {
    window.onboarding.removeFile(side);
}

function retakeSelfie() {
    window.onboarding.retakePhoto();
}

function confirmSelfie() {
    window.onboarding.confirmSelfie();
}

function goToDashboard() {
    window.location.href = '/web-app/dashboard.html';
}

function takeTour() {
    // In production, this would start an interactive tour
    alert('Interactive tour coming soon!');
}

// Add animation styles
const animationStyles = `
<style>
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

@keyframes slideOut {
    from {
        transform: translateX(0);
        opacity: 1;
    }
    to {
        transform: translateX(100%);
        opacity: 0;
    }
}

.error {
    border-color: var(--accent-red) !important;
}

.selected {
    border-color: var(--primary-blue) !important;
    background: rgba(0, 102, 255, 0.1) !important;
}
</style>
`;

document.head.insertAdjacentHTML('beforeend', animationStyles);

// Initialize onboarding when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.onboarding = new ZmartyChatOnboarding();
});