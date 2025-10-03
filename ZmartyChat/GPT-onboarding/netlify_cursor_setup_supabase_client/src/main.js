import { AuthManager, validateEmail, validatePassword } from './lib/auth.js'
import { UIComponents, animateTransition, hideElement, showElement } from './lib/components.js'
import { runOnboardingTests } from './lib/test-suite.js'
import './style.css'

class OnboardingApp {
  constructor() {
    this.authManager = new AuthManager()
    this.uiComponents = new UIComponents()
    this.currentScreen = 'loading'
    this.appElement = document.querySelector('#app')
    this.loadingElement = document.querySelector('#loading')
    
    this.init()
  }

  async init() {
    try {
      // Check if user is already authenticated
      const session = await this.authManager.getCurrentSession()
      
      if (session?.user) {
        this.showDashboard(session.user)
      } else {
        this.showSignUp()
      }
      
      // Setup auth state listener
      this.authManager.onAuthStateChange = (event, user) => {
        if (event === 'signed_in' && user) {
          this.showDashboard(user)
        } else if (event === 'signed_out') {
          this.showSignUp()
        }
      }
      
    } catch (error) {
      console.error('Initialization error:', error)
      this.showMessage('Failed to initialize app. Please refresh the page.', 'error')
      this.showSignUp()
    }
  }

  // Screen management
  showScreen(content, screenName) {
    this.currentScreen = screenName
    
    // Hide loading screen
    if (this.loadingElement) {
      hideElement(this.loadingElement)
    }
    
    // Update app content
    this.appElement.innerHTML = this.uiComponents.createContainer(content)
    animateTransition(this.appElement)
    
    // Setup event listeners for the new screen
    this.setupEventListeners(screenName)
  }

  showLoading() {
    this.currentScreen = 'loading'
    this.appElement.innerHTML = this.uiComponents.createLoadingScreen()
    showElement(this.loadingElement)
  }

  showSignUp() {
    const content = this.uiComponents.createSignUpForm()
    this.showScreen(content, 'signup')
  }

  showSignIn() {
    const content = this.uiComponents.createSignInForm()
    this.showScreen(content, 'signin')
  }

  showEmailVerification(email) {
    const content = this.uiComponents.createEmailVerificationScreen(email)
    this.showScreen(content, 'verification')
  }

  showForgotPassword() {
    const content = this.uiComponents.createForgotPasswordForm()
    this.showScreen(content, 'forgot-password')
  }

  showPasswordReset() {
    const content = this.uiComponents.createPasswordResetForm()
    this.showScreen(content, 'reset-password')
  }

  showDashboard(user) {
    const content = this.uiComponents.createDashboard(user)
    this.showScreen(content, 'dashboard')
  }

  showMessage(message, type = 'info') {
    const messageElement = document.createElement('div')
    messageElement.innerHTML = this.uiComponents.createMessage(message, type)
    messageElement.style.position = 'fixed'
    messageElement.style.top = '20px'
    messageElement.style.right = '20px'
    messageElement.style.zIndex = '1000'
    messageElement.style.maxWidth = '400px'
    
    document.body.appendChild(messageElement)
    
    setTimeout(() => {
      if (document.body.contains(messageElement)) {
        document.body.removeChild(messageElement)
      }
    }, 5000)
  }

  // Event listeners setup
  setupEventListeners(screenName) {
    switch (screenName) {
      case 'signup':
        this.setupSignUpListeners()
        break
      case 'signin':
        this.setupSignInListeners()
        break
      case 'verification':
        this.setupVerificationListeners()
        break
      case 'forgot-password':
        this.setupForgotPasswordListeners()
        break
      case 'reset-password':
        this.setupPasswordResetListeners()
        break
    }
  }

