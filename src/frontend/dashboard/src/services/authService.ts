import axios from 'axios'

// Types
export interface User {
  id: string
  username: string
  email: string
  full_name: string
  role: string
  created_at: string
  last_login?: string
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
  full_name: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface AuthState {
  user: User | null
  tokens: AuthTokens | null
  isAuthenticated: boolean
  isLoading: boolean
}

// API base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance with interceptors
const authApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
authApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle token refresh
authApi.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await authApi.post('/auth/refresh', {
            refresh_token: refreshToken,
          })
          
          const { access_token, refresh_token } = response.data
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)
          
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return authApi(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

// Authentication service
class AuthService {
  private static instance: AuthService
  private authState: AuthState = {
    user: null,
    tokens: null,
    isAuthenticated: false,
    isLoading: true,
  }

  private listeners: ((state: AuthState) => void)[] = []

  private constructor() {
    this.initializeAuth()
  }

  static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService()
    }
    return AuthService.instance
  }

  private initializeAuth(): void {
    const accessToken = localStorage.getItem('access_token')
    const user = localStorage.getItem('user')

    if (accessToken && user) {
      try {
        this.authState.user = JSON.parse(user)
        this.authState.tokens = {
          access_token: accessToken,
          refresh_token: localStorage.getItem('refresh_token') || '',
          token_type: 'bearer',
          expires_in: 3600,
        }
        this.authState.isAuthenticated = true
      } catch (error) {
        console.error('Error parsing stored auth data:', error)
        this.clearAuth()
      }
    }

    this.authState.isLoading = false
    this.notifyListeners()
  }

  private notifyListeners(): void {
    this.listeners.forEach(listener => listener(this.authState))
  }

  subscribe(listener: (state: AuthState) => void): () => void {
    this.listeners.push(listener)
    listener(this.authState) // Initial call

    return () => {
      const index = this.listeners.indexOf(listener)
      if (index > -1) {
        this.listeners.splice(index, 1)
      }
    }
  }

  async login(credentials: LoginCredentials): Promise<User> {
    try {
      this.authState.isLoading = true
      this.notifyListeners()

      const response = await authApi.post('/auth/login', credentials)
      const { access_token, refresh_token, token_type, expires_in } = response.data

      // Store tokens
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)

      // Get user profile
      const userResponse = await authApi.get('/auth/profile')
      const user = userResponse.data

      // Store user data
      localStorage.setItem('user', JSON.stringify(user))

      // Update state
      this.authState.user = user
      this.authState.tokens = { access_token, refresh_token, token_type, expires_in }
      this.authState.isAuthenticated = true
      this.authState.isLoading = false

      this.notifyListeners()
      return user
    } catch (error) {
      this.authState.isLoading = false
      this.notifyListeners()
      throw error
    }
  }

  async register(userData: RegisterData): Promise<User> {
    try {
      this.authState.isLoading = true
      this.notifyListeners()

      const response = await authApi.post('/auth/register', userData)
      const { access_token, refresh_token, token_type, expires_in } = response.data

      // Store tokens
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)

      // Get user profile
      const userResponse = await authApi.get('/auth/profile')
      const user = userResponse.data

      // Store user data
      localStorage.setItem('user', JSON.stringify(user))

      // Update state
      this.authState.user = user
      this.authState.tokens = { access_token, refresh_token, token_type, expires_in }
      this.authState.isAuthenticated = true
      this.authState.isLoading = false

      this.notifyListeners()
      return user
    } catch (error) {
      this.authState.isLoading = false
      this.notifyListeners()
      throw error
    }
  }

  async logout(): Promise<void> {
    try {
      await authApi.post('/auth/logout')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      this.clearAuth()
    }
  }

  private clearAuth(): void {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')

    this.authState.user = null
    this.authState.tokens = null
    this.authState.isAuthenticated = false
    this.authState.isLoading = false

    this.notifyListeners()
  }

  async getProfile(): Promise<User> {
    const response = await authApi.get('/auth/profile')
    const user = response.data
    
    // Update stored user data
    localStorage.setItem('user', JSON.stringify(user))
    this.authState.user = user
    this.notifyListeners()
    
    return user
  }

  async updateProfile(profileData: Partial<User>): Promise<User> {
    const response = await authApi.put('/auth/profile', profileData)
    const user = response.data
    
    // Update stored user data
    localStorage.setItem('user', JSON.stringify(user))
    this.authState.user = user
    this.notifyListeners()
    
    return user
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await authApi.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    })
  }

  getAuthState(): AuthState {
    return { ...this.authState }
  }

  isAuthenticated(): boolean {
    return this.authState.isAuthenticated
  }

  getUser(): User | null {
    return this.authState.user
  }
}

export default AuthService.getInstance() 