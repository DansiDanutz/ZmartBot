import React, { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion } from 'framer-motion'
import { Eye, EyeOff, Mail, Lock, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'

import { useAppDispatch, useAppSelector } from '@store/hooks'
import { login, resetLoginAttempts } from '@store/slices/authSlice'
import { LoginCredentials } from '@types/user'

// Validation schema
const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Please enter a valid email address'),
  password: z
    .string()
    .min(1, 'Password is required')
    .min(8, 'Password must be at least 8 characters'),
  rememberMe: z.boolean().optional(),
})

type LoginFormData = z.infer<typeof loginSchema>

const LoginPage: React.FC = () => {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const location = useLocation()
  
  const { loading, error, loginAttempts, lastLoginAttempt } = useAppSelector(state => state.auth)
  
  const [showPassword, setShowPassword] = useState(false)
  const [isBlocked, setIsBlocked] = useState(false)
  const [blockTimeLeft, setBlockTimeLeft] = useState(0)
  
  const from = (location.state as any)?.from?.pathname || '/dashboard'
  
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    clearErrors,
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
      rememberMe: false,
    },
  })
  
  // Check if user is temporarily blocked due to failed attempts
  useEffect(() => {
    if (loginAttempts >= 5 && lastLoginAttempt) {
      const blockDuration = 15 * 60 * 1000 // 15 minutes
      const timePassed = Date.now() - lastLoginAttempt
      
      if (timePassed < blockDuration) {
        setIsBlocked(true)
        setBlockTimeLeft(Math.ceil((blockDuration - timePassed) / 1000))
        
        const timer = setInterval(() => {
          const newTimePassed = Date.now() - lastLoginAttempt
          const newTimeLeft = Math.ceil((blockDuration - newTimePassed) / 1000)
          
          if (newTimeLeft <= 0) {
            setIsBlocked(false)
            setBlockTimeLeft(0)
            dispatch(resetLoginAttempts())
            clearInterval(timer)
          } else {
            setBlockTimeLeft(newTimeLeft)
          }
        }, 1000)
        
        return () => clearInterval(timer)
      } else {
        dispatch(resetLoginAttempts())
      }
    }
  }, [loginAttempts, lastLoginAttempt, dispatch])
  
  const formatBlockTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }
  
  const onSubmit = async (data: LoginFormData) => {
    if (isBlocked) return
    
    try {
      const result = await dispatch(login(data)).unwrap()
      toast.success(`Welcome back, ${result.user.fullName || result.user.username}!`)
      navigate(from, { replace: true })
    } catch (error: any) {
      toast.error(error || 'Login failed')
      
      // Clear password field on error
      const passwordField = document.getElementById('password') as HTMLInputElement
      if (passwordField) {
        passwordField.value = ''
      }
    }
  }
  
  return (
    <div className="min-h-screen flex">
      {/* Left side - Login Form */}
      <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8 bg-secondary-900">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-md w-full space-y-8"
        >
          {/* Header */}
          <div className="text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
              className="mx-auto h-16 w-16 bg-primary-600 rounded-2xl flex items-center justify-center mb-6"
            >
              <span className="text-2xl font-bold text-white">Z</span>
            </motion.div>
            
            <h1 className="text-3xl font-bold text-white mb-2">
              Welcome to Zmarty
            </h1>
            <p className="text-secondary-400">
              Sign in to your trading dashboard
            </p>
          </div>
          
          {/* Login Form */}
          <motion.form
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            onSubmit={handleSubmit(onSubmit)}
            className="space-y-6"
          >
            {/* Error Message */}
            {error && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="bg-danger-500 bg-opacity-10 border border-danger-500 border-opacity-30 rounded-lg p-4 flex items-center space-x-3"
              >
                <AlertCircle className="w-5 h-5 text-danger-400 flex-shrink-0" />
                <p className="text-danger-400 text-sm">{error}</p>
              </motion.div>
            )}
            
            {/* Block Message */}
            {isBlocked && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="bg-warning-500 bg-opacity-10 border border-warning-500 border-opacity-30 rounded-lg p-4 flex items-center space-x-3"
              >
                <AlertCircle className="w-5 h-5 text-warning-400 flex-shrink-0" />
                <div>
                  <p className="text-warning-400 text-sm font-medium">
                    Too many failed attempts
                  </p>
                  <p className="text-warning-300 text-xs">
                    Please wait {formatBlockTime(blockTimeLeft)} before trying again
                  </p>
                </div>
              </motion.div>
            )}
            
            {/* Email Field */}
            <div className="space-y-2">
              <label htmlFor="email" className="form-label">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-secondary-400" />
                <input
                  {...register('email')}
                  type="email"
                  id="email"
                  disabled={isBlocked}
                  className={`input-primary pl-10 w-full ${
                    errors.email ? 'border-danger-500 focus:ring-danger-500' : ''
                  }`}
                  placeholder="Enter your email"
                  onChange={() => {
                    clearErrors('email')
                    if (error) {
                      // Clear global error when user starts typing
                    }
                  }}
                />
              </div>
              {errors.email && (
                <p className="form-error">{errors.email.message}</p>
              )}
            </div>
            
            {/* Password Field */}
            <div className="space-y-2">
              <label htmlFor="password" className="form-label">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-secondary-400" />
                <input
                  {...register('password')}
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  disabled={isBlocked}
                  className={`input-primary pl-10 pr-10 w-full ${
                    errors.password ? 'border-danger-500 focus:ring-danger-500' : ''
                  }`}
                  placeholder="Enter your password"
                  onChange={() => {
                    clearErrors('password')
                  }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-secondary-400 hover:text-secondary-300"
                >
                  {showPassword ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="form-error">{errors.password.message}</p>
              )}
            </div>
            
            {/* Remember Me & Forgot Password */}
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  {...register('rememberMe')}
                  id="rememberMe"
                  type="checkbox"
                  disabled={isBlocked}
                  className="h-4 w-4 text-primary-600 border-secondary-600 rounded focus:ring-primary-500 bg-secondary-800"
                />
                <label htmlFor="rememberMe" className="ml-2 text-sm text-secondary-300">
                  Remember me
                </label>
              </div>
              
              <Link
                to="/forgot-password"
                className="text-sm text-primary-400 hover:text-primary-300 transition-colors"
              >
                Forgot password?
              </Link>
            </div>
            
            {/* Submit Button */}
            <button
              type="submit"
              disabled={isSubmitting || loading || isBlocked}
              className="w-full btn-primary py-3 text-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed relative overflow-hidden"
            >
              {isSubmitting || loading ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Signing in...</span>
                </div>
              ) : (
                'Sign In'
              )}
            </button>
            
            {/* Login Attempts Warning */}
            {loginAttempts > 0 && loginAttempts < 5 && !isBlocked && (
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center text-sm text-warning-400"
              >
                {5 - loginAttempts} attempts remaining
              </motion.p>
            )}
          </motion.form>
          
          {/* Sign up link */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-center"
          >
            <p className="text-secondary-400">
              Don't have an account?{' '}
              <Link
                to="/register"
                className="text-primary-400 hover:text-primary-300 font-medium transition-colors"
              >
                Sign up now
              </Link>
            </p>
          </motion.div>
          
          {/* Demo Credentials (Development Only) */}
          {process.env.NODE_ENV === 'development' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="mt-8 p-4 bg-secondary-800 rounded-lg border border-secondary-700"
            >
              <h3 className="text-sm font-medium text-secondary-300 mb-2">
                Demo Credentials
              </h3>
              <div className="text-xs text-secondary-400 space-y-1">
                <p>Email: demo@zmarty.com</p>
                <p>Password: demo123456</p>
              </div>
            </motion.div>
          )}
        </motion.div>
      </div>
      
      {/* Right side - Branding */}
      <div className="hidden lg:flex lg:flex-1 bg-gradient-to-br from-primary-600 to-primary-800 relative overflow-hidden">
        <div className="absolute inset-0 bg-black bg-opacity-20" />
        
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0 bg-repeat" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Ccircle cx='7' cy='7' r='7'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }} />
        </div>
        
        <div className="relative flex items-center justify-center p-12 z-10">
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2, duration: 0.8 }}
            className="text-center max-w-md"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.4, type: 'spring', stiffness: 150 }}
              className="w-20 h-20 bg-white bg-opacity-20 rounded-3xl flex items-center justify-center mx-auto mb-8 backdrop-blur-sm"
            >
              <span className="text-3xl">📊</span>
            </motion.div>
            
            <h2 className="text-4xl font-bold text-white mb-4">
              Professional Trading
            </h2>
            <p className="text-primary-100 text-lg mb-8">
              Access AI-powered insights, real-time market data, and advanced analytics to make informed trading decisions.
            </p>
            
            <div className="space-y-4 text-left">
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 }}
                className="flex items-center space-x-3"
              >
                <div className="w-2 h-2 bg-primary-200 rounded-full" />
                <span className="text-primary-100">AI-powered market analysis</span>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.7 }}
                className="flex items-center space-x-3"
              >
                <div className="w-2 h-2 bg-primary-200 rounded-full" />
                <span className="text-primary-100">Real-time trading signals</span>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.8 }}
                className="flex items-center space-x-3"
              >
                <div className="w-2 h-2 bg-primary-200 rounded-full" />
                <span className="text-primary-100">Advanced portfolio management</span>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}

export default LoginPage