  setupSignUpListeners() {
    const form = document.getElementById('signup-form')
    const passwordInput = document.getElementById('password')
    const confirmPasswordInput = document.getElementById('confirmPassword')
    
    // Password strength indicator
    if (passwordInput) {
      passwordInput.addEventListener('input', (e) => {
        this.updatePasswordStrength(e.target.value)
      })
    }
    
    // Form submission
    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault()
        await this.handleSignUp()
      })
    }
  }

  setupSignInListeners() {
    const form = document.getElementById('signin-form')
    
    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault()
        await this.handleSignIn()
      })
    }
  }

  setupVerificationListeners() {
    const inputs = document.querySelectorAll('.verification-input')
    
    inputs.forEach((input, index) => {
      input.addEventListener('input', (e) => {
        if (e.target.value.length === 1) {
          const nextInput = inputs[index + 1]
          if (nextInput) nextInput.focus()
        }
      })
      
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Backspace' && !e.target.value) {
          const prevInput = inputs[index - 1]
          if (prevInput) prevInput.focus()
        }
      })
    })
  }

  setupForgotPasswordListeners() {
    const form = document.getElementById('forgot-password-form')
    
    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault()
        await this.handleForgotPassword()
      })
    }
  }

  setupPasswordResetListeners() {
    const form = document.getElementById('reset-password-form')
    const passwordInput = document.getElementById('password')
    
    if (passwordInput) {
      passwordInput.addEventListener('input', (e) => {
        this.updatePasswordStrength(e.target.value)
      })
    }
    
    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault()
        await this.handlePasswordReset()
      })
    }
  }

  // Password strength indicator
  updatePasswordStrength(password) {
    const strengthElement = document.getElementById('password-strength')
    const strengthTextElement = document.getElementById('password-strength-text')
    
    if (!strengthElement || !strengthTextElement) return
    
    const validation = validatePassword(password)
    const strengthClass = `strength-${validation.strength}`
    const strengthText = `Password strength: ${validation.strength}`
    
    strengthElement.className = `strength-fill ${strengthClass}`
    strengthTextElement.textContent = strengthText
  }

  // Authentication handlers
  async handleSignUp() {
    const formData = new FormData(document.getElementById('signup-form'))
    const email = formData.get('email')
    const password = formData.get('password')
    const confirmPassword = formData.get('confirmPassword')
    const fullName = formData.get('fullName')
    
    // Validation
    if (!validateEmail(email)) {
      this.showMessage('Please enter a valid email address', 'error')
      return
    }
    
    if (password !== confirmPassword) {
      this.showMessage('Passwords do not match', 'error')
      return
    }
    
    const passwordValidation = validatePassword(password)
    if (!passwordValidation.isValid) {
      this.showMessage('Password must be at least 8 characters with uppercase, lowercase, number, and special character', 'error')
      return
    }
    
    this.showLoading()
    
    const result = await this.authManager.signUp(email, password, { full_name: fullName })
    
    if (result.success) {
      this.showMessage(result.message, 'success')
      this.showEmailVerification(email)
    } else {
      this.showMessage(result.error, 'error')
      this.showSignUp()
    }
  }

  async handleSignIn() {
    const formData = new FormData(document.getElementById('signin-form'))
    const email = formData.get('email')
    const password = formData.get('password')
    
    if (!validateEmail(email)) {
      this.showMessage('Please enter a valid email address', 'error')
      return
    }
    
    this.showLoading()
    
    const result = await this.authManager.signIn(email, password)
    
    if (result.success) {
      this.showMessage(result.message, 'success')
      // Dashboard will be shown automatically via auth state change
    } else {
      this.showMessage(result.error, 'error')
      this.showSignIn()
    }
  }

  async handleForgotPassword() {
    const formData = new FormData(document.getElementById('forgot-password-form'))
    const email = formData.get('email')
    
    if (!validateEmail(email)) {
      this.showMessage('Please enter a valid email address', 'error')
      return
    }
    
    this.showLoading()
    
    const result = await this.authManager.resetPassword(email)
    
    if (result.success) {
      this.showMessage(result.message, 'success')
      this.showSignIn()
    } else {
      this.showMessage(result.error, 'error')
      this.showForgotPassword()
    }
  }

  async handlePasswordReset() {
    const formData = new FormData(document.getElementById('reset-password-form'))
    const password = formData.get('password')
    const confirmPassword = formData.get('confirmPassword')
    
    if (password !== confirmPassword) {
      this.showMessage('Passwords do not match', 'error')
      return
    }
    
    const passwordValidation = validatePassword(password)
    if (!passwordValidation.isValid) {
      this.showMessage('Password must be at least 8 characters with uppercase, lowercase, number, and special character', 'error')
      return
    }
    
    this.showLoading()
    
    const result = await this.authManager.updatePassword(password)
    
    if (result.success) {
      this.showMessage(result.message, 'success')
      // Dashboard will be shown automatically via auth state change
    } else {
      this.showMessage(result.error, 'error')
      this.showPasswordReset()
    }
  }

  async verifyEmail() {
    // In a real app, you would verify the code from the inputs
    // For demo purposes, we'll simulate verification
    const inputs = document.querySelectorAll('.verification-input')
    const code = Array.from(inputs).map(input => input.value).join('')
    
    if (code.length !== 6) {
      this.showMessage('Please enter the complete verification code', 'error')
      return
    }
    
    // Check if email is already verified
    const isVerified = await this.authManager.checkEmailVerified()
    
    if (isVerified) {
      this.showMessage('Email verified successfully!', 'success')
      // Dashboard will be shown automatically via auth state change
    } else {
      this.showMessage('Please check your email and click the verification link', 'info')
    }
  }

  async resendVerification() {
    const session = await this.authManager.getCurrentSession()
    if (session?.user?.email) {
      const result = await this.authManager.resendVerification(session.user.email)
      if (result.success) {
        this.showMessage(result.message, 'success')
      } else {
        this.showMessage(result.error, 'error')
      }
    }
  }

  // Test functionality
  async runTests() {
    console.log('🧪 Starting comprehensive onboarding tests...')
    const testResults = await runOnboardingTests(this)
    this.showTestResults(testResults)
    return testResults
  }

  showTestResults(results) {
    const content = `
      ${this.uiComponents.createHeader('Test Results', 'Comprehensive Onboarding Tests')}
      
      <div class="message ${results.passRate === 100 ? 'success' : results.passRate >= 80 ? 'info' : 'error'}">
        <strong>Test Summary:</strong><br>
        Total Tests: ${results.totalTests}<br>
        Passed: ${results.passedTests} ✅<br>
        Failed: ${results.failedTests} ${results.failedTests > 0 ? '❌' : ''}<br>
        Pass Rate: ${results.passRate}%
      </div>
      
      <div style="text-align: left; margin: 20px 0;">
        <h3>Test Details:</h3>
        ${results.results.map(test => `
          <div style="margin: 10px 0; padding: 10px; border-left: 4px solid ${test.status === 'PASSED' ? '#10b981' : '#ef4444'}; background: ${test.status === 'PASSED' ? '#f0fdf4' : '#fef2f2'};">
            <strong>${test.name}</strong> - ${test.status} (${test.duration})
            ${test.details.length > 0 ? `<br><small>${test.details.join(', ')}</small>` : ''}
          </div>
        `).join('')}
      </div>
      
      <button class="btn btn-primary" onclick="window.app.showSignUp()">
        Back to Onboarding
      </button>
      
      <button class="btn btn-secondary" onclick="window.app.runTests()" style="margin-left: 10px;">
        Run Tests Again
      </button>
    `
    
    this.showScreen(content, 'test-results')
  }
}

