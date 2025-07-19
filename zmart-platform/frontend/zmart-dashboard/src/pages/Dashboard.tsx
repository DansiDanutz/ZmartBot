import { DollarSign, TrendingUp, Activity, AlertTriangle } from 'lucide-react'

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-neutral-50">Dashboard</h1>
        <p className="text-neutral-400 mt-2">Welcome to the Zmart Trading Bot Platform</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-neutral-400">Portfolio Value</p>
              <p className="text-2xl font-bold text-neutral-50">$125,430</p>
              <p className="text-sm text-success-400">+2.5% today</p>
            </div>
            <div className="p-3 bg-primary-500/10 rounded-lg">
              <DollarSign className="h-6 w-6 text-primary-400" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-neutral-400">Active Trades</p>
              <p className="text-2xl font-bold text-neutral-50">12</p>
              <p className="text-sm text-neutral-400">3 pending</p>
            </div>
            <div className="p-3 bg-success-500/10 rounded-lg">
              <TrendingUp className="h-6 w-6 text-success-400" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-neutral-400">Signals Today</p>
              <p className="text-2xl font-bold text-neutral-50">47</p>
              <p className="text-sm text-neutral-400">85% accuracy</p>
            </div>
            <div className="p-3 bg-warning-500/10 rounded-lg">
              <Activity className="h-6 w-6 text-warning-400" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-neutral-400">Risk Level</p>
              <p className="text-2xl font-bold text-neutral-50">Low</p>
              <p className="text-sm text-success-400">Safe</p>
            </div>
            <div className="p-3 bg-danger-500/10 rounded-lg">
              <AlertTriangle className="h-6 w-6 text-danger-400" />
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-neutral-50 mb-4">Recent Activity</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-neutral-700/50 rounded-lg">
              <div>
                <p className="text-sm font-medium text-neutral-50">BTC/USDT Trade</p>
                <p className="text-xs text-neutral-400">2 minutes ago</p>
              </div>
              <span className="badge badge-success">Executed</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-neutral-700/50 rounded-lg">
              <div>
                <p className="text-sm font-medium text-neutral-50">Signal Generated</p>
                <p className="text-xs text-neutral-400">5 minutes ago</p>
              </div>
              <span className="badge badge-warning">High Confidence</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-neutral-700/50 rounded-lg">
              <div>
                <p className="text-sm font-medium text-neutral-50">Position Closed</p>
                <p className="text-xs text-neutral-400">10 minutes ago</p>
              </div>
              <span className="badge badge-success">+$1,250</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-neutral-50 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <button className="w-full btn btn-primary">
              Start New Trade
            </button>
            <button className="w-full btn btn-secondary">
              View Signals
            </button>
            <button className="w-full btn btn-secondary">
              Check Analytics
            </button>
            <button className="w-full btn btn-secondary">
              Manage Positions
            </button>
          </div>
        </div>
      </div>

      {/* Placeholder for charts */}
      <div className="card">
        <h3 className="text-lg font-semibold text-neutral-50 mb-4">Performance Chart</h3>
        <div className="h-64 bg-neutral-700/50 rounded-lg flex items-center justify-center">
          <p className="text-neutral-400">Chart component will be implemented here</p>
        </div>
      </div>
    </div>
  )
} 