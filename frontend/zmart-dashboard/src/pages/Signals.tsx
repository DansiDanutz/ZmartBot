import React from 'react'
import { Helmet } from 'react-helmet-async'

const Signals: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>Signals - Zmart Trading Bot</title>
      </Helmet>
      <div>
        <h1 className="text-2xl font-bold text-white">Trading Signals</h1>
        <p className="text-slate-400">Monitor and manage trading signals from multiple sources</p>
        <div className="mt-6 bg-slate-800 rounded-lg p-6">
          <p className="text-slate-400">Signal management interface coming soon...</p>
        </div>
      </div>
    </>
  )
}

export default Signals 