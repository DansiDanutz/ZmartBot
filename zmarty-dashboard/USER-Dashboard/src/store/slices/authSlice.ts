import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { authAPI } from '@services/api/auth'
import { User } from '@types/user'

interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null
  loginAttempts: number
  lastLoginAttempt: number | null
}

const initialState: AuthState = {
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  loading: false,
  error: null,
  loginAttempts: 0,
  lastLoginAttempt: null,
}

// Async thunks for authentication
export const login = createAsyncThunk(
  'auth/login',
  async (credentials: { email: string; password: string; rememberMe?: boolean }, { rejectWithValue }) => {
    try {
      const response = await authAPI.login(credentials)
      
      // Store tokens in localStorage if "remember me" is checked
      if (credentials.rememberMe) {
        localStorage.setItem('token', response.access_token)
        localStorage.setItem('refreshToken', response.refresh_token)
      } else {
        // Store in sessionStorage for session-only persistence
        sessionStorage.setItem('token', response.access_token)
        sessionStorage.setItem('refreshToken', response.refresh_token)
      }
      
      return response
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Login failed')
    }
  }
)

export const register = createAsyncThunk(
  'auth/register',
  async (userData: { 
    email: string
    password: string
    username: string
    fullName?: string 
  }, { rejectWithValue }) => {
    try {
      const response = await authAPI.register(userData)
      return response
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Registration failed')
    }
  }
)

export const logout = createAsyncThunk(
  'auth/logout',
  async (_, { getState }) => {
    try {
      const state = getState() as { auth: AuthState }
      if (state.auth.token) {
        await authAPI.logout()
      }
    } catch (error) {
      console.warn('Logout API call failed:', error)
    } finally {
      // Always clear local storage
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      sessionStorage.removeItem('token')
      sessionStorage.removeItem('refreshToken')
    }
  }
)

export const refreshTokenThunk = createAsyncThunk(
  'auth/refreshToken',
  async (_, { getState, rejectWithValue }) => {
    try {
      const state = getState() as { auth: AuthState }
      if (!state.auth.refreshToken) {
        throw new Error('No refresh token available')
      }
      
      const response = await authAPI.refreshToken(state.auth.refreshToken)
      
      // Update stored tokens
      const storage = localStorage.getItem('token') ? localStorage : sessionStorage
      storage.setItem('token', response.access_token)
      if (response.refresh_token) {
        storage.setItem('refreshToken', response.refresh_token)
      }
      
      return response
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Token refresh failed')
    }
  }
)

export const checkAuthStatus = createAsyncThunk(
  'auth/checkStatus',
  async (_, { dispatch, rejectWithValue }) => {
    try {
      // Check for stored tokens
      const token = localStorage.getItem('token') || sessionStorage.getItem('token')
      const refreshToken = localStorage.getItem('refreshToken') || sessionStorage.getItem('refreshToken')
      
      if (!token) {
        throw new Error('No token found')
      }
      
      // Validate token with API
      const user = await authAPI.getCurrentUser()
      
      return {
        user,
        token,
        refreshToken,
      }
    } catch (error: any) {
      // Try to refresh token if available
      const refreshToken = localStorage.getItem('refreshToken') || sessionStorage.getItem('refreshToken')
      if (refreshToken) {
        try {
          await dispatch(refreshTokenThunk())
          const user = await authAPI.getCurrentUser()
          const newToken = localStorage.getItem('token') || sessionStorage.getItem('token')
          return {
            user,
            token: newToken,
            refreshToken,
          }
        } catch (refreshError) {
          // Clear invalid tokens
          localStorage.removeItem('token')
          localStorage.removeItem('refreshToken')
          sessionStorage.removeItem('token')
          sessionStorage.removeItem('refreshToken')
        }
      }
      
      return rejectWithValue('Authentication check failed')
    }
  }
)

export const forgotPassword = createAsyncThunk(
  'auth/forgotPassword',
  async (email: string, { rejectWithValue }) => {
    try {
      await authAPI.forgotPassword(email)
      return email
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to send reset email')
    }
  }
)

export const resetPassword = createAsyncThunk(
  'auth/resetPassword',
  async (data: { token: string; password: string }, { rejectWithValue }) => {
    try {
      await authAPI.resetPassword(data.token, data.password)
      return true
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Password reset failed')
    }
  }
)

export const updateProfile = createAsyncThunk(
  'auth/updateProfile',
  async (profileData: Partial<User>, { rejectWithValue }) => {
    try {
      const updatedUser = await authAPI.updateProfile(profileData)
      return updatedUser
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Profile update failed')
    }
  }
)

// Auth slice
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
    updateUser: (state, action: PayloadAction<Partial<User>>) => {
      if (state.user) {
        state.user = { ...state.user, ...action.payload }
      }
    },
    resetLoginAttempts: (state) => {
      state.loginAttempts = 0
      state.lastLoginAttempt = null
    },
  },
  extraReducers: (builder) => {
    // Login
    builder
      .addCase(login.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false
        state.user = action.payload.user
        state.token = action.payload.access_token
        state.refreshToken = action.payload.refresh_token
        state.isAuthenticated = true
        state.error = null
        state.loginAttempts = 0
        state.lastLoginAttempt = null
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
        state.loginAttempts += 1
        state.lastLoginAttempt = Date.now()
      })
    
    // Register
    builder
      .addCase(register.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(register.fulfilled, (state, action) => {
        state.loading = false
        state.user = action.payload.user
        state.token = action.payload.access_token
        state.refreshToken = action.payload.refresh_token
        state.isAuthenticated = true
        state.error = null
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })
    
    // Logout
    builder
      .addCase(logout.fulfilled, (state) => {
        state.user = null
        state.token = null
        state.refreshToken = null
        state.isAuthenticated = false
        state.loading = false
        state.error = null
        state.loginAttempts = 0
        state.lastLoginAttempt = null
      })
    
    // Token refresh
    builder
      .addCase(refreshTokenThunk.fulfilled, (state, action) => {
        state.token = action.payload.access_token
        if (action.payload.refresh_token) {
          state.refreshToken = action.payload.refresh_token
        }
        state.error = null
      })
      .addCase(refreshTokenThunk.rejected, (state) => {
        state.user = null
        state.token = null
        state.refreshToken = null
        state.isAuthenticated = false
      })
    
    // Check auth status
    builder
      .addCase(checkAuthStatus.pending, (state) => {
        state.loading = true
      })
      .addCase(checkAuthStatus.fulfilled, (state, action) => {
        state.loading = false
        state.user = action.payload.user
        state.token = action.payload.token
        state.refreshToken = action.payload.refreshToken
        state.isAuthenticated = true
        state.error = null
      })
      .addCase(checkAuthStatus.rejected, (state) => {
        state.loading = false
        state.user = null
        state.token = null
        state.refreshToken = null
        state.isAuthenticated = false
      })
    
    // Forgot password
    builder
      .addCase(forgotPassword.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(forgotPassword.fulfilled, (state) => {
        state.loading = false
        state.error = null
      })
      .addCase(forgotPassword.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })
    
    // Reset password
    builder
      .addCase(resetPassword.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(resetPassword.fulfilled, (state) => {
        state.loading = false
        state.error = null
      })
      .addCase(resetPassword.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })
    
    // Update profile
    builder
      .addCase(updateProfile.fulfilled, (state, action) => {
        state.user = action.payload
        state.error = null
      })
      .addCase(updateProfile.rejected, (state, action) => {
        state.error = action.payload as string
      })
  },
})

export const { clearError, updateUser, resetLoginAttempts } = authSlice.actions
export default authSlice.reducer