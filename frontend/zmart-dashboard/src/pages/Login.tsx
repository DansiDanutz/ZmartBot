import React from 'react'
import { Helmet } from 'react-helmet-async'

const Login: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>Login - Zmart Trading Bot</title>
      </Helmet>
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="max-w-md w-full bg-slate-800 rounded-lg shadow-xl p-8">
          <div className="text-center mb-8">
            <div className="mx-auto h-12 w-12 bg-blue-600 rounded-lg flex items-center justify-center mb-4">
              <span className="text-white font-bold text-xl">Z</span>
            </div>
            <h2 className="text-2xl font-bold text-white">Zmart Trading Bot</h2>
            <p className="text-slate-400 mt-2">Sign in to your account</p>
          </div>
          <div className="bg-slate-700 rounded-lg p-6">
            <p className="text-slate-400 text-center">Login interface coming soon...</p>
          </div>
        </div>
      </div>
    </>
  )
}

export default Login 