import React, { useState, useEffect } from 'react'
import { 
  Play, 
  CheckCircle, 
  AlertTriangle, 
  Clock, 
  TrendingUp,
  Calculator,
  Target,
  Zap,
  ArrowRight,
  FileText,
  Code,
  Award,
  Shield,
  BarChart3,
  Activity
} from 'lucide-react'

const DBI = () => {
  const [isGenerating, setIsGenerating] = useState(false)
  const [generationStatus, setGenerationStatus] = useState(null)
  const [activeTab, setActiveTab] = useState('methodology')
  const [workflowProgress, setWorkflowProgress] = useState(0)

  const tabs = [
    {
      id: 'methodology',
      label: 'DBI Methodology',
      icon: Calculator,
      description: 'Dynamic Bidirectional Interpolation'
    },
    {
      id: 'workflow',
      label: 'Workflow',
      icon: Activity,
      description: 'Complete daily sequence'
    },
    {
      id: 'results',
      label: 'Results',
      icon: BarChart3,
      description: 'Generated coefficients'
    }
  ]

  const handleGenerateNow = async () => {
    setIsGenerating(true)
    setGenerationStatus('starting')
    setWorkflowProgress(0)

    try {
      // Simulate the complete workflow
      const steps = [
        { name: 'Life Age Update', progress: 20 },
        { name: 'Risk Band Update', progress: 40 },
        { name: 'Percentage Recalculation', progress: 60 },
        { name: 'Coefficient Update (DBI)', progress: 80 },
        { name: 'Final Score Calculation', progress: 100 }
      ]

      for (let i = 0; i < steps.length; i++) {
        const step = steps[i]
        setGenerationStatus(`Running: ${step.name}`)
        setWorkflowProgress(step.progress)
        
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1000))
      }

      setGenerationStatus('completed')
      
      // Show success message
      setTimeout(() => {
        setGenerationStatus(null)
        setIsGenerating(false)
        setWorkflowProgress(0)
      }, 3000)

    } catch (error) {
      console.error('Error running DBI workflow:', error)
      setGenerationStatus('error')
      setIsGenerating(false)
    }
  }

  const getStatusIcon = () => {
    switch (generationStatus) {
      case 'starting':
        return <Clock className="w-5 h-5 text-blue-500 animate-spin" />
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'error':
        return <AlertTriangle className="w-5 h-5 text-red-500" />
      default:
        return <Play className="w-5 h-5 text-blue-500" />
    }
  }

  const getStatusText = () => {
    switch (generationStatus) {
      case 'starting':
        return 'Starting DBI workflow...'
      case 'completed':
        return 'DBI workflow completed successfully!'
      case 'error':
        return 'Error running DBI workflow'
      default:
        return 'Ready to generate'
    }
  }

  return (
    <div className="dbi-container">
      {/* Header */}
      <div className="dbi-header">
        <div className="header-content">
          <div className="header-icon">
            <Calculator className="w-8 h-8 text-blue-600" />
          </div>
          <div className="header-text">
            <h1 className="header-title">Dynamic Bidirectional Interpolation (DBI)</h1>
            <p className="header-subtitle">Perfected coefficient calculation methodology</p>
          </div>
        </div>
        
        {/* Generate Now Button */}
        <div className="generate-section">
          <button
            onClick={handleGenerateNow}
            disabled={isGenerating}
            className={`generate-button ${isGenerating ? 'generating' : ''}`}
          >
            {getStatusIcon()}
            <span>{isGenerating ? 'Generating...' : 'Generate Now'}</span>
          </button>
          
          {generationStatus && (
            <div className={`status-message ${generationStatus}`}>
              <span>{getStatusText()}</span>
              {workflowProgress > 0 && (
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${workflowProgress}%` }}
                  ></div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Horizontal Tabs */}
      <div className="dbi-tabs">
        {tabs.map((tab, index) => (
          <button
            key={tab.id}
            className={`dbi-tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <tab.icon className="tab-icon" />
            <div className="tab-content">
              <span className="tab-label">{tab.label}</span>
              <span className="tab-description">{tab.description}</span>
            </div>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="dbi-content">
        {activeTab === 'methodology' && (
          <div className="methodology-content">
            <div className="methodology-grid">
              {/* Overview Card */}
              <div className="methodology-card overview">
                <div className="card-header">
                  <Award className="w-6 h-6 text-yellow-500" />
                  <h3>Methodology Overview</h3>
                </div>
                <div className="card-content">
                  <p className="methodology-description">
                    <strong>Dynamic Bidirectional Interpolation (DBI)</strong> is our perfected coefficient calculation method 
                    that dynamically chooses the correct neighboring band based on the direction from the current band's midpoint, 
                    ensuring perfect linear interpolation in both directions.
                  </p>
                  <div className="methodology-stats">
                    <div className="stat">
                      <span className="stat-value">1.000-1.600</span>
                      <span className="stat-label">Coefficient Range</span>
                    </div>
                    <div className="stat">
                      <span className="stat-value">0.0085</span>
                      <span className="stat-label">Previous Band Increment</span>
                    </div>
                    <div className="stat">
                      <span className="stat-value">0.031</span>
                      <span className="stat-label">Next Band Increment</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Calculation Steps */}
              <div className="methodology-card steps">
                <div className="card-header">
                  <Calculator className="w-6 h-6 text-blue-500" />
                  <h3>Calculation Steps</h3>
                </div>
                <div className="card-content">
                  <div className="steps-list">
                    <div className="step">
                      <div className="step-number">1</div>
                      <div className="step-content">
                        <h4>Band Assignment</h4>
                        <p>Determine current risk band based on risk value</p>
                      </div>
                    </div>
                    <div className="step">
                      <div className="step-number">2</div>
                      <div className="step-content">
                        <h4>Direction Detection</h4>
                        <p>Check if moving towards previous or next band</p>
                      </div>
                    </div>
                    <div className="step">
                      <div className="step-number">3</div>
                      <div className="step-content">
                        <h4>Dynamic Increment</h4>
                        <p>Use band-specific increments (0.0085 vs 0.031)</p>
                      </div>
                    </div>
                    <div className="step">
                      <div className="step-number">4</div>
                      <div className="step-content">
                        <h4>Final Calculation</h4>
                        <p>Apply linear interpolation for precise coefficient</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Example Calculation */}
              <div className="methodology-card example">
                <div className="card-header">
                  <Target className="w-6 h-6 text-green-500" />
                  <h3>BTC Example</h3>
                </div>
                <div className="card-content">
                  <div className="example-calculation">
                    <div className="calculation-row">
                      <span className="label">Risk Value:</span>
                      <span className="value">0.544</span>
                    </div>
                    <div className="calculation-row">
                      <span className="label">Current Band:</span>
                      <span className="value">0.5-0.6</span>
                    </div>
                    <div className="calculation-row">
                      <span className="label">Direction:</span>
                      <span className="value">Towards Previous (0.4-0.5)</span>
                    </div>
                    <div className="calculation-row">
                      <span className="label">Increment:</span>
                      <span className="value">0.0085</span>
                    </div>
                    <div className="calculation-row result">
                      <span className="label">DBI Coefficient:</span>
                      <span className="value">1.096</span>
                    </div>
                    <div className="calculation-row result">
                      <span className="label">Final Score:</span>
                      <span className="value">49.97</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Band Coefficients */}
              <div className="methodology-card coefficients">
                <div className="card-header">
                  <BarChart3 className="w-6 h-6 text-purple-500" />
                  <h3>Band Midpoint Coefficients</h3>
                </div>
                <div className="card-content">
                  <div className="coefficients-grid">
                    <div className="coefficient-item">
                      <span className="band">0.0-0.1</span>
                      <span className="coef">1.538</span>
                    </div>
                    <div className="coefficient-item">
                      <span className="band">0.1-0.2</span>
                      <span className="coef">1.221</span>
                    </div>
                    <div className="coefficient-item">
                      <span className="band">0.2-0.3</span>
                      <span className="coef">1.157</span>
                    </div>
                    <div className="coefficient-item">
                      <span className="band">0.3-0.4</span>
                      <span className="coef">1.000</span>
                    </div>
                    <div className="coefficient-item">
                      <span className="band">0.4-0.5</span>
                      <span className="coef">1.016</span>
                    </div>
                    <div className="coefficient-item">
                      <span className="band">0.5-0.6</span>
                      <span className="coef">1.101</span>
                    </div>
                    <div className="coefficient-item">
                      <span className="band">0.6-0.7</span>
                      <span className="coef">1.411</span>
                    </div>
                    <div className="coefficient-item">
                      <span className="band">0.7-0.8</span>
                      <span className="coef">1.537</span>
                    </div>
                    <div className="coefficient-item">
                      <span className="band">0.8-0.9</span>
                      <span className="coef">1.568</span>
                    </div>
                    <div className="coefficient-item">
                      <span className="band">0.9-1.0</span>
                      <span className="coef">1.600</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'workflow' && (
          <div className="workflow-content">
            <div className="workflow-card">
              <div className="card-header">
                <Activity className="w-6 h-6 text-blue-500" />
                <h3>Complete Daily Workflow</h3>
              </div>
              <div className="card-content">
                <div className="workflow-steps">
                  <div className="workflow-step">
                    <div className="step-icon">
                      <TrendingUp className="w-5 h-5" />
                    </div>
                    <div className="step-content">
                      <h4>Step 1: Life Age Update</h4>
                      <p>Increment life age by +1 day for all symbols</p>
                      <div className="step-details">
                        <span className="detail">Trigger: Daily at 1:00 AM</span>
                        <span className="detail">Status: Automated</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="workflow-step">
                    <div className="step-icon">
                      <Target className="w-5 h-5" />
                    </div>
                    <div className="step-content">
                      <h4>Step 2: Risk Band Update</h4>
                      <p>Add +1 day to current risk band for each symbol</p>
                      <div className="step-details">
                        <span className="detail">Trigger: After Life Age Update</span>
                        <span className="detail">Status: Automated</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="workflow-step">
                    <div className="step-icon">
                      <BarChart3 className="w-5 h-5" />
                    </div>
                    <div className="step-content">
                      <h4>Step 3: Percentage Recalculation</h4>
                      <p>Recalculate all band percentages based on new total</p>
                      <div className="step-details">
                        <span className="detail">Trigger: After Risk Band Update</span>
                        <span className="detail">Status: Automated</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="workflow-step">
                    <div className="step-icon">
                      <Calculator className="w-5 h-5" />
                    </div>
                    <div className="step-content">
                      <h4>Step 4: Coefficient Update (DBI)</h4>
                      <p>Calculate coefficients using Dynamic Bidirectional Interpolation</p>
                      <div className="step-details">
                        <span className="detail">Trigger: After Percentage Update</span>
                        <span className="detail">Status: Automated</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="workflow-step">
                    <div className="step-icon">
                      <Zap className="w-5 h-5" />
                    </div>
                    <div className="step-content">
                      <h4>Step 5: Final Score Calculation</h4>
                      <p>Calculate final score: Base Score × Coefficient</p>
                      <div className="step-details">
                        <span className="detail">Trigger: After Coefficient Update</span>
                        <span className="detail">Status: Automated</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'results' && (
          <div className="results-content">
            <div className="results-card">
              <div className="card-header">
                <BarChart3 className="w-6 h-6 text-green-500" />
                <h3>Generated Results</h3>
              </div>
              <div className="card-content">
                <div className="results-grid">
                  <div className="result-item">
                    <div className="result-header">
                      <span className="symbol">BTC</span>
                      <span className="status success">Completed</span>
                    </div>
                    <div className="result-details">
                      <div className="detail-row">
                        <span>Risk Value:</span>
                        <span>0.544</span>
                      </div>
                      <div className="detail-row">
                        <span>DBI Coefficient:</span>
                        <span>1.096</span>
                      </div>
                      <div className="detail-row">
                        <span>Base Score:</span>
                        <span>45.60</span>
                      </div>
                      <div className="detail-row">
                        <span>Final Score:</span>
                        <span>49.97</span>
                      </div>
                      <div className="detail-row">
                        <span>Signal:</span>
                        <span>NEUTRAL</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="result-item">
                    <div className="result-header">
                      <span className="symbol">ETH</span>
                      <span className="status success">Completed</span>
                    </div>
                    <div className="result-details">
                      <div className="detail-row">
                        <span>Risk Value:</span>
                        <span>0.647</span>
                      </div>
                      <div className="detail-row">
                        <span>DBI Coefficient:</span>
                        <span>1.402</span>
                      </div>
                      <div className="detail-row">
                        <span>Base Score:</span>
                        <span>35.30</span>
                      </div>
                      <div className="detail-row">
                        <span>Final Score:</span>
                        <span>49.48</span>
                      </div>
                      <div className="detail-row">
                        <span>Signal:</span>
                        <span>NEUTRAL</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default DBI
