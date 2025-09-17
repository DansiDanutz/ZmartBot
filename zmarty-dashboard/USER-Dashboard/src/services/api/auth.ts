import axios from 'axios'
import { 
  AuthResponse, 
  LoginCredentials, 
  RegisterData, 
  User, 
  UpdateProfileData 
} from '@types/user'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

// Create axios instance with default config
const authApiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
})

// Request interceptor to add auth token
authApiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token') || sessionStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for handling auth errors
authApiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        // Try to refresh token
        const refreshToken = localStorage.getItem('refreshToken') || sessionStorage.getItem('refreshToken')
        if (refreshToken) {
          const response = await authApiClient.post('/auth/refresh', {
            refresh_token: refreshToken
          })
          
          const { access_token } = response.data
          
          // Update stored token
          const storage = localStorage.getItem('token') ? localStorage : sessionStorage
          storage.setItem('token', access_token)
          
          // Retry original request
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return authApiClient(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')
        sessionStorage.removeItem('token')
        sessionStorage.removeItem('refreshToken')
        
        if (typeof window !== 'undefined') {
          window.location.href = '/login'
        }
      }
    }
    
    return Promise.reject(error)
  }
)

export const authAPI = {
  // Authentication endpoints
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await authApiClient.post('/auth/login', credentials)
    return response.data
  },

  async register(userData: RegisterData): Promise<AuthResponse> {
    const response = await authApiClient.post('/auth/register', userData)
    return response.data
  },

  async logout(): Promise<void> {
    await authApiClient.post('/auth/logout')
  },

  async refreshToken(refreshToken: string): Promise<{ access_token: string; refresh_token?: string }> {
    const response = await authApiClient.post('/auth/refresh', {
      refresh_token: refreshToken
    })
    return response.data
  },

  async forgotPassword(email: string): Promise<void> {
    await authApiClient.post('/auth/forgot-password', { email })
  },

  async resetPassword(token: string, password: string): Promise<void> {
    await authApiClient.post('/auth/reset-password', { token, password })
  },

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await authApiClient.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    })
  },

  // User profile endpoints
  async getCurrentUser(): Promise<User> {
    const response = await authApiClient.get('/auth/me')
    return response.data
  },

  async updateProfile(profileData: UpdateProfileData): Promise<User> {
    const response = await authApiClient.put('/auth/profile', profileData)
    return response.data
  },

  async uploadAvatar(file: File): Promise<{ avatar_url: string }> {
    const formData = new FormData()
    formData.append('avatar', file)
    
    const response = await authApiClient.post('/auth/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  async deleteAccount(): Promise<void> {
    await authApiClient.delete('/auth/account')
  },

  // Email verification
  async verifyEmail(token: string): Promise<void> {
    await authApiClient.post('/auth/verify-email', { token })
  },

  async resendVerificationEmail(): Promise<void> {
    await authApiClient.post('/auth/resend-verification')
  },

  // Two-factor authentication
  async enableTwoFactor(): Promise<{ qr_code: string; secret: string }> {
    const response = await authApiClient.post('/auth/2fa/enable')
    return response.data
  },

  async confirmTwoFactor(token: string): Promise<void> {
    await authApiClient.post('/auth/2fa/confirm', { token })
  },

  async disableTwoFactor(token: string): Promise<void> {
    await authApiClient.post('/auth/2fa/disable', { token })
  },

  async verifyTwoFactor(token: string): Promise<void> {
    await authApiClient.post('/auth/2fa/verify', { token })
  },

  // Session management
  async getSessions(): Promise<Array<{
    id: string
    device: string
    location: string
    lastActivity: string
    current: boolean
  }>> {
    const response = await authApiClient.get('/auth/sessions')
    return response.data
  },

  async terminateSession(sessionId: string): Promise<void> {
    await authApiClient.delete(`/auth/sessions/${sessionId}`)
  },

  async terminateAllSessions(): Promise<void> {
    await authApiClient.delete('/auth/sessions')
  },

  // Account security
  async getSecurityLog(): Promise<Array<{
    id: string
    event: string
    ipAddress: string
    userAgent: string
    timestamp: string
  }>> {
    const response = await authApiClient.get('/auth/security-log')
    return response.data
  },

  async checkEmailAvailability(email: string): Promise<{ available: boolean }> {
    const response = await authApiClient.post('/auth/check-email', { email })
    return response.data
  },

  async checkUsernameAvailability(username: string): Promise<{ available: boolean }> {
    const response = await authApiClient.post('/auth/check-username', { username })
    return response.data
  },
}

export default authApiClient