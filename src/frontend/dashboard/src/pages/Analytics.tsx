import React from 'react'
import { Helmet } from 'react-helmet-async'

const Analytics: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>Analytics - Zmart Trading Bot</title>
      </Helmet>
      <div>
        <h1 className="text-2xl font-bold text-white">Analytics</h1>
        <p className="text-slate-400">Advanced trading analytics and performance metrics</p>
        <div className="mt-6 bg-slate-800 rounded-lg p-6">
          <p className="text-slate-400">Analytics dashboard coming soon...</p>
        </div>
      </div>
    </>
  )
}

export default Analytics 