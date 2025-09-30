import React from 'react'
import { Helmet } from 'react-helmet-async'

const Trading: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>Trading - Zmart Trading Bot</title>
      </Helmet>
      <div>
        <h1 className="text-2xl font-bold text-white">Trading Console</h1>
        <p className="text-slate-400">Advanced trading interface with real-time charts and order management</p>
        <div className="mt-6 bg-slate-800 rounded-lg p-6">
          <p className="text-slate-400">Trading interface coming soon...</p>
        </div>
      </div>
    </>
  )
}

export default Trading 