// Global functions for onclick handlers
window.showSignUp = () => app.showSignUp()
window.showSignIn = () => app.showSignIn()
window.showForgotPassword = () => app.showForgotPassword()
window.verifyEmail = () => app.verifyEmail()
window.resendVerification = () => app.resendVerification()
window.runTests = () => app.runTests()

// Initialize the app
const app = new OnboardingApp()
window.authManager = app.authManager
window.app = app

// Handle Google Sign-in
window.onGoogleSignIn = async (response) => {
  try {
    app.showLoading()
    const result = await app.authManager.signInWithGoogle()
    if (result.success) {
      app.showMessage('Redirecting to Google...', 'info')
    } else {
      app.showMessage(result.error, 'error')
      app.showSignIn()
    }
  } catch (error) {
    app.showMessage('Google sign-in failed', 'error')
    app.showSignIn()
  }
}

// Initialize Google Sign-in when available
window.addEventListener('load', () => {
  if (window.google) {
    window.google.accounts.id.initialize({
      client_id: '966065216838-fu5fmuckc7n4e9pjbvg4o1m9vo6d9uur.apps.googleusercontent.com',
      callback: window.onGoogleSignIn
    })
    
    window.google.accounts.id.renderButton(
      document.getElementById('google-signin-button'),
      {
        theme: 'outline',
        size: 'large',
        width: '100%'
      }
    )
  }
})// Cache bust: 1759110278
