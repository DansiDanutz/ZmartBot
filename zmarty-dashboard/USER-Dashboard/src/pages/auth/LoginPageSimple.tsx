import React from 'react'
import { Navigate } from 'react-router-dom'

const LoginPageSimple: React.FC = () => {
  // Auto-redirect to dashboard for demo
  return <Navigate to="/dashboard" replace />
}

export default LoginPageSimple