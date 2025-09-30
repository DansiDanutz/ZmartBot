import React from 'react'
import { Helmet } from 'react-helmet-async'

const Settings: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>Settings - Zmart Trading Bot</title>
      </Helmet>
      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-slate-400">Configure your trading bot and account preferences</p>
        <div className="mt-6 bg-slate-800 rounded-lg p-6">
          <p className="text-slate-400">Settings interface coming soon...</p>
        </div>
      </div>
    </>
  )
}

export default Settings 