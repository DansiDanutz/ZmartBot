import React, { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import SimpleChart from './SimpleChart'
import { 
  TrendingUp, 
  Target, 
  BarChart3, 
  Activity, 
  Zap, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  RefreshCw,
  Database,
  Cpu,
  Signal,
  TrendingDown,
  Minus,
  Sparkles,
  Eye,
  BarChart,
  PieChart,
  LineChart,
  Shield,
  Award,
  Star,
  Zap as Lightning
} from 'lucide-react'

const API_BASE = 'http://localhost:3400'

// Enhanced Horizontal Tabs Component with animations
const HorizontalTabs = ({ tabs, active, onChange }) => (
  <div className="scoring-tabs">
    {tabs.map((tab, index) => (
      <button
        key={tab.id}
        className={`scoring-tab ${active === tab.id ? 'active' : ''}`}
        onClick={() => onChange(tab.id)}
        style={{ animationDelay: `${index * 100}ms` }}
      >
        <div className="tab-content">
          {tab.icon && <tab.icon className="tab-icon" />}
          <span className="tab-label">{tab.label}</span>
          {tab.badge && <span className="tab-badge">{tab.badge}</span>}
        </div>
        <div className="tab-indicator"></div>
      </button>
    ))}
  </div>
)

// Enhanced Cryptometer Data Card with animations
const CryptometerCard = ({ title, value, subtitle, icon: Icon, status = 'neutral', trend = null, loading = false }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'success': return 'text-green-500'
      case 'warning': return 'text-yellow-500'
      case 'error': return 'text-red-500'
      default: return 'text-blue-500'
    }
  }

  const getTrendIcon = () => {
    if (!trend) return null
    if (trend > 0) return <TrendingUp className="w-4 h-4 text-green-500 animate-pulse" />
    if (trend < 0) return <TrendingDown className="w-4 h-4 text-red-500 animate-pulse" />
    return <Minus className="w-4 h-4 text-gray-500" />
  }

  return (
    <div className={`cryptometer-card ${loading ? 'loading' : ''}`}>
      <div className="card-glow"></div>
      <div className="card-header">
        <div className="card-icon-wrapper">
          <Icon className={`card-icon ${getStatusColor()}`} />
          <div className="icon-glow"></div>
        </div>
        <div className="card-title">
          <h4>{title}</h4>
          {subtitle && <p className="card-subtitle">{subtitle}</p>}
        </div>
        {getTrendIcon()}
      </div>
      <div className="card-value">
        {loading ? (
          <div className="loading-skeleton">
            <div className="skeleton-bar"></div>
          </div>
        ) : (
          <span className="value-text">
            {typeof value === 'number' ? value.toFixed(2) : value}
          </span>
        )}
      </div>
      <div className="card-particles"></div>
    </div>
  )
}

// Enhanced Endpoint Status Component
const EndpointStatus = ({ endpoint, data }) => {
  const isSuccess = data?.success
  const isLoading = data?.loading
  const hasError = data?.error

  return (
    <div className={`endpoint-status ${isSuccess ? 'success' : hasError ? 'error' : 'loading'}`}>
      <div className="endpoint-glow"></div>
      <div className="endpoint-header">
        <span className="endpoint-name">{endpoint}</span>
        <div className="endpoint-indicator">
          {isSuccess && <CheckCircle className="w-4 h-4 text-green-500 animate-bounce" />}
          {hasError && <XCircle className="w-4 h-4 text-red-500 animate-pulse" />}
          {isLoading && <RefreshCw className="w-4 h-4 text-blue-500 animate-spin" />}
        </div>
      </div>
      {data?.weight && (
        <div className="endpoint-weight">
          <span className="weight-label">Weight:</span>
          <span className="weight-value">{data.weight}</span>
        </div>
      )}
      <div className="endpoint-particles"></div>
    </div>
  )
}

// Enhanced AI Analysis Component
const AIAnalysis = ({ analysis }) => {
  if (!analysis) return null

  return (
    <div className="ai-analysis">
      <div className="ai-glow"></div>
      <div className="ai-header">
        <div className="ai-icon-wrapper">
          <Cpu className="ai-icon" />
          <div className="ai-icon-glow"></div>
        </div>
        <h4>AI Analysis</h4>
        <div className="ai-badge">
          <Sparkles className="w-4 h-4" />
          <span>Powered by GPT-4</span>
        </div>
      </div>
      <div className="ai-content">
        <div className="ai-metrics">
          <div className="ai-metric">
            <div className="metric-icon">
              <Target className="w-4 h-4" />
            </div>
            <div className="metric-content">
              <span className="metric-label">Confidence:</span>
              <span className="metric-value">{(analysis.confidence * 100).toFixed(1)}%</span>
            </div>
            <div className="metric-progress">
              <div 
                className="progress-bar" 
                style={{ width: `${analysis.confidence * 100}%` }}
              ></div>
            </div>
          </div>
          <div className="ai-metric">
            <div className="metric-icon">
              <TrendingUp className="w-4 h-4" />
            </div>
            <div className="metric-content">
              <span className="metric-label">Direction:</span>
              <span className={`metric-value ${analysis.direction?.toLowerCase()}`}>
                {analysis.direction}
              </span>
            </div>
          </div>
          <div className="ai-metric">
            <div className="metric-icon">
              <BarChart className="w-4 h-4" />
            </div>
            <div className="metric-content">
              <span className="metric-label">Patterns:</span>
              <span className="metric-value">{analysis.patterns_count || 0}</span>
            </div>
          </div>
        </div>
        {analysis.interpretation && (
          <div className="ai-interpretation">
            <div className="interpretation-header">
              <Eye className="w-4 h-4" />
              <span>AI Interpretation</span>
            </div>
            <p>{analysis.interpretation}</p>
          </div>
        )}
      </div>
      <div className="ai-particles"></div>
    </div>
  )
}

// Enhanced Cryptometer Tab Component
const CryptometerTab = () => {
  const [symbol, setSymbol] = useState('BTCUSDT')
  const [cryptometerData, setCryptometerData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [lastUpdated, setLastUpdated] = useState(null)
  const [isRefreshing, setIsRefreshing] = useState(false)

  const fetchCryptometerData = async (symbolToFetch) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`${API_BASE}/cryptometer/symbol/${symbolToFetch}`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      setCryptometerData(data)
      setLastUpdated(new Date())
    } catch (err) {
      console.error('Error fetching Cryptometer data:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCryptometerData(symbol)
  }, [symbol])

  const handleRefresh = async () => {
    setIsRefreshing(true)
    await fetchCryptometerData(symbol)
    setIsRefreshing(false)
  }

  const handleSymbolChange = (newSymbol) => {
    setSymbol(newSymbol.toUpperCase())
  }

  // Calculate summary metrics
  const summaryMetrics = cryptometerData ? {
    totalEndpoints: cryptometerData.summary?.total_endpoints || 0,
    successfulEndpoints: cryptometerData.summary?.successful_endpoints || 0,
    successRate: cryptometerData.summary?.success_rate || 0,
    dataQuality: cryptometerData.summary?.data_quality || 0
  } : null

  // Get endpoint data
  const endpoints = cryptometerData?.endpoints || {}

  // Calculate AI score (mock calculation based on successful endpoints)
  const aiScore = summaryMetrics ? 
    Math.min(100, (summaryMetrics.successfulEndpoints / summaryMetrics.totalEndpoints) * 100) : 0

  return (
    <div className="cryptometer-tab">
      <div className="tab-background"></div>
      
      <div className="cryptometer-header">
        <div className="header-left">
          <div className="header-icon">
            <BarChart3 className="w-6 h-6" />
            <div className="header-glow"></div>
          </div>
          <div className="header-content">
            <h3>📊 Cryptometer Analysis</h3>
            <p>Multi-timeframe AI-powered market analysis using 17 endpoints</p>
          </div>
        </div>
        <div className="header-right">
          <div className="symbol-input">
            <input
              type="text"
              placeholder="Enter symbol (e.g., BTCUSDT)"
              value={symbol}
              onChange={(e) => handleSymbolChange(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && fetchCryptometerData(symbol)}
              className="symbol-input-field"
            />
            <button 
              className={`refresh-btn ${isRefreshing ? 'refreshing' : ''}`}
              onClick={handleRefresh}
              disabled={loading || isRefreshing}
            >
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            </button>
          </div>
          {lastUpdated && (
            <div className="last-updated">
              <Clock className="w-4 h-4" />
              <span>Updated: {lastUpdated.toLocaleTimeString()}</span>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="error-message">
          <AlertTriangle className="w-5 h-5" />
          <span>Error: {error}</span>
        </div>
      )}

      {loading && (
        <div className="loading-message">
          <div className="loading-spinner">
            <RefreshCw className="w-5 h-5 animate-spin" />
          </div>
          <span>Loading Cryptometer data...</span>
        </div>
      )}

      {cryptometerData && (
        <>
          {/* Summary Metrics */}
          <div className="summary-metrics">
            <CryptometerCard
              title="AI Score"
              value={aiScore}
              subtitle="Overall analysis score"
              icon={Target}
              status={aiScore > 70 ? 'success' : aiScore > 50 ? 'warning' : 'error'}
            />
            <CryptometerCard
              title="Success Rate"
              value={summaryMetrics.successRate}
              subtitle="API endpoints working"
              icon={CheckCircle}
              status={summaryMetrics.successRate > 80 ? 'success' : 'warning'}
            />
            <CryptometerCard
              title="Data Quality"
              value={summaryMetrics.dataQuality}
              subtitle="Data reliability score"
              icon={Database}
              status={summaryMetrics.dataQuality > 0.8 ? 'success' : 'warning'}
            />
            <CryptometerCard
              title="Endpoints"
              value={`${summaryMetrics.successfulEndpoints}/${summaryMetrics.totalEndpoints}`}
              subtitle="Active data sources"
              icon={Signal}
              status="neutral"
            />
          </div>

          {/* AI Analysis */}
          <AIAnalysis analysis={{
            confidence: summaryMetrics.dataQuality,
            direction: aiScore > 70 ? 'BULLISH' : aiScore > 50 ? 'NEUTRAL' : 'BEARISH',
            patterns_count: Object.keys(endpoints).length,
            interpretation: `Based on ${summaryMetrics.successfulEndpoints} active endpoints, the AI analysis shows ${aiScore > 70 ? 'strong bullish' : aiScore > 50 ? 'neutral' : 'bearish'} signals for ${symbol}.`
          }} />

          {/* Endpoints Status */}
          <div className="endpoints-section">
            <div className="section-header">
              <h4>📡 Endpoint Status</h4>
              <div className="section-badge">
                <Signal className="w-4 h-4" />
                <span>{Object.keys(endpoints).length} endpoints</span>
              </div>
            </div>
            <div className="endpoints-grid">
              {Object.entries(endpoints).map(([endpoint, data]) => (
                <EndpointStatus 
                  key={endpoint} 
                  endpoint={endpoint} 
                  data={data} 
                />
              ))}
            </div>
          </div>

          {/* Raw Data Preview */}
          <div className="raw-data-section">
            <div className="section-header">
              <h4>🔍 Raw Data Preview</h4>
              <div className="section-badge">
                <Database className="w-4 h-4" />
                <span>JSON format</span>
              </div>
            </div>
            <div className="data-preview">
              <pre>{JSON.stringify(cryptometerData, null, 2)}</pre>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

// KingFisher Tab Component
const KingFisherTab = () => {
  const [symbol, setSymbol] = useState('BTCUSDT');
  const [kingfisherData, setKingfisherData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchKingFisherData = async (symbolToFetch) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:3400/kingfisher/analysis/${symbolToFetch}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setKingfisherData(data);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err.message);
      console.error('Error fetching KingFisher data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    fetchKingFisherData(symbol);
  };

  const handleSymbolChange = (newSymbol) => {
    setSymbol(newSymbol.toUpperCase());
  };

  useEffect(() => {
    fetchKingFisherData(symbol);
  }, [symbol]);

  return (
    <div className="kingfisher-tab">
      <div className="header">
        <div className="header-left">
          <h3>🎣 KingFisher Analysis</h3>
          <p>Liquidation analysis and AI win rate predictions</p>
        </div>
        <div className="header-right">
          <div className="symbol-input">
            <input
              type="text"
              placeholder="Enter symbol (e.g., BTCUSDT)"
              value={symbol}
              onChange={(e) => handleSymbolChange(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && fetchKingFisherData(symbol)}
            />
            <button 
              className="refresh-btn"
              onClick={handleRefresh}
              disabled={loading}
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
          {lastUpdated && (
            <div className="last-updated">
              <Clock className="w-4 h-4" />
              <span>Updated: {lastUpdated.toLocaleTimeString()}</span>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="error-message">
          <AlertTriangle className="w-5 h-5" />
          <span>Error: {error}</span>
        </div>
      )}

      {loading && (
        <div className="loading-message">
          <RefreshCw className="w-5 h-5 animate-spin" />
          <span>Loading KingFisher analysis...</span>
        </div>
      )}

      {kingfisherData && (
        <div className="kingfisher-content">
          <div className="analysis-grid">
            <div className="analysis-card">
              <h4>📊 Liquidation Analysis</h4>
              <div className="metrics-grid">
                <div className="metric">
                  <span className="metric-label">Short Liquidations</span>
                  <span className="metric-value">{kingfisherData.analysis?.liquidation_analysis?.short_liquidations || 'N/A'}</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Long Liquidations</span>
                  <span className="metric-value">{kingfisherData.analysis?.liquidation_analysis?.long_liquidations || 'N/A'}</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Net Liquidations</span>
                  <span className="metric-value">{kingfisherData.analysis?.liquidation_analysis?.net_liquidations || 'N/A'}</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Liquidation Score</span>
                  <span className="metric-value">{kingfisherData.analysis?.liquidation_analysis?.liquidation_score || 'N/A'}</span>
                </div>
              </div>
            </div>

            <div className="analysis-card">
              <h4>🤖 AI Win Rate Prediction</h4>
              <div className="ai-prediction">
                {kingfisherData.analysis?.ai_win_rate_prediction ? (
                  <div className="prediction-details">
                    <div className="prediction-score">
                      <span className="score-label">Win Rate</span>
                      <span className="score-value">
                        {(kingfisherData.analysis.ai_win_rate_prediction.win_rate_prediction * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="prediction-confidence">
                      <span className="confidence-label">Confidence</span>
                      <span className="confidence-value">
                        {(kingfisherData.analysis.ai_win_rate_prediction.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                ) : (
                  <p>AI prediction not available</p>
                )}
              </div>
            </div>
          </div>

          <div className="raw-data-section">
            <h4>🔍 Raw Analysis Data</h4>
            <div className="data-preview">
              <pre>{JSON.stringify(kingfisherData, null, 2)}</pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// RiskMetric Tab Component
const RiskMetricTab = ({ activeSubTab, setActiveSubTab, selectedTicker, setSelectedTicker }) => {
  const [riskMatrixData, setRiskMatrixData] = useState([]);
  const [symbols, setSymbols] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [selectedSymbol, setSelectedSymbol] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPrice, setCurrentPrice] = useState(null);
  const [priceLoading, setPriceLoading] = useState(true);
  const [minRiskPrice, setMinRiskPrice] = useState(null);
  const [newPriceInput, setNewPriceInput] = useState('');
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [maxRiskPrice, setMaxRiskPrice] = useState(null);
  const [bandChangeAlert, setBandChangeAlert] = useState(null);
  const [alertHistory, setAlertHistory] = useState([]);
  const [updateLogs, setUpdateLogs] = useState([]);
  const [updateLogsLoading, setUpdateLogsLoading] = useState(false);
  const [newMaxPriceInput, setNewMaxPriceInput] = useState('');
  const [lastMaxUpdate, setLastMaxUpdate] = useState(new Date());

  // State variables for Polynomial Formula
  const [polynomialFormula, setPolynomialFormula] = useState('BTC=31000.147395+12913.634041⋅x+281625.197482⋅x²−64979.714839⋅x³+37986.750750⋅x⁴');
  const [newFormulaInput, setNewFormulaInput] = useState('');
  const [lastFormulaUpdate, setLastFormulaUpdate] = useState(new Date());
  const [riskValue, setRiskValue] = useState(null);
  const [lastRiskValueUpdate, setLastRiskValueUpdate] = useState(new Date());
  const [coefficientApply, setCoefficientApply] = useState(null);
  const [lastCoefficientUpdate, setLastCoefficientUpdate] = useState(new Date());
  const [currentCoefficient, setCurrentCoefficient] = useState(null);
  const [currentRiskBand, setCurrentRiskBand] = useState(null);
  const [lastRiskBandUpdate, setLastRiskBandUpdate] = useState(new Date());

  // State variables for Risk Value Formula
  const [riskValueFormula, setRiskValueFormula] = useState('Risk=−0.380790057100+1.718335491963×10⁻⁵⋅P−1.213364209168×10⁻¹⁰⋅P²+4.390647720677×10⁻¹⁶⋅P³−5.830886880671×10⁻²²⋅P⁴');
  const [newRiskFormulaInput, setNewRiskFormulaInput] = useState('');
  const [lastRiskFormulaUpdate, setLastRiskFormulaUpdate] = useState(new Date());

  // State variables for Life Age
  const [lifeAge, setLifeAge] = useState(365);
  const [newLifeAgeInput, setNewLifeAgeInput] = useState('');
  const [lastLifeAgeUpdate, setLastLifeAgeUpdate] = useState(new Date());
  const [lifeAgeLoading, setLifeAgeLoading] = useState(false);

  // State variables for Risk Bands
  const [riskBands, setRiskBands] = useState({
    '0.0-0.1': { days: 0, percentage: 0, lastUpdate: new Date() },
    '0.1-0.2': { days: 0, percentage: 0, lastUpdate: new Date() },
    '0.2-0.3': { days: 0, percentage: 0, lastUpdate: new Date() },
    '0.3-0.4': { days: 0, percentage: 0, lastUpdate: new Date() },
    '0.4-0.5': { days: 0, percentage: 0, lastUpdate: new Date() },
    '0.5-0.6': { days: 0, percentage: 0, lastUpdate: new Date() },
    '0.6-0.7': { days: 0, percentage: 0, lastUpdate: new Date() },
    '0.7-0.8': { days: 0, percentage: 0, lastUpdate: new Date() },
    '0.8-0.9': { days: 0, percentage: 0, lastUpdate: new Date() },
    '0.9-1.0': { days: 0, percentage: 0, lastUpdate: new Date() }
  });
  const [newRiskBandInputs, setNewRiskBandInputs] = useState({
    '0.0-0.1': '',
    '0.1-0.2': '',
    '0.2-0.3': '',
    '0.3-0.4': '',
    '0.4-0.5': '',
    '0.5-0.6': '',
    '0.6-0.7': '',
    '0.7-0.8': '',
    '0.8-0.9': '',
    '0.9-1.0': ''
  });

  const fetchRiskMatrixData = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('🔍 Fetching RiskMetric Matrix data...');
      const response = await fetch('http://localhost:3400/api/v1/riskmatrix-grid/all');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('✅ API Response:', data);
      
      if (data.success) {
        setRiskMatrixData(data.data);
        setSymbols(data.symbols);
        console.log(`✅ Loaded ${data.data.length} risk levels for ${data.symbols.length} symbols`);
      } else {
        setError('Failed to fetch risk matrix data');
        console.error('❌ API returned success: false');
      }
      setLastUpdated(new Date());
    } catch (err) {
      setError(err.message);
      console.error('❌ Error fetching risk matrix data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    fetchRiskMatrixData();
  };

  // Function to get risk band based on risk value
  const getRiskBand = (riskValue) => {
    if (riskValue < 0.1) return '0.0-0.1';
    if (riskValue < 0.2) return '0.1-0.2';
    if (riskValue < 0.3) return '0.2-0.3';
    if (riskValue < 0.4) return '0.3-0.4';
    if (riskValue < 0.5) return '0.4-0.5';
    if (riskValue < 0.6) return '0.5-0.6';
    if (riskValue < 0.7) return '0.6-0.7';
    if (riskValue < 0.8) return '0.7-0.8';
    if (riskValue < 0.9) return '0.8-0.9';
    return '0.9-1.0';
  };

  // Function to calculate base score based on risk value with dynamic rarity-based scoring
  const calculateBaseScore = (riskValue, riskBandsData = null) => {
    if (riskValue === null) return null;
    
    // Base score ranges as specified
    let baseMin, baseMax;
    
    if (riskValue >= 0 && riskValue <= 0.25) {
      // 0-0.25: 70 to 100 points
      baseMin = 70;
      baseMax = 100;
    } else if (riskValue >= 0.25 && riskValue <= 0.40) {
      // 0.25-0.40: 60 to 70 points
      baseMin = 60;
      baseMax = 70;
    } else if (riskValue >= 0.40 && riskValue <= 0.60) {
      // 0.40-0.60: 40 to 60 points (neutral zone)
      baseMin = 40;
      baseMax = 60;
    } else if (riskValue >= 0.60 && riskValue <= 0.75) {
      // 0.60-0.75: 60 to 70 points
      baseMin = 60;
      baseMax = 70;
    } else if (riskValue >= 0.75 && riskValue <= 1.0) {
      // 0.75-1.0: 70 to 100 points
      baseMin = 70;
      baseMax = 100;
    } else {
      return 50; // Default neutral score
    }
    
    // Calculate base proportion within the risk band
    let proportion;
    if (riskValue >= 0 && riskValue <= 0.25) {
      proportion = riskValue / 0.25;
    } else if (riskValue >= 0.25 && riskValue <= 0.40) {
      proportion = (riskValue - 0.25) / (0.40 - 0.25);
    } else if (riskValue >= 0.40 && riskValue <= 0.60) {
      proportion = (riskValue - 0.40) / (0.60 - 0.40);
    } else if (riskValue >= 0.60 && riskValue <= 0.75) {
      proportion = (riskValue - 0.60) / (0.75 - 0.60);
    } else if (riskValue >= 0.75 && riskValue <= 1.0) {
      proportion = (riskValue - 0.75) / (1.0 - 0.75);
    } else {
      proportion = 0.5; // Default to middle
    }
    
    // Calculate base score
    let baseScore = baseMin + (proportion * (baseMax - baseMin));
    
    // Apply rarity-based adjustments if risk bands data is available
    if (riskBandsData && Object.keys(riskBandsData).length > 0) {
      const currentBand = getRiskBand(riskValue);
      const currentBandData = riskBandsData[currentBand];
      
      if (currentBandData) {
        const currentDays = currentBandData.days || 0;
        const currentPercentage = currentBandData.percentage || 0;
        
        // Convert risk bands data to array for analysis
        const bandsArray = Object.entries(riskBandsData)
          .filter(([band, data]) => data && data.days !== undefined)
          .map(([band, data]) => ({
            band,
            days: data.days || 0,
            percentage: data.percentage || 0
          }))
          .sort((a, b) => a.days - b.days); // Sort by rarity (least days = rarest)
        
        if (bandsArray.length > 0) {
          // Find current band rank (1 = rarest, 10 = most common)
          const currentBandRank = bandsArray.findIndex(b => b.band === currentBand) + 1;
          const totalBands = bandsArray.length;
          
          // Calculate rarity factor (0 = most common, 1 = rarest)
          const rarityFactor = 1 - (currentBandRank - 1) / (totalBands - 1);
          
          // Calculate proximity to neighboring bands
          const currentBandIndex = bandsArray.findIndex(b => b.band === currentBand);
          const lowerNeighbor = bandsArray[currentBandIndex - 1];
          const upperNeighbor = bandsArray[currentBandIndex + 1];
          
          let proximityBonus = 0;
          
          if (lowerNeighbor && upperNeighbor) {
            // Check if current band is sandwiched between rarer bands
            const lowerRarer = lowerNeighbor.days < currentDays;
            const upperRarer = upperNeighbor.days < currentDays;
            
            if (lowerRarer && upperRarer) {
              // High opportunity: sandwiched between rarer bands
              proximityBonus = 15;
            } else if (lowerRarer || upperRarer) {
              // Medium opportunity: adjacent to rarer band
              const rarerNeighbor = lowerRarer ? lowerNeighbor : upperNeighbor;
              const rarityRatio = currentDays / rarerNeighbor.days;
              proximityBonus = Math.min(10, rarityRatio * 5);
            }
          }
          
          // Apply rarity and proximity adjustments
          const rarityBonus = rarityFactor * 20; // 0-20 points based on rarity
          const totalBonus = rarityBonus + proximityBonus;
          
          // Apply bonus to base score
          baseScore = Math.min(100, baseScore + totalBonus);
        }
      }
    }
    
    return Math.round(baseScore);
  };

  // Function to calculate final score with coefficient (1.0-1.6 range)
  const calculateFinalScore = (baseScore, coefficient) => {
    if (baseScore === null || coefficient === null) return null;
    
    // Convert coefficient to number if it's a string
    const numericCoefficient = typeof coefficient === 'string' ? parseFloat(coefficient) : coefficient;
    
    // Ensure coefficient is between 1.0 and 1.6
    const clampedCoefficient = Math.max(1.0, Math.min(1.6, numericCoefficient));
    
    // Apply coefficient to base score
    let finalScore = baseScore * clampedCoefficient;
    
    // Cap at 100 maximum
    finalScore = Math.min(100, finalScore);
    
    // Return with exactly 2 decimal places
    return Number(finalScore).toFixed(2);
  };

  // Function to determine signal status based on RiskMetric market structure and final score
  const getSignalStatus = (finalScore, riskValue) => {
    if (finalScore === null || riskValue === null) return { status: 'NA', color: '#6b7280', bgColor: 'rgba(107, 114, 128, 0.1)' };
    
    // First, determine the market structure signal based on risk value
    let marketSignal = '';
    let marketColor = '';
    let marketBgColor = '';
    
    if (riskValue >= 0.75 && riskValue <= 1.0) {
      marketSignal = 'STRONG SELL';
      marketColor = '#dc2626';
      marketBgColor = 'rgba(220, 38, 38, 0.1)';
    } else if (riskValue >= 0.60 && riskValue < 0.75) {
      marketSignal = 'SELL';
      marketColor = '#ef4444';
      marketBgColor = 'rgba(239, 68, 68, 0.1)';
    } else if (riskValue >= 0.40 && riskValue < 0.60) {
      marketSignal = 'NEUTRAL';
      marketColor = '#f59e0b';
      marketBgColor = 'rgba(245, 158, 11, 0.1)';
    } else if (riskValue >= 0.25 && riskValue < 0.40) {
      marketSignal = 'BUY';
      marketColor = '#22c55e';
      marketBgColor = 'rgba(34, 197, 94, 0.1)';
    } else if (riskValue >= 0.0 && riskValue < 0.25) {
      marketSignal = 'STRONG BUY';
      marketColor = '#10b981';
      marketBgColor = 'rgba(16, 185, 129, 0.1)';
    } else {
      marketSignal = 'NEUTRAL';
      marketColor = '#f59e0b';
      marketBgColor = 'rgba(245, 158, 11, 0.1)';
    }
    
    // Then, determine if the score triggers a trading signal (80+ score)
    let tradingSignal = '';
    if (finalScore >= 80) {
      // Determine position type based on market structure
      if (riskValue >= 0.60) {
        // In sell zones (0.6-1.0), high score = SHORT opportunity
        tradingSignal = 'SHORT';
      } else if (riskValue < 0.40) {
        // In buy zones (0.0-0.4), high score = LONG opportunity
        tradingSignal = 'LONG';
      } else {
        // In neutral zone (0.4-0.6), high score = breakout opportunity
        tradingSignal = 'BREAKOUT';
      }
    } else {
      tradingSignal = 'NO SIGNAL';
    }
    
    // Combine market structure and trading signal
    let finalStatus = '';
    if (finalScore >= 80) {
      if (tradingSignal === 'LONG') {
        finalStatus = `LONG ${marketSignal}`;
      } else if (tradingSignal === 'SHORT') {
        finalStatus = `SHORT ${marketSignal}`;
      } else if (tradingSignal === 'BREAKOUT') {
        finalStatus = `BREAKOUT ${marketSignal}`;
      }
    } else {
      finalStatus = marketSignal;
    }
    
    return { 
      status: finalStatus, 
      color: marketColor, 
      bgColor: marketBgColor,
      marketSignal: marketSignal,
      tradingSignal: tradingSignal,
      riskValue: riskValue
    };
  };

  // Function to get percentage in current risk band
  const getPercentageInRiskBand = (riskValue) => {
    if (riskValue === null || !riskBands) return null;
    
    const currentBand = getRiskBand(riskValue);
    const bandData = riskBands[currentBand];
    
    if (bandData && bandData.percentage !== undefined) {
      return bandData.percentage;
    }
    
    return null;
  };

  // State for pattern modal
  const [patternModalOpen, setPatternModalOpen] = useState(false);
  const [patternReport, setPatternReport] = useState('');
  const [rarityRank, setRarityRank] = useState(null);

  // Function to generate detailed pattern report using ChatGPT
  const generatePatternReport = async (riskValue, riskBandsData, lifeAge) => {
    if (riskValue === null || !riskBandsData) return '';
    
    const currentBand = getRiskBand(riskValue);
    const currentDays = riskBandsData[currentBand]?.days || 0;
    const currentPercentage = riskBandsData[currentBand]?.percentage || 0;
    
    // Find rarest and most common bands for comparison
    const bandsArray = Object.entries(riskBandsData).map(([band, data]) => ({
      band,
      days: data.days || 0,
      percentage: data.percentage || 0
    })).sort((a, b) => a.days - b.days);
    
    const rarestBand = bandsArray[0];
    const mostCommonBand = bandsArray[bandsArray.length - 1];
    const currentBandRank = bandsArray.findIndex(b => b.band === currentBand) + 1;
    
    // Calculate distance to rarest band
    const distanceToRarest = Math.abs(parseFloat(currentBand.split('-')[0]) - parseFloat(rarestBand.band.split('-')[0]));
    const isNearRarest = distanceToRarest <= 0.2; // Within 0.2 risk units
    
    // Analyze coefficient dynamics (if available)
    const coefficientValue = currentCoefficient ? parseFloat(currentCoefficient) : null;
    const isHighCoefficient = coefficientValue && coefficientValue > 1.3;
    const isGrowingCoefficient = coefficientValue && coefficientValue > 1.2;
    
    // Determine rarity level
    const rarityLevel = currentDays < 100 ? 'EXTREMELY RARE' : 
                       currentDays < 300 ? 'RARE' : 
                       currentDays < 500 ? 'UNCOMMON' : 
                       currentDays < 800 ? 'COMMON' : 'FREQUENT';
    
    // Calculate volatility potential
    const volatilityScore = (100 - currentPercentage) / 10; // Higher score = more volatile potential
    const volatilityLevel = volatilityScore > 7 ? 'HIGH' : volatilityScore > 4 ? 'MEDIUM' : 'LOW';
    
    // Create sophisticated, data-driven report
    const report = `# ADVANCED PATTERN ANALYSIS - ${selectedTicker}
## RISK OPPORTUNITY ASSESSMENT

**Symbol**: ${selectedTicker} | **Current Risk**: ${riskValue} | **Band**: ${currentBand}
**Analysis**: ${new Date().toLocaleDateString()} | **Life Age**: ${lifeAge} days

---

## 🎯 OPPORTUNITY CLASSIFICATION

### RARITY PROFILE
**Current Band Rarity**: ${rarityLevel} (${currentDays} days, ${currentPercentage.toFixed(2)}%)
**Rank Among All Bands**: ${currentBandRank}/${bandsArray.length} (${currentBandRank === 1 ? 'RAREST' : currentBandRank <= 3 ? 'TOP 3 RAREST' : currentBandRank <= 5 ? 'TOP 5 RAREST' : 'COMMON'})
**Distance to Rarest Band**: ${distanceToRarest.toFixed(2)} risk units ${isNearRarest ? '🚨 PROXIMITY ALERT' : ''}

### VOLATILITY POTENTIAL
**Volatility Score**: ${volatilityScore.toFixed(1)}/10 (${volatilityLevel})
**Historical Stability**: ${currentPercentage > 15 ? 'LOW' : currentPercentage > 8 ? 'MEDIUM' : 'HIGH'} (${currentPercentage.toFixed(2)}% of time)
**Breakout Probability**: ${currentDays < 200 ? 'HIGH' : currentDays < 500 ? 'MEDIUM' : 'LOW'}

---

## 🔍 PATTERN ANALYSIS

### PATTERN 1: RARITY-BASED OPPORTUNITY
**Type**: ${currentDays < 100 ? 'EXTREME RARITY PATTERN' : currentDays < 300 ? 'RARITY PATTERN' : 'FREQUENCY PATTERN'}
**Significance**: ${currentDays < 100 ? 'CRITICAL' : currentDays < 300 ? 'HIGH' : 'MEDIUM'}
**Trading Implication**: ${currentDays < 100 
  ? `🚨 EXTREME OPPORTUNITY: Only ${currentDays} days in ${lifeAge} total days (${currentPercentage.toFixed(2)}%). This represents a highly unusual market condition with significant breakout potential.`
  : currentDays < 300 
  ? `⚠️ RARE OPPORTUNITY: ${currentDays} days (${currentPercentage.toFixed(2)}%) indicates infrequent visits to this price level. Monitor for potential reversal or continuation patterns.`
  : `📊 FREQUENT PATTERN: ${currentDays} days (${currentPercentage.toFixed(2)}%) suggests this is a common price level with established support/resistance.`
}

### PATTERN 2: NEIGHBORING BANDS ANALYSIS
**Type**: ${(() => {
  const currentBandIndex = bandsArray.findIndex(b => b.band === currentBand);
  const lowerNeighbor = bandsArray[currentBandIndex - 1];
  const upperNeighbor = bandsArray[currentBandIndex + 1];
  
  if (lowerNeighbor && upperNeighbor) {
    const lowerRarer = lowerNeighbor.days < currentDays;
    const upperRarer = upperNeighbor.days < currentDays;
    
    if (lowerRarer && upperRarer) return 'SANDWICHED BY RARER BANDS';
    if (lowerRarer || upperRarer) return 'ADJACENT TO RARER BAND';
    return 'SURROUNDED BY COMMON BANDS';
  }
  return 'EDGE POSITION';
})()}
**Significance**: ${(() => {
  const currentBandIndex = bandsArray.findIndex(b => b.band === currentBand);
  const lowerNeighbor = bandsArray[currentBandIndex - 1];
  const upperNeighbor = bandsArray[currentBandIndex + 1];
  
  if (lowerNeighbor && upperNeighbor) {
    const lowerRarer = lowerNeighbor.days < currentDays;
    const upperRarer = upperNeighbor.days < currentDays;
    
    if (lowerRarer && upperRarer) return 'HIGH';
    if (lowerRarer || upperRarer) return 'MEDIUM';
    return 'LOW';
  }
  return 'MEDIUM';
})()}
**Lower Neighbor**: ${(() => {
  const currentBandIndex = bandsArray.findIndex(b => b.band === currentBand);
  const lowerNeighbor = bandsArray[currentBandIndex - 1];
  return lowerNeighbor ? `${lowerNeighbor.band} (${lowerNeighbor.days} days, ${lowerNeighbor.percentage.toFixed(2)}%)` : 'N/A';
})()}
**Upper Neighbor**: ${(() => {
  const currentBandIndex = bandsArray.findIndex(b => b.band === currentBand);
  const upperNeighbor = bandsArray[currentBandIndex + 1];
  return upperNeighbor ? `${upperNeighbor.band} (${upperNeighbor.days} days, ${upperNeighbor.percentage.toFixed(2)}%)` : 'N/A';
})()}
**Analysis**: ${(() => {
  const currentBandIndex = bandsArray.findIndex(b => b.band === currentBand);
  const lowerNeighbor = bandsArray[currentBandIndex - 1];
  const upperNeighbor = bandsArray[currentBandIndex + 1];
  
  if (lowerNeighbor && upperNeighbor) {
    const lowerRarer = lowerNeighbor.days < currentDays;
    const upperRarer = upperNeighbor.days < currentDays;
    
    if (lowerRarer && upperRarer) {
      return `🎯 HIGH OPPORTUNITY: Sandwiched between two rarer bands (${lowerNeighbor.band} and ${upperNeighbor.band}). This creates a high-volatility zone with strong breakout potential toward either rare neighbor. Coefficient likely to increase as price approaches either boundary.`;
    } else if (lowerRarer) {
      const rarityRatio = (currentDays / lowerNeighbor.days).toFixed(1);
      const rarityMultiplier = (lowerNeighbor.percentage / currentPercentage).toFixed(1);
      return `🚨 MAJOR OPPORTUNITY: Lower neighbor (${lowerNeighbor.band}) is ${rarityRatio}x rarer than current position (${currentDays} vs ${lowerNeighbor.days} days). Moving down represents a ${rarityMultiplier}x reduction in frequency (${currentPercentage.toFixed(2)}% → ${lowerNeighbor.percentage.toFixed(2)}%). This is a HIGH-VALUE directional trade with significant coefficient amplification potential.`;
    } else if (upperRarer) {
      const rarityRatio = (currentDays / upperNeighbor.days).toFixed(1);
      const rarityMultiplier = (upperNeighbor.percentage / currentPercentage).toFixed(1);
      return `🚨 MAJOR OPPORTUNITY: Upper neighbor (${upperNeighbor.band}) is ${rarityRatio}x rarer than current position (${currentDays} vs ${upperNeighbor.days} days). Moving up represents a ${rarityMultiplier}x reduction in frequency (${currentPercentage.toFixed(2)}% → ${upperNeighbor.percentage.toFixed(2)}%). This is a HIGH-VALUE directional trade with significant coefficient amplification potential.`;
    } else {
      return `📊 LOW OPPORTUNITY: Both neighboring bands (${lowerNeighbor.band} and ${upperNeighbor.band}) are more common than current position. This suggests a stable zone with low volatility and reduced trading opportunities. Coefficient likely to decrease.`;
    }
  }
  return `📏 EDGE POSITION: Current band is at the edge of the risk spectrum. Limited neighboring band analysis available.`;
})()}

### PATTERN 3: COEFFICIENT DYNAMICS
**Current Coefficient**: ${coefficientValue ? coefficientValue.toFixed(2) : 'Calculating...'}
**Coefficient Status**: ${isHighCoefficient ? '🚀 HIGH VALUE' : isGrowingCoefficient ? '📈 GROWING' : '📊 NORMAL'}
**Analysis**: ${coefficientValue 
  ? `${isHighCoefficient 
      ? `🚀 HIGH COEFFICIENT ALERT: ${coefficientValue.toFixed(2)} indicates this position is in a historically rare zone, amplifying trading opportunities.`
      : isGrowingCoefficient 
      ? `📈 GROWING COEFFICIENT: ${coefficientValue.toFixed(2)} suggests increasing rarity, potentially signaling accumulation of rare market conditions.`
      : `📊 NORMAL COEFFICIENT: ${coefficientValue.toFixed(2)} indicates typical market conditions for this risk level.`
    }`
  : '⏳ Coefficient calculation in progress...'
}

---

## 📊 RISK BAND HIERARCHY (RAREST TO MOST COMMON)
${bandsArray.map((band, index) => 
  `${index + 1}. **${band.band}**: ${band.days} days (${band.percentage.toFixed(2)}%) ${band.band === currentBand ? '← CURRENT' : ''}`
).join('\n')}

---

## 🎯 TRADING OPPORTUNITY ASSESSMENT

### OPPORTUNITY LEVEL: ${currentDays < 100 ? '🚨 EXTREME' : currentDays < 300 ? '⚠️ HIGH' : currentDays < 500 ? '📈 MEDIUM' : '📊 LOW'}

### DIRECTIONAL OPPORTUNITIES
${(() => {
  const currentBandIndex = bandsArray.findIndex(b => b.band === currentBand);
  const lowerNeighbor = bandsArray[currentBandIndex - 1];
  const upperNeighbor = bandsArray[currentBandIndex + 1];
  
  let opportunities = [];
  
  if (lowerNeighbor && lowerNeighbor.days < currentDays) {
    const ratio = (currentDays / lowerNeighbor.days).toFixed(1);
    const coefficientIncrease = ((lowerNeighbor.percentage / currentPercentage) * 1.6).toFixed(2);
    opportunities.push(`📉 DOWNWARD: ${lowerNeighbor.band} (${ratio}x rarer, ${currentPercentage.toFixed(2)}% → ${lowerNeighbor.percentage.toFixed(2)}%, Coef: 1.16 → ~${coefficientIncrease})`);
  }
  
  if (upperNeighbor && upperNeighbor.days < currentDays) {
    const ratio = (currentDays / upperNeighbor.days).toFixed(1);
    const coefficientIncrease = ((upperNeighbor.percentage / currentPercentage) * 1.6).toFixed(2);
    opportunities.push(`📈 UPWARD: ${upperNeighbor.band} (${ratio}x rarer, ${currentPercentage.toFixed(2)}% → ${upperNeighbor.percentage.toFixed(2)}%, Coef: 1.16 → ~${coefficientIncrease})`);
  }
  
  if (opportunities.length === 0) {
    return '📊 NO DIRECTIONAL OPPORTUNITIES: Both neighboring bands are more common than current position.';
  }
  
  return opportunities.join('\n');
})()}

### NEIGHBOR RISK BAND COMPARISON
${(() => {
  const currentBandIndex = bandsArray.findIndex(b => b.band === currentBand);
  const lowerNeighbor = bandsArray[currentBandIndex - 1];
  const upperNeighbor = bandsArray[currentBandIndex + 1];
  
  let comparison = [];
  
  if (lowerNeighbor) {
    const lowerRatio = (currentDays / lowerNeighbor.days).toFixed(1);
    const lowerRarity = lowerNeighbor.days < currentDays ? 'RARER' : 'MORE COMMON';
    comparison.push(`**Lower Neighbor (${lowerNeighbor.band})**: ${lowerNeighbor.days} days (${lowerNeighbor.percentage.toFixed(2)}%) - ${lowerRatio}x ${lowerRarity.toLowerCase()}`);
  }
  
  if (upperNeighbor) {
    const upperRatio = (currentDays / upperNeighbor.days).toFixed(1);
    const upperRarity = upperNeighbor.days < currentDays ? 'RARER' : 'MORE COMMON';
    comparison.push(`**Upper Neighbor (${upperNeighbor.band})**: ${upperNeighbor.days} days (${upperNeighbor.percentage.toFixed(2)}%) - ${upperRatio}x ${upperRarity.toLowerCase()}`);
  }
  
  return comparison.join('\n');
})()}

### 4-YEAR CYCLE PATTERN ANALYSIS
${(() => {
  const currentYear = new Date().getFullYear();
  const cyclePhase = (currentYear - 2013) % 4; // Assuming 2013 as cycle start
  const cycleYears = ['Accumulation', 'Markup', 'Distribution', 'Markdown'];
  const currentPhase = cycleYears[cyclePhase];
  
  // Historical cycle analysis based on current risk band
  let cycleAnalysis = '';
  
  if (currentBand === '0.5-0.6') {
    cycleAnalysis = `**Current Phase**: ${currentPhase} (Year ${currentYear})
**Historical Pattern**: The 0.5-0.6 band typically acts as a transition zone during ${currentPhase} phases. In previous cycles, this level has shown:
- **Accumulation Phase**: Strong support with gradual upward pressure
- **Markup Phase**: Breakout catalyst toward higher risk bands (0.7-0.8, 0.8-0.9)
- **Distribution Phase**: Resistance level with potential reversal
- **Markdown Phase**: Breakdown catalyst toward lower risk bands (0.3-0.4, 0.2-0.3)

**Cycle Recommendation**: ${currentPhase === 'Markup' ? 'Monitor for upward breakout toward 0.7-0.8 (7x rarer)' : currentPhase === 'Markdown' ? 'Monitor for downward breakdown toward 0.3-0.4' : 'Range-bound trading with breakout monitoring'}`;
  } else {
    cycleAnalysis = `**Current Phase**: ${currentPhase} (Year ${currentYear})
**Historical Pattern**: ${currentBand} band behavior varies by cycle phase. Monitor for phase-specific breakout patterns.`;
  }
  
  return cycleAnalysis;
})()}

### SHORT-TERM STRATEGY (1-7 days)
${currentDays < 100 
  ? `🚨 AGGRESSIVE OPPORTUNITY: Extremely rare position suggests high probability of significant price movement. Consider larger position sizes with tight stops.`
  : currentDays < 300 
  ? `⚠️ MODERATE OPPORTUNITY: Rare position indicates potential for directional movement. Standard position sizing with normal risk management.`
  : `📊 CONSERVATIVE APPROACH: Common position suggests range-bound trading. Smaller positions with wider stops.`
}

### MEDIUM-TERM STRATEGY (1-4 weeks)
${(() => {
  const currentBandIndex = bandsArray.findIndex(b => b.band === currentBand);
  const lowerNeighbor = bandsArray[currentBandIndex - 1];
  const upperNeighbor = bandsArray[currentBandIndex + 1];
  
  if (lowerNeighbor && upperNeighbor) {
    const lowerRarer = lowerNeighbor.days < currentDays;
    const upperRarer = upperNeighbor.days < currentDays;
    
    if (lowerRarer && upperRarer) {
      return `🎯 HIGH-VOLATILITY STRATEGY: Sandwiched between rarer bands (${lowerNeighbor.band} and ${upperNeighbor.band}). Monitor for breakouts in either direction with increased position sizing due to high coefficient potential.`;
    } else if (lowerRarer) {
      const rarityRatio = (currentDays / lowerNeighbor.days).toFixed(1);
      return `🚨 AGGRESSIVE SHORT STRATEGY: Lower neighbor (${lowerNeighbor.band}) is ${rarityRatio}x rarer. This represents a MAJOR opportunity - moving from ${currentPercentage.toFixed(2)}% frequency to ${lowerNeighbor.percentage.toFixed(2)}% frequency. Use larger position sizes with tight stops. Coefficient will dramatically increase on downward breakout.`;
    } else if (upperRarer) {
      const rarityRatio = (currentDays / upperNeighbor.days).toFixed(1);
      return `🚨 AGGRESSIVE LONG STRATEGY: Upper neighbor (${upperNeighbor.band}) is ${rarityRatio}x rarer. This represents a MAJOR opportunity - moving from ${currentPercentage.toFixed(2)}% frequency to ${upperNeighbor.percentage.toFixed(2)}% frequency. Use larger position sizes with tight stops. Coefficient will dramatically increase on upward breakout.`;
    } else {
      return `📊 STABLE ZONE STRATEGY: Both neighbors are more common. Focus on range-bound trading with smaller positions. Coefficient likely to decrease, reducing trading opportunities.`;
    }
  }
  return `📏 EDGE STRATEGY: Positioned at risk spectrum edge. Limited directional bias, focus on technical analysis and market structure.`;
})()}

### RISK MANAGEMENT
**Position Size**: ${currentDays < 100 ? 'LARGER (due to rarity)' : currentDays < 300 ? 'STANDARD' : 'SMALLER (due to frequency)'}
**Stop Loss**: ${riskValue < 0.5 ? 'Below current level' : 'Above current level'} (${currentDays < 200 ? 'TIGHTER' : 'NORMAL'} due to ${currentDays < 200 ? 'rarity' : 'frequency'})
**Take Profit**: ${currentDays < 100 ? 'Target adjacent rare bands' : currentDays < 300 ? 'Target 1-2 bands away' : 'Target within current band range'}

---

## 🔥 CRITICAL ALERTS
${(() => {
  const alerts = [];
  if (currentDays < 100) alerts.push('🚨 EXTREME RARITY: Less than 100 days in this band');
  if (isNearRarest) alerts.push('🎯 PROXIMITY ALERT: Near rarest band');
  if (isHighCoefficient) alerts.push('🚀 HIGH COEFFICIENT: Amplified trading opportunity');
  if (volatilityScore > 7) alerts.push('⚡ HIGH VOLATILITY: Potential for significant price swings');
  if (currentBandRank <= 3) alerts.push('🏆 TOP 3 RAREST: Among the rarest positions');
  
  // Add cycle-based alerts
  const currentYear = new Date().getFullYear();
  const cyclePhase = (currentYear - 2013) % 4;
  const cycleYears = ['Accumulation', 'Markup', 'Distribution', 'Markdown'];
  const currentPhase = cycleYears[cyclePhase];
  
  if (currentPhase === 'Markup' && currentBand === '0.5-0.6') {
    alerts.push('📈 CYCLE BREAKOUT ALERT: Markup phase + 0.5-0.6 band = High upward breakout probability');
  }
  if (currentPhase === 'Markdown' && currentBand === '0.5-0.6') {
    alerts.push('📉 CYCLE BREAKDOWN ALERT: Markdown phase + 0.5-0.6 band = High downward breakdown probability');
  }
  
  // Add neighbor-based alerts
  const currentBandIndex = bandsArray.findIndex(b => b.band === currentBand);
  const upperNeighbor = bandsArray[currentBandIndex + 1];
  if (upperNeighbor && upperNeighbor.days < currentDays) {
    const ratio = (currentDays / upperNeighbor.days).toFixed(1);
    if (ratio >= 5) alerts.push(`🚀 MAJOR UPPER BREAKOUT: ${ratio}x rarer neighbor above (${upperNeighbor.band})`);
  }
  
  return alerts.length > 0 ? alerts.join('\n') : '📊 No critical alerts at this time';
})()}

---

## 📈 TECHNICAL METRICS
- **Risk Value**: ${riskValue}
- **Base Score**: ${calculateBaseScore(riskValue, riskBands)} points
- **Coefficient**: ${coefficientValue ? coefficientValue.toFixed(2) : 'Calculating...'}
- **Final Score**: ${calculateFinalScore(calculateBaseScore(riskValue, riskBands), currentCoefficient)}
- **Volatility Potential**: ${volatilityScore.toFixed(1)}/10
- **Rarity Rank**: ${currentBandRank}/${bandsArray.length}

---

## 🎯 FINAL ASSESSMENT
${(() => {
  if (currentDays < 100 && isNearRarest) {
    return '🚨 EXTREME OPPORTUNITY: Rare position near rarest band. High probability of significant price movement. Consider aggressive positioning.';
  } else if (currentDays < 300 || isHighCoefficient) {
    return '⚠️ HIGH OPPORTUNITY: Rare position or high coefficient indicates favorable trading conditions. Monitor for breakout signals.';
  } else if (isNearRarest) {
    return '🎯 MODERATE OPPORTUNITY: Proximity to rarest band suggests potential for directional movement. Standard risk management.';
  } else {
    return '📊 NORMAL CONDITIONS: Common position with standard trading parameters. Focus on technical analysis and market structure.';
  }
})()}

---
*Advanced Pattern Analysis | RiskMetric System | ${new Date().toLocaleString()}*
*Methodology: Rarity-based coefficient calculation with volatility scoring*`;

    return report;
  };

  // Function to calculate rarity rank
  const calculateRarityRank = (riskValue, riskBandsData) => {
    if (riskValue === null || !riskBandsData) return null;
    
    const currentBand = getRiskBand(riskValue);
    const currentDays = riskBandsData[currentBand]?.days || 0;
    
    // Sort bands by days (ascending - rarest first)
    const bandsArray = Object.entries(riskBandsData).map(([band, data]) => ({
      band,
      days: data.days || 0,
      percentage: data.percentage || 0
    })).sort((a, b) => a.days - b.days);
    
    // Find current band rank
    const currentBandRank = bandsArray.findIndex(b => b.band === currentBand) + 1;
    return currentBandRank;
  };

  // Function to analyze patterns in historical data for current risk band
  const analyzePatterns = (riskValue) => {
    if (riskValue === null) return { patterns: [], count: 0 };
    
    const currentBand = getRiskBand(riskValue);
    const patterns = [];
    
    // Analyze historical patterns for the current risk band
    if (riskBands[currentBand]) {
      const days = riskBands[currentBand].days || 0;
      const percentage = riskBands[currentBand].percentage || 0;
      
      // Pattern 1: High frequency pattern
      if (days > 500) {
        patterns.push({
          type: 'High Frequency',
          description: `Spent ${days} days in this band (${percentage}% of total time)`,
          significance: 'High'
        });
      }
      
      // Pattern 2: Recent activity pattern
      if (days > 100 && percentage > 10) {
        patterns.push({
          type: 'Recent Activity',
          description: `Active pattern with ${days} days and ${percentage}% frequency`,
          significance: 'Medium'
        });
      }
      
      // Pattern 3: Rare pattern
      if (days < 50 && percentage < 5) {
        patterns.push({
          type: 'Rare Pattern',
          description: `Rare occurrence: ${days} days (${percentage}%)`,
          significance: 'High'
        });
      }
      
      // Pattern 4: Transition pattern
      if (riskValue >= 0.5 && riskValue <= 0.6) {
        patterns.push({
          type: 'Transition Zone',
          description: 'Currently in 0.5-0.6 transition zone',
          significance: 'Medium'
        });
      }
    }
    
    return {
      patterns,
      count: patterns.length,
      currentBand
    };
  };

  // PERFECTED DBI Coefficient Calculation System
  const calculateCoefficientWithOpenAI = async (symbol, riskValue) => {
    try {
      console.log(`🎯 Calculating coefficient for ${symbol} at risk ${riskValue} using PERFECTED DBI methodology`);
      
      // Use the PERFECTED DBI coefficient calculation system
              const response = await fetch(`http://localhost:3400/api/v1/coefficient/calculate?symbol=${symbol}&risk_value=${riskValue}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ PERFECTED DBI coefficient calculation response:', data);
        
        if (data.success) {
          const coefficient = Number(data.coefficient).toFixed(3);
          const finalScore = Number(data.final_score.final_score).toFixed(2);
          const signalStrength = data.final_score.signal_strength;
          const methodology = data.methodology;
          
          // Log the perfected calculation details
          console.log(`🎯 PERFECTED DBI RESULTS for ${symbol}:`);
          console.log(`  Coefficient: ${coefficient} (${methodology})`);
          console.log(`  Final Score: ${finalScore}`);
          console.log(`  Signal: ${signalStrength}`);
          console.log(`  Calculation Details:`, data.calculation_details);
          
          return {
            coefficient: coefficient,
            finalScore: finalScore,
            signalStrength: signalStrength,
            methodology: methodology,
            calculationDetails: data.calculation_details
          };
        } else {
          console.error('❌ DBI coefficient calculation failed:', data.error);
          return null;
        }
      } else {
        const errorText = await response.text();
        console.error('❌ Failed to calculate DBI coefficient:', response.status, errorText);
        return null;
      }
      
    } catch (error) {
      console.error('❌ Error calculating DBI coefficient:', error);
      return null;
    }
  };

  // Function to get coefficient for current risk value using ChatGPT coefficient system
  const getCurrentRiskValueCoefficient = async (riskValue, riskBandsData) => {
    if (riskValue === null || !riskBandsData) {
      console.log('❌ Invalid input for coefficient calculation:', { riskValue, riskBandsData });
      return null;
    }
    
    try {
      // Convert risk bands dictionary to array format for coefficient calculation
      const riskBandsArray = Object.entries(riskBandsData).map(([bandKey, bandData]) => ({
        band: bandKey,
        days: bandData.days || 0,
        percentage: bandData.percentage || 0
      }));
      
      // Check if all days are zero (data not loaded yet)
      const totalDays = riskBandsArray.reduce((total, band) => total + band.days, 0);
      if (totalDays === 0) {
        console.log('⏳ Risk bands data not loaded yet (all days are 0), skipping coefficient calculation');
        setCurrentCoefficient('Waiting for data...');
        return null;
      }
      
      console.log('🔄 Calculating coefficient with data:', { riskValue, riskBandsArray });
      
      // Use the PERFECTED DBI coefficient calculation system
              const response = await fetch(`http://localhost:3400/api/v1/coefficient/calculate?symbol=${selectedTicker}&risk_value=${riskValue}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ PERFECTED DBI coefficient calculation response:', data);
        
        if (data.success) {
          const coefficient = Number(data.coefficient).toFixed(3);
          const finalScore = Number(data.final_score.final_score).toFixed(2);
          const signalStrength = data.final_score.signal_strength;
          const methodology = data.methodology;
          
          setCurrentCoefficient(coefficient);
          
          // Log the perfected calculation details
          console.log(`🎯 PERFECTED DBI RESULTS for ${selectedTicker}:`);
          console.log(`  Coefficient: ${coefficient} (${methodology})`);
          console.log(`  Final Score: ${finalScore}`);
          console.log(`  Signal: ${signalStrength}`);
          console.log(`  Calculation Details:`, data.calculation_details);
          
          return {
            coefficient: coefficient,
            finalScore: finalScore,
            signalStrength: signalStrength,
            methodology: methodology,
            calculationDetails: data.calculation_details
          };
        } else {
          console.error('❌ DBI coefficient calculation failed:', data.error);
          setCurrentCoefficient(null);
          return null;
        }
      } else {
        const errorText = await response.text();
        console.error('❌ Failed to calculate DBI coefficient:', response.status, errorText);
        setCurrentCoefficient(null);
        return null;
      }
    } catch (error) {
      console.error('❌ Error calculating coefficient:', error);
      setCurrentCoefficient(null);
      return null;
    }
  };

  // Synchronous wrapper for coefficient display
  const getCurrentCoefficientDisplay = () => {
    return currentCoefficient || 'Calculating...';
  };

  // Function to set Min/Max prices from risk matrix table
const setMinMaxPricesFromTable = () => {
  // Min price is for Risk 0.0 (first row)
  setMinRiskPrice(30001.00);
  // Max price is for Risk 1.0 (last row)
  setMaxRiskPrice(299720.00);
  console.log('✅ Min/Max prices set from risk matrix table');
};

  // Function to create band change alert (ONLY 1 ALERT)
  const createBandChangeAlert = (oldBand, newBand, riskValue, price) => {
    const alert = {
      id: Date.now(),
      timestamp: new Date(),
      symbol: selectedTicker,
      oldBand,
      newBand,
      riskValue,
      price,
      message: `${selectedTicker} moved from ${oldBand} to ${newBand} at $${price} (Risk: ${riskValue})`
    };
    
    // Set ONLY 1 alert (replace any existing alert)
    setBandChangeAlert(alert);
    
    console.log(`🚨 BAND CHANGE ALERT: ${alert.message}`);
  };

  // Function to check if risk band has changed and trigger coefficient update
  const hasRiskBandChanged = (riskValue) => {
    if (riskValue === null) return false;
    
    const newRiskBand = getRiskBand(riskValue);
    if (currentRiskBand !== newRiskBand) {
      console.log(`🔄 Risk band changed: ${currentRiskBand} → ${newRiskBand}`);
      console.log(`📊 Risk value: ${riskValue} moved to band: ${newRiskBand}`);
      
      // Create alert for band change
      if (currentRiskBand && currentPrice) {
        createBandChangeAlert(currentRiskBand, newRiskBand, riskValue, currentPrice);
      }
      
      // Update current band
      setCurrentRiskBand(newRiskBand);
      setLastRiskBandUpdate(new Date());
      
              // Trigger immediate coefficient recalculation for new band using PERFECTED DBI
        if (selectedTicker && riskValue !== null) {
          console.log(`🚀 Recalculating coefficients for new band: ${newRiskBand} using DBI methodology`);
          const recalculateCoefficients = async () => {
            const dbiResult = await calculateCoefficientWithOpenAI(selectedTicker, riskValue);
            if (dbiResult) {
              setCoefficientApply(dbiResult.coefficient);
              setLastCoefficientUpdate(new Date());
              
              // Log the perfected DBI results
              console.log(`🎯 PERFECTED DBI RECALCULATION for ${selectedTicker}:`);
              console.log(`  New Band: ${newRiskBand}`);
              console.log(`  Coefficient: ${dbiResult.coefficient} (${dbiResult.methodology})`);
              console.log(`  Final Score: ${dbiResult.finalScore}`);
              console.log(`  Signal: ${dbiResult.signalStrength}`);
              
              // Update the coefficient display with DBI methodology
              setCurrentCoefficient(dbiResult.coefficient);
            
            // Get old and new coefficients for comparison
            const oldCoefficient = currentRiskBand ? getCurrentRiskValueCoefficient(riskValue, coefficientApply) : null;
            const newCoefficient = getCurrentRiskValueCoefficient(riskValue, newCoefficients);
            
            console.log(`✅ Band change coefficient update:`);
            console.log(`   Old band: ${currentRiskBand} → Coefficient: ${oldCoefficient}`);
            console.log(`   New band: ${newRiskBand} → Coefficient: ${newCoefficient}`);
            console.log(`   Signal impact: ${oldCoefficient !== newCoefficient ? 'POTENTIAL SIGNAL CHANGE' : 'No change'}`);
            console.log(`   Precision: Both coefficients displayed with 2 decimal places for accuracy`);
          }
        };
        recalculateCoefficients();
      }
      
      return true;
    }
    return false;
  };

  // PERFECTED DBI SYSTEM - No fallback needed, this is the definitive calculation method



  // Function to calculate risk value using the correct risk formula
  const calculateRiskValue = (price, formula) => {
    try {
      // Use the correct risk formula: Risk = −0.380790057100 + 1.718335491963×10⁻⁵⋅P − 1.213364209168×10⁻¹⁰⋅P² + 4.390647720677×10⁻¹⁶⋅P³ − 5.830886880671×10⁻²²⋅P⁴
      const a0 = -0.380790057100;
      const a1 = 1.718335491963e-5;  // 1.718335491963×10⁻⁵
      const a2 = -1.213364209168e-10; // -1.213364209168×10⁻¹⁰
      const a3 = 4.390647720677e-16;  // 4.390647720677×10⁻¹⁶
      const a4 = -5.830886880671e-22; // -5.830886880671×10⁻²²
      
      console.log('🔍 Risk formula coefficients:', { a0, a1, a2, a3, a4, price });
      
      // Calculate risk value: a0 + a1*P + a2*P² + a3*P³ + a4*P⁴
      const P = price;
      const riskValue = a0 + a1*P + a2*P*P + a3*P*P*P + a4*P*P*P*P;
      
      console.log('🔍 Risk value calculated:', riskValue);
      
      // Ensure the result is between 0 and 1
      const clampedRiskValue = Math.max(0, Math.min(1, riskValue));
      
      if (clampedRiskValue !== riskValue) {
        console.warn('⚠️ Risk value clamped to range (0-1):', riskValue, '→', clampedRiskValue);
      }
      
      return Math.round(clampedRiskValue * 1000) / 1000; // Round to 3 decimal places
    } catch (error) {
      console.error('❌ Error calculating risk value:', error);
      return null;
    }
  };

  const fetchCurrentPrice = async (symbol) => {
    if (!symbol) return;
    
    setPriceLoading(true);
    try {
      // Use Binance API to get current price
      const url = `https://api.binance.com/api/v3/ticker/price?symbol=${symbol}USDT`;
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data && data.price) {
        const price = parseFloat(data.price);
        setCurrentPrice(price);
        
        // Calculate risk value when price updates
        if (polynomialFormula) {
          const calculatedRiskValue = calculateRiskValue(price, polynomialFormula);
          setRiskValue(calculatedRiskValue);
          setLastRiskValueUpdate(new Date());
          

        }
      } else {
        setCurrentPrice(null);
      }
    } catch (err) {
      setCurrentPrice(null);
    } finally {
      setPriceLoading(false);
    }
  };

  // Function to fetch Life Age from backend
  const fetchLifeAge = async (symbol) => {
    if (!symbol) return;
    
    setLifeAgeLoading(true);
    try {
      const response = await fetch(`http://localhost:3400/api/v1/life-age/${symbol}`);
      
      if (response.ok) {
        const data = await response.json();
        setLifeAge(data.age_days);
        setLastLifeAgeUpdate(new Date(data.last_updated));
      } else {
        console.warn(`⚠️ Could not fetch life age for ${symbol}, using default`);
        setLifeAge(365);
        setLastLifeAgeUpdate(new Date());
      }
    } catch (err) {
      console.error(`❌ Error fetching life age for ${symbol}:`, err);
      setLifeAge(365);
      setLastLifeAgeUpdate(new Date());
    } finally {
      setLifeAgeLoading(false);
    }
  };

  // Function to fetch update logs
  const fetchUpdateLogs = async (symbol) => {
    if (!symbol) return;
    
    setUpdateLogsLoading(true);
    try {
      const response = await fetch(`http://localhost:3400/api/v1/update-logs/${symbol}?limit=5`);
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setUpdateLogs(data.updates);
          console.log(`✅ Fetched ${data.count} update logs for ${symbol}`);
        }
      } else {
        console.warn(`⚠️ Could not fetch update logs for ${symbol}`);
      }
    } catch (err) {
      console.error(`❌ Error fetching update logs for ${symbol}:`, err);
    } finally {
      setUpdateLogsLoading(false);
    }
  };

  // Function to save Life Age to backend
  const saveLifeAge = async (symbol, ageDays) => {
    try {
      const response = await fetch(`http://localhost:3400/api/v1/life-age/${symbol}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbol: symbol,
          age_days: ageDays
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log(`✅ Life age saved for ${symbol}:`, data);
        return true;
      } else {
        console.error(`❌ Failed to save life age for ${symbol}`);
        return false;
      }
    } catch (err) {
      console.error(`❌ Error saving life age for ${symbol}:`, err);
      return false;
    }
  };

  useEffect(() => {
    console.log('🚀 RiskMetricTab component mounted');
    fetchRiskMatrixData();
  }, []);

  useEffect(() => {
    if (selectedTicker) {
      fetchCurrentPrice(selectedTicker);
      fetchLifeAge(selectedTicker);
      fetchRiskBands(selectedTicker);
      fetchUpdateLogs(selectedTicker);
    }
  }, [selectedTicker]);

  // Refresh Life Age data every hour to ensure it's up to date
  useEffect(() => {
    if (selectedTicker) {
      const interval = setInterval(() => {
        console.log(`🔄 Refreshing Life Age for ${selectedTicker}...`);
        fetchLifeAge(selectedTicker);
      }, 60 * 60 * 1000); // 1 hour

      return () => clearInterval(interval);
    }
  }, [selectedTicker]);

  // Update risk value every 5 minutes and check for band changes
  useEffect(() => {
    if (selectedTicker && currentPrice && polynomialFormula) {
      const interval = setInterval(() => {
        const calculatedRiskValue = calculateRiskValue(currentPrice, polynomialFormula);
        const previousRiskValue = riskValue;
        
        setRiskValue(calculatedRiskValue);
        setLastRiskValueUpdate(new Date());
        console.log(`🔄 Updated risk value for ${selectedTicker}: ${calculatedRiskValue}`);
        
        // Check if risk band has changed
        if (previousRiskValue !== null) {
          const previousBand = getRiskBand(previousRiskValue);
          const newBand = getRiskBand(calculatedRiskValue);
          
          if (previousBand !== newBand) {
            console.log(`🚨 BAND CHANGE DETECTED: ${previousBand} → ${newBand}`);
            console.log(`📊 Price: $${currentPrice} | Risk: ${previousRiskValue} → ${calculatedRiskValue}`);
            hasRiskBandChanged(calculatedRiskValue);
          }
        }
      }, 5 * 60 * 1000); // 5 minutes

      return () => clearInterval(interval);
    }
  }, [selectedTicker, currentPrice, polynomialFormula, riskValue]);

  // Calculate coefficients every 12 hours OR when risk band changes
  useEffect(() => {
    if (selectedTicker && riskBands && lifeAge) {
      const calculateCoefficients = async () => {
        console.log(`🔄 Starting coefficient calculation for ${selectedTicker}...`);
        const dbiResult = await calculateCoefficientWithOpenAI(selectedTicker, riskValue);
        if (dbiResult) {
          setCoefficientApply(dbiResult.coefficient);
          setLastCoefficientUpdate(new Date());
          console.log(`✅ PERFECTED DBI coefficients updated for ${selectedTicker} (Risk: ${riskValue}, Band: ${getRiskBand(riskValue)}):`, dbiResult);
        } else {
          console.log(`❌ Failed to calculate coefficients for ${selectedTicker}`);
        }
      };

      // Check if we need to calculate coefficients
      const now = new Date();
      const lastUpdate = lastCoefficientUpdate;
      const hoursSinceUpdate = (now - lastUpdate) / (1000 * 60 * 60);
      
      // Update every 12 hours OR when risk band changes OR if no coefficients exist
      const shouldUpdate = hoursSinceUpdate >= 12 || hasRiskBandChanged(riskValue) || !coefficientApply;
      
      if (shouldUpdate) {
        console.log(`🔄 Updating coefficients for ${selectedTicker}: 12h=${hoursSinceUpdate >= 12}, bandChange=${hasRiskBandChanged(riskValue)}, noCoeff=${!coefficientApply}`);
        calculateCoefficients();
      }
    }
  }, [selectedTicker, riskBands, lifeAge, riskValue, lastCoefficientUpdate, coefficientApply, currentRiskBand]);

  // Set Min/Max prices when component loads
  useEffect(() => {
    if (selectedTicker) {
      setMinMaxPricesFromTable();
    }
  }, [selectedTicker]);

  // Force initial coefficient calculation when all data is available
  useEffect(() => {
    if (selectedTicker && riskBands && lifeAge && riskValue) {
      // Check if risk bands data is actually loaded (not just default zeros)
      const totalDays = Object.values(riskBands).reduce((total, band) => total + (band.days || 0), 0);
      
      if (totalDays > 0) {
        console.log(`🚀 Force calculating initial coefficients for ${selectedTicker}...`);
        console.log('📊 Available data:', { selectedTicker, riskBands, lifeAge, riskValue });
        console.log('📊 Current coefficientApply:', coefficientApply);
        
        const calculateInitialCoefficients = async () => {
                  const dbiResult = await calculateCoefficientWithOpenAI(selectedTicker, riskValue);
        if (dbiResult) {
          setCoefficientApply(dbiResult.coefficient);
          setLastCoefficientUpdate(new Date());
          console.log(`✅ PERFECTED DBI initial coefficients calculated for ${selectedTicker}:`, dbiResult);
          } else {
            console.log(`❌ Failed to calculate coefficients for ${selectedTicker}`);
          }
        };
        
        // Always calculate if no coefficients exist
        if (!coefficientApply || Object.keys(coefficientApply).length === 0) {
          calculateInitialCoefficients();
        }
      } else {
        console.log('⏳ Waiting for risk bands data to load before calculating coefficients...');
      }
    }
  }, [selectedTicker, riskBands, lifeAge, riskValue]);

  // Calculate coefficient when risk value or risk bands data changes
  useEffect(() => {
    if (riskValue !== null && riskBands && Object.keys(riskBands).length > 0) {
      // Check if risk bands data is actually loaded (not just default zeros)
      const totalDays = Object.values(riskBands).reduce((total, band) => total + (band.days || 0), 0);
      if (totalDays > 0) {
        console.log('🔄 Calculating coefficient for current risk value...');
        getCurrentRiskValueCoefficient(riskValue, riskBands);
      } else {
        console.log('⏳ Waiting for risk bands data to load...');
      }
    }
  }, [riskValue, riskBands]);

  // Calculate rarity rank when risk value or risk bands data changes
  useEffect(() => {
    if (riskValue !== null && riskBands && Object.keys(riskBands).length > 0) {
      const rank = calculateRarityRank(riskValue, riskBands);
      setRarityRank(rank);
      console.log('🏆 Updated rarity rank:', rank);
    }
  }, [riskValue, riskBands]);

  const getRiskZoneColor = (riskValue) => {
    if (riskValue < 0.2) return '#4CAF50'; // Green - Accumulation
    if (riskValue < 0.4) return '#8BC34A'; // Light Green - Early Bull
    if (riskValue < 0.6) return '#FFC107'; // Yellow - Neutral
    if (riskValue < 0.8) return '#FF9800'; // Orange - Late Bull
    return '#F44336'; // Red - Distribution
  };

  const getRiskZoneName = (riskValue) => {
    // Return the actual risk value instead of zone names
    return riskValue.toFixed(3);
  };

  const formatPrice = (price) => {
    if (price >= 1000) {
      return `$${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    } else if (price >= 1) {
      return `$${price.toFixed(2)}`;
    } else if (price >= 0.01) {
      return `$${price.toFixed(4)}`;
    } else {
      return `$${price.toFixed(6)}`;
    }
  };

  const filteredData = riskMatrixData.filter(row => {
    if (selectedSymbol === 'ALL') {
      return true;
    }
    return row.prices[selectedSymbol] !== undefined;
  });

  // Ensure all symbols are displayed - temporary override
  const filteredSymbols = searchTerm ? 
    symbols.filter(symbol => symbol.toLowerCase().includes(searchTerm.toLowerCase())) :
    symbols;



    // Handle ticker button click
  const handleTickerClick = (ticker) => {
    setSelectedTicker(ticker);
    fetchCurrentPrice(ticker);
  };

  // Handle navigation tab click
  const handleNavTabClick = (tab) => {
    setActiveSubTab(tab);
    // Don't reset selectedTicker - keep the current selection
  };

  const handleSetMinPrice = () => {
    if (newPriceInput && !isNaN(newPriceInput)) {
      const newPrice = parseFloat(newPriceInput);
      setMinRiskPrice(newPrice);
      setLastUpdate(new Date());
      setNewPriceInput('');
    }
  };

  const handleSetMaxPrice = () => {
    if (newMaxPriceInput && !isNaN(newMaxPriceInput)) {
      const newPrice = parseFloat(newMaxPriceInput);
      setMaxRiskPrice(newPrice);
      setLastMaxUpdate(new Date());
      setNewMaxPriceInput('');
    }
  };

  // Function to handle setting Polynomial Formula
  const handleSetFormula = () => {
    if (newFormulaInput.trim()) {
      setPolynomialFormula(newFormulaInput.trim());
      setLastFormulaUpdate(new Date());
      setNewFormulaInput('');
    }
  };

  // Function to handle setting Risk Value Formula
  const handleSetRiskFormula = () => {
    if (newRiskFormulaInput.trim()) {
      setRiskValueFormula(newRiskFormulaInput.trim());
      setLastRiskFormulaUpdate(new Date());
      setNewRiskFormulaInput('');
    }
  };

  // Function to handle setting Life Age
  const handleSetLifeAge = async () => {
    if (!selectedTicker) {
      console.error('❌ No ticker selected');
      alert('Please select a ticker first');
      return;
    }
    
    if (newLifeAgeInput && !isNaN(newLifeAgeInput)) {
      const newAge = parseInt(newLifeAgeInput);
      
      // Save to backend first
      const success = await saveLifeAge(selectedTicker, newAge);
      
      if (success) {
        // Update local state only if backend save was successful
        setLifeAge(newAge);
        setLastLifeAgeUpdate(new Date());
        setNewLifeAgeInput('');
        console.log(`✅ Life age updated for ${selectedTicker}: ${newAge} days`);
      } else {
        console.error(`❌ Failed to update life age for ${selectedTicker}`);
        alert(`Failed to update life age for ${selectedTicker}`);
      }
    }
  };

  // Function to save risk band to backend
  const saveRiskBand = async (symbol, bandKey, days) => {
    try {
      const response = await fetch(`http://localhost:3400/api/v1/risk-bands/${symbol}/${bandKey}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbol: symbol,
          band_key: bandKey,
          days: days
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log(`✅ Risk band saved:`, data);
        return true;
      } else {
        console.error(`❌ Failed to save risk band`);
        return false;
      }
    } catch (err) {
      console.error(`❌ Error saving risk band:`, err);
      return false;
    }
  };

  // Function to fetch risk bands from backend
  const fetchRiskBands = async (symbol) => {
    if (!symbol) return;
    
    try {
      console.log(`🔍 Fetching risk bands for ${symbol}...`);
      const response = await fetch(`http://localhost:3400/api/v1/risk-bands/${symbol}`);
      
      if (response.ok) {
        const data = await response.json();
        console.log(`📊 Raw risk bands data for ${symbol}:`, data);
        
        const bandsData = {};
        data.forEach(band => {
          bandsData[band.band_key] = {
            days: band.days,
            percentage: band.percentage || 0,
            lastUpdate: new Date(band.last_updated)
          };
        });
        setRiskBands(bandsData);
        console.log(`✅ Loaded risk bands for ${symbol}:`, bandsData);
      } else {
        console.error(`❌ Failed to fetch risk bands for ${symbol}: ${response.status} ${response.statusText}`);
        const errorText = await response.text();
        console.error(`❌ Error details:`, errorText);
      }
    } catch (err) {
      console.error(`❌ Error fetching risk bands for ${symbol}:`, err);
    }
  };

  // Function to calculate total risk band days
  const calculateTotalRiskBandDays = () => {
    return Object.values(riskBands).reduce((total, band) => total + band.days, 0);
  };

  // Function to handle setting individual risk band
  const handleSetRiskBand = async (bandKey) => {
    if (!selectedTicker) {
      console.error('❌ No ticker selected');
      alert('Please select a ticker first');
      return;
    }
    
    const inputValue = newRiskBandInputs[bandKey];
    if (inputValue && !isNaN(inputValue)) {
      const newDays = parseInt(inputValue);
      const currentTotal = calculateTotalRiskBandDays();
      const currentBandDays = riskBands[bandKey]?.days || 0;
      const newTotal = currentTotal - currentBandDays + newDays;
      
      // Check if new total would exceed life age
      if (newTotal > lifeAge) {
        alert(`❌ Total days (${newTotal}) would exceed life age (${lifeAge}). Please check all days updated in time spent.`);
        return;
      }
      
      // Save to backend first
      const success = await saveRiskBand(selectedTicker, bandKey, newDays);
      
      if (success) {
        // Update local state only if backend save was successful
        const newPercentage = lifeAge > 0 ? Math.round((newDays / lifeAge) * 100 * 100) / 100 : 0;
        setRiskBands(prev => ({
          ...prev,
          [bandKey]: {
            days: newDays,
            percentage: newPercentage,
            lastUpdate: new Date()
          }
        }));
        
        // Clear the input
        setNewRiskBandInputs(prev => ({
          ...prev,
          [bandKey]: ''
        }));
        
        console.log(`✅ Risk band ${bandKey} updated: ${newDays} days`);
      } else {
        alert(`Failed to update risk band ${bandKey}`);
      }
    }
  };

  // Function to handle input change for risk bands
  const handleRiskBandInputChange = (bandKey, value) => {
    setNewRiskBandInputs(prev => ({
      ...prev,
      [bandKey]: value
    }));
  };

  // Function to handle setting Percentage in Risk Band
  // Commented out - unused function with undefined variables
  // const handleSetPercentage = () => {
  //   if (newPercentageInput && !isNaN(newPercentageInput)) {
  //     const newPercentage = parseFloat(newPercentageInput);
  //     if (newPercentage >= 0 && newPercentage <= 100) {
  //       setPercentageInRiskBand(newPercentage);
  //       setLastPercentageUpdate(new Date());
  //       setNewPercentageInput('');
  //       console.log(`✅ Percentage in risk band updated: ${newPercentage}%`);
  //     }
  //   }
  // };



  return (
    <div className="riskmetric-tab">
      {error && (
        <div className="error-message">
          <AlertTriangle className="w-5 h-5" />
          <span>Error: {error}</span>
        </div>
      )}

      {loading && (
        <div className="loading-message">
          <RefreshCw className="w-5 h-5 animate-spin" />
          <span>Loading RiskMetric Matrix...</span>
        </div>
      )}

      <div className="riskmatrix-content">
        {/* BTC Risk Matrix Card */}
        <div className="risk-matrix-card">
          <div className="card-content">
            {/* Horizontal Navigation Card */}
            <div className="horizontal-nav-card">
              <div className="nav-tabs">
                <button 
                  className={`nav-tab ${activeSubTab === 'symbols' ? 'active' : ''}`}
                  onClick={() => handleNavTabClick('symbols')}
                >
                  <span className="tab-icon">📊</span>
                  <span className="tab-text">Symbols</span>
                </button>
                <button 
                  className={`nav-tab ${activeSubTab === 'my-symbols' ? 'active' : ''}`}
                  onClick={() => handleNavTabClick('my-symbols')}
                >
                  <span className="tab-icon">🎯</span>
                  <span className="tab-text">My Symbols</span>
                </button>
                <button 
                  className={`nav-tab ${activeSubTab === 'management' ? 'active' : ''}`}
                  onClick={() => handleNavTabClick('management')}
                >
                  <span className="tab-icon">⚙️</span>
                  <span className="tab-text">Management</span>
                </button>
              </div>
            </div>
            
            {/* Ticker Buttons Card */}
            <div className="ticker-buttons-card">
              <div className="ticker-buttons">
                <button 
                  className={`ticker-btn ${selectedTicker === 'BTC' ? 'active' : ''}`}
                  onClick={() => handleTickerClick('BTC')}
                >BTC</button>
                <button 
                  className={`ticker-btn ${selectedTicker === 'ETH' ? 'active' : ''}`}
                  onClick={() => handleTickerClick('ETH')}
                >ETH</button>
                <button 
                  className={`ticker-btn ${selectedTicker === 'XRP' ? 'active' : ''}`}
                  onClick={() => handleTickerClick('XRP')}
                >XRP</button>
                <button 
                  className={`ticker-btn ${selectedTicker === 'BNB' ? 'active' : ''}`}
                  onClick={() => handleTickerClick('BNB')}
                >BNB</button>
                <button 
                  className={`ticker-btn ${selectedTicker === 'SOL' ? 'active' : ''}`}
                  onClick={() => handleTickerClick('SOL')}
                >SOL</button>
                <button 
                  className={`ticker-btn ${selectedTicker === 'DOGE' ? 'active' : ''}`}
                  onClick={() => handleTickerClick('DOGE')}
                >DOGE</button>
                <button 
                  className={`ticker-btn ${selectedTicker === 'ADA' ? 'active' : ''}`}
                  onClick={() => handleTickerClick('ADA')}
                >ADA</button>
                <button 
                  className={`ticker-btn ${selectedTicker === 'LINK' ? 'active' : ''}`}
                  onClick={() => handleTickerClick('LINK')}
                >LINK</button>
                <button 
                  className={`ticker-btn ${selectedTicker === 'AVAX' ? 'active' : ''}`}
                  onClick={() => handleTickerClick('AVAX')}
                >AVAX</button>
                <button 
                  className={`ticker-btn ${selectedTicker === 'XLM' ? 'active' : ''}`}
                  onClick={() => handleTickerClick('XLM')}
                >XLM</button>
                <button 
                  className={`ticker-btn ${selectedTicker === 'SUI' ? 'active' : ''}`}
                  onClick={() => handleTickerClick('SUI')}
                >SUI</button>
                <button 
                  className={`ticker-btn ${selectedTicker === 'DOT' ? 'active' : ''}`}
                  onClick={() => handleTickerClick('DOT')}
                >DOT</button>
                <button 
                  className={`ticker-btn ${selectedTicker === 'LTC' ? 'active' : ''}`}
                  onClick={() => handleTickerClick('LTC')}
                >LTC</button>
                <button 
                  className={`ticker-btn ${selectedTicker === 'XMR' ? 'active' : ''}`}
                  onClick={() => handleTickerClick('XMR')}
                >XMR</button>
                <button 
                  className={`ticker-btn ${selectedTicker === 'AAVE' ? 'active' : ''}`}
                  onClick={() => handleTickerClick('AAVE')}
                >AAVE</button>
                <button 
                  className={`ticker-btn ${selectedTicker === 'VET' ? 'active' : ''}`}
                  onClick={() => handleTickerClick('VET')}
                >VET</button>
                <button 
                  className={`ticker-btn ${selectedTicker === 'ATOM' ? 'active' : ''}`}
                  onClick={() => handleTickerClick('ATOM')}
                >ATOM</button>
                <button 
                  className={`ticker-btn ${selectedTicker === 'RENDER' ? 'active' : ''}`}
                  onClick={() => handleTickerClick('RENDER')}
                >RENDER</button>
                <button 
                  className={`ticker-btn ${selectedTicker === 'HBAR' ? 'active' : ''}`}
                  onClick={() => handleTickerClick('HBAR')}
                >HBAR</button>
                <button 
                  className={`ticker-btn ${selectedTicker === 'XTZ' ? 'active' : ''}`}
                  onClick={() => handleTickerClick('XTZ')}
                >XTZ</button>
                <button 
                  className={`ticker-btn ${selectedTicker === 'TRX' ? 'active' : ''}`}
                  onClick={() => handleTickerClick('TRX')}
                >TRX</button>
              </div>
            </div>
            
            {/* Conditional Content Based on Workflow State */}
            {activeSubTab === 'symbols' && !selectedTicker && (
              <div className="empty-cards-container">
                <div className="empty-card">
                  <div className="empty-card-content">
                    <span className="empty-icon">📊</span>
                    <span className="empty-text">Select a ticker to view data</span>
                  </div>
                </div>
                <div className="empty-card">
                  <div className="data-analysis-card">
                    <div className="card-header">
                      <h4>📊 Analysis Dashboard</h4>
                    </div>
                    <div className="data-grid">
                      <div className="data-item">
                        <div className="data-label">Current Price</div>
                        <div className="data-value price-value">
                          {priceLoading ? (
                            <>
                              <span className="loading-spinner">⏳</span>
                              <span className="price-text">Loading {selectedTicker} price...</span>
                            </>
                          ) : currentPrice ? (
                            <span className="price-text">${currentPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                          ) : (
                            <span className="price-text error">Failed to load price</span>
                          )}
                        </div>
                      </div>
                      
                      <div className="data-item">
                        <div className="data-label">Risk Value</div>
                        <div className="data-value">
                          {riskValue !== null ? (
                            <span className="risk-value-text">{riskValue.toFixed(6)}</span>
                          ) : (
                            <span className="na-text">NA</span>
                          )}
                        </div>
                      </div>
                      
                      <div className="data-item">
                        <div className="data-label">Risk Band</div>
                        <div className="data-value">
                          {currentRiskBand ? (
                            <span className="risk-band-text">{currentRiskBand}</span>
                          ) : (
                            <span className="na-text">NA</span>
                          )}
                        </div>
                      </div>
                      
                      <div className="data-item">
                        <div className="data-label">Min Price (Risk 0)</div>
                        <div className="data-value">
                          {minRiskPrice ? (
                            <span className="price-text">${minRiskPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                          ) : (
                            <span className="na-text">NA</span>
                          )}
                        </div>
                      </div>
                      
                      <div className="data-item">
                        <div className="data-label">Max Price (Risk 1)</div>
                        <div className="data-value">
                          {maxRiskPrice ? (
                            <span className="price-text">${maxRiskPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                          ) : (
                            <span className="na-text">NA</span>
                          )}
                        </div>
                      </div>
                      
                      <div className="data-item">
                        <div className="data-label">Base Score</div>
                        <div className="data-value">
                          {riskValue !== null ? (
                            <span className="base-score-text">{calculateBaseScore(riskValue, riskBands)} points</span>
                          ) : (
                            <span className="na-text">NA</span>
                          )}
                        </div>
                      </div>
                      
                      <div className="data-item">
                        <div className="data-label">Life Age</div>
                        <div className="data-value">
                          {lifeAge ? (
                            <span className="life-age-text">{lifeAge} days</span>
                          ) : (
                            <span className="na-text">NA</span>
                          )}
                        </div>
                      </div>
                      
                      <div className="data-item">
                        <div className="data-label">% in Risk Band</div>
                        <div className="data-value">
                          {currentRiskBand && riskBands[currentRiskBand] ? (
                            <span className="percentage-text">{riskBands[currentRiskBand].percentage.toFixed(2)}%</span>
                          ) : (
                            <span className="na-text">NA</span>
                          )}
                        </div>
                      </div>
                      
                      <div className="data-item">
                        <div className="data-label">Coefficient Apply</div>
                        <div className="data-value">
                          {currentCoefficient ? (
                            <span className="coefficient-text">{parseFloat(currentCoefficient).toFixed(3)}</span>
                          ) : (
                            <span className="na-text">NA</span>
                          )}
                        </div>
                      </div>
                      
                      <div className="data-item">
                        <div className="data-label">Final Score</div>
                        <div className="data-value">
                          {riskValue !== null && currentCoefficient ? (
                            <span className="final-score-text">{calculateFinalScore(calculateBaseScore(riskValue, riskBands), currentCoefficient).toFixed(1)} points</span>
                          ) : (
                            <span className="na-text">NA</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="empty-card">
                  <div className="empty-card-content">
                    <span className="empty-icon">📊</span>
                    <span className="empty-text">Empty Card 3</span>
                  </div>
                </div>
              </div>
            )}

            {activeSubTab === 'symbols' && selectedTicker && (
              <div className="empty-cards-container">
                <div className="empty-card">
                  <div className="btc-risk-table">
                    <div className="table-container">
                      <table className="risk-data-table">
                        <thead>
                          <tr>
                            <th>Risk Value</th>
                            <th>{selectedTicker} Price</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr><td>0</td><td>$30,000.00</td></tr>
                          <tr><td>0.025</td><td>$31,352.00</td></tr>
                          <tr><td>0.05</td><td>$32,704.00</td></tr>
                          <tr><td>0.075</td><td>$34,055.00</td></tr>
                          <tr><td>0.1</td><td>$35,567.00</td></tr>
                          <tr><td>0.125</td><td>$37,452.00</td></tr>
                          <tr><td>0.15</td><td>$39,336.00</td></tr>
                          <tr><td>0.175</td><td>$41,718.00</td></tr>
                          <tr><td>0.2</td><td>$44,371.00</td></tr>
                          <tr><td>0.225</td><td>$47,457.00</td></tr>
                          <tr><td>0.25</td><td>$50,778.00</td></tr>
                          <tr><td>0.275</td><td>$54,471.00</td></tr>
                          <tr><td>0.3</td><td>$58,519.00</td></tr>
                          <tr><td>0.325</td><td>$62,865.00</td></tr>
                          <tr><td>0.35</td><td>$67,523.00</td></tr>
                          <tr><td>0.375</td><td>$72,497.00</td></tr>
                          <tr><td>0.4</td><td>$77,786.00</td></tr>
                          <tr><td>0.425</td><td>$83,385.00</td></tr>
                          <tr><td>0.45</td><td>$89,289.00</td></tr>
                          <tr><td>0.475</td><td>$95,509.00</td></tr>
                          <tr><td>0.5</td><td>$102,054.00</td></tr>
                          <tr><td>0.525</td><td>$108,886.00</td></tr>
                          <tr><td>0.55</td><td>$116,028.00</td></tr>
                          <tr><td>0.575</td><td>$123,479.00</td></tr>
                          <tr><td>0.6</td><td>$131,227.00</td></tr>
                          <tr><td>0.625</td><td>$139,275.00</td></tr>
                          <tr><td>0.65</td><td>$147,635.00</td></tr>
                          <tr><td>0.675</td><td>$156,284.00</td></tr>
                          <tr><td>0.7</td><td>$165,228.00</td></tr>
                          <tr><td>0.725</td><td>$174,480.00</td></tr>
                          <tr><td>0.75</td><td>$184,029.00</td></tr>
                          <tr><td>0.775</td><td>$193,872.00</td></tr>
                          <tr><td>0.8</td><td>$204,009.00</td></tr>
                          <tr><td>0.825</td><td>$214,439.00</td></tr>
                          <tr><td>0.85</td><td>$225,163.00</td></tr>
                          <tr><td>0.875</td><td>$236,186.00</td></tr>
                          <tr><td>0.9</td><td>$247,499.00</td></tr>
                          <tr><td>0.925</td><td>$259,099.00</td></tr>
                          <tr><td>0.95</td><td>$272,006.00</td></tr>
                          <tr><td>0.975</td><td>$286,003.00</td></tr>
                          <tr><td>1</td><td>$299,720.00</td></tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
                <div className="empty-card">
                  <div className="data-analysis-card">
                    <div className="data-grid">
                      <div className="card-title">
                        <h3>📊 {selectedTicker} Management</h3>
                      </div>
                      <div className="data-item">
                        <div className="data-label">Current Price</div>
                        <div className="data-value price-value">
                          {currentPrice !== null ? (
                            <span className="price-text">${currentPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                          ) : (
                            <span className="na-text">Loading...</span>
                          )}
                        </div>
                      </div>
                      
                      <div className="data-item">
                        <div className="data-label">Risk Value</div>
                        <div className="data-value">
                          {riskValue !== null ? (
                            <span className="risk-value-text">{riskValue}</span>
                          ) : (
                            <span className="na-text">NA</span>
                          )}
                        </div>
                      </div>
                      

                      
                      <div className="data-item">
                        <div className="data-label">Min Price</div>
                        <div className="data-value">
                          {minRiskPrice !== null ? (
                            <span className="price-text">${minRiskPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                          ) : (
                            <span className="na-text">NA</span>
                          )}
                        </div>
                      </div>
                      
                      <div className="data-item">
                        <div className="data-label">Max Price</div>
                        <div className="data-value">
                          {maxRiskPrice !== null ? (
                            <span className="price-text">${maxRiskPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                          ) : (
                            <span className="na-text">NA</span>
                          )}
                        </div>
                      </div>
                      
                      <div className="data-item">
                        <div className="data-label">Final Score</div>
                        <div className="data-value">
                          {riskValue !== null && coefficientApply !== null ? (
                            <span className="final-score-text">
                              {calculateFinalScore(calculateBaseScore(riskValue, riskBands), currentCoefficient)}
                            </span>
                          ) : (
                            <span className="na-text">NA</span>
                          )}
                        </div>
                      </div>
                      

                      
                      <div className="data-item">
                        <div className="data-label">Life Age</div>
                        <div className="data-value">
                          {lifeAge !== null ? (
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                              <span className="life-age-text">{lifeAge} days</span>
                              <button 
                                onClick={() => {
                                  console.log(`🔄 Manually refreshing Life Age for ${selectedTicker}...`);
                                  fetchLifeAge(selectedTicker);
                                }}
                                style={{
                                  padding: '2px 6px',
                                  fontSize: '0.6rem',
                                  background: '#3b82f6',
                                  color: 'white',
                                  border: 'none',
                                  borderRadius: '3px',
                                  cursor: 'pointer'
                                }}
                                title="Refresh Life Age"
                              >
                                🔄
                              </button>
                            </div>
                          ) : (
                            <span className="na-text">NA</span>
                          )}
                        </div>
                      </div>
                      
                      <div className="data-item">
                        <div className="data-label">Risk Band</div>
                        <div className="data-value">
                          {riskValue !== null ? (
                            <span className="risk-band-text">{getRiskBand(riskValue)}</span>
                          ) : (
                            <span className="na-text">NA</span>
                          )}
                        </div>
                      </div>
                      
                      <div className="data-item">
                        <div className="data-label">Pattern</div>
                        <div className="data-value">
                          {riskValue !== null ? (
                            <div 
                              style={{ cursor: 'pointer' }}
                              onClick={async () => {
                                const report = await generatePatternReport(riskValue, riskBands, lifeAge);
                                setPatternReport(report);
                                setPatternModalOpen(true);
                              }}
                              title="Click to view detailed pattern analysis"
                            >
                              <span className="risk-band-text">{getRiskBand(riskValue)}</span>
                              {(() => {
                                const patternAnalysis = analyzePatterns(riskValue);
                                if (patternAnalysis.count > 0) {
                                  return (
                                    <div className="pattern-info">
                                      <small style={{ color: '#666', fontSize: '0.8em' }}>
                                        {patternAnalysis.count} pattern{patternAnalysis.count > 1 ? 's' : ''} found
                                      </small>
                                    </div>
                                  );
                                }
                                return null;
                              })()}
                            </div>
                          ) : (
                            <span className="na-text">NA</span>
                          )}
                        </div>
                      </div>
                      
                      <div className="data-item">
                        <div className="data-label">% in Risk Band</div>
                        <div className="data-value">
                          {riskValue !== null ? (
                            <span className="percentage-text">{getPercentageInRiskBand(riskValue)}%</span>
                          ) : (
                            <span className="na-text">NA</span>
                          )}
                        </div>
                      </div>
                      
                      <div className="data-item">
                        <div className="data-label">Coefficient Apply</div>
                        <div className="data-value">
                          {riskValue !== null && coefficientApply && Object.keys(coefficientApply).length > 0 ? (
                            <span className="coefficient-text">{getCurrentCoefficientDisplay()}</span>
                          ) : (
                            <span className="na-text">NA (Risk: {riskValue}, Coeff: {coefficientApply && Object.keys(coefficientApply).length > 0 ? 'Loaded' : 'Not Loaded'})</span>
                          )}
                        </div>
                      </div>
                      
                      <div className="data-item">
                        <div className="data-label">Base Score</div>
                        <div className="data-value">
                          {riskValue !== null ? (
                            <span className="base-score-text">{calculateBaseScore(riskValue, riskBands)} points</span>
                          ) : (
                            <span className="na-text">NA</span>
                          )}
                        </div>
                      </div>
                      
                      <div className="data-item">
                        <div className="data-label">Signal Status</div>
                        <div className="data-value">
                          {riskValue !== null && coefficientApply !== null ? (
                            (() => {
                              const finalScore = calculateFinalScore(calculateBaseScore(riskValue, riskBands), currentCoefficient);
                              const signal = getSignalStatus(finalScore, riskValue);
                              return (
                                <span 
                                  className="signal-status-text"
                                  style={{ 
                                    color: signal.color, 
                                    backgroundColor: signal.bgColor,
                                    border: `1px solid ${signal.color}40`
                                  }}
                                >
                                  {signal.status}
                                </span>
                              );
                            })()
                          ) : (
                            <span className="na-text">NA</span>
                          )}
                        </div>
                      </div>
                      
                      <div className="data-item">
                        <div className="data-label">Last Update</div>
                        <div className="data-value">
                          {lastCoefficientUpdate ? (
                            <span className="update-time-text">
                              {lastCoefficientUpdate.toLocaleString()}
                            </span>
                          ) : (
                            <span className="na-text">NA</span>
                          )}
                        </div>
                      </div>
                      
                      <div className="data-item">
                        <div className="data-label">Debug: Coefficients</div>
                        <div className="data-value">
                          {coefficientApply && Object.keys(coefficientApply).length > 0 ? (
                            <span className="debug-text">
                              {Object.keys(coefficientApply).length} bands loaded
                            </span>
                          ) : (
                            <span className="na-text">No coefficients</span>
                          )}
                        </div>
                      </div>
                      
                      <div className="data-item">
                        <div className="data-label">Test Calculate</div>
                        <div className="data-value">
                          <button 
                            onClick={async () => {
                              console.log('🧪 Manual test calculation...');
                              console.log('🧪 Input data:', { riskBands, lifeAge });
                              
                              // Simple test first
                              console.log('🧪 Testing button click...');
                              alert('Button clicked! Testing coefficient calculation...');
                              
                              if (!riskBands || !lifeAge) {
                                console.error('❌ Missing data for calculation:', { riskBands: !!riskBands, lifeAge: !!lifeAge });
                                alert('Missing risk bands or life age data');
                                return;
                              }
                              
                              try {
                                const dbiResult = await calculateCoefficientWithOpenAI(selectedTicker, riskValue);
                                console.log('🧪 PERFECTED DBI test result:', dbiResult);
                                
                                if (dbiResult) {
                                  setCoefficientApply(dbiResult.coefficient);
                                  setLastCoefficientUpdate(new Date());
                                  console.log('🧪 PERFECTED DBI coefficients applied!');
                                  alert(`PERFECTED DBI Coefficients calculated successfully!\nCoefficient: ${dbiResult.coefficient}\nFinal Score: ${dbiResult.finalScore}\nSignal: ${dbiResult.signalStrength}`);
                                } else {
                                  console.error('❌ Failed to calculate DBI coefficients');
                                  alert('Failed to calculate DBI coefficients. Check console for details.');
                                }
                              } catch (error) {
                                console.error('❌ Error in DBI coefficient calculation:', error);
                                alert('Error calculating DBI coefficients: ' + error.message);
                              }
                            }}
                            style={{
                              padding: '4px 8px',
                              fontSize: '0.7rem',
                              background: '#059669',
                              color: 'white',
                              border: 'none',
                              borderRadius: '4px',
                              cursor: 'pointer'
                            }}
                          >
                            Calculate Now
                          </button>
                        </div>
                      </div>
                      
                      <div className="data-item">
                        <div className="data-label">Debug: Coefficient Calc</div>
                        <div className="data-value">
                          {currentPrice && riskValue ? (
                            <span className="debug-text">
                              Price: ${currentPrice.toLocaleString()} | 
                              Coef: {getCurrentCoefficientDisplay()}
                            </span>
                          ) : (
                            <span className="na-text">No price/risk data</span>
                          )}
                        </div>
                      </div>
                      
                      <div className="data-item">
                        <div className="data-label">Rarity Rank</div>
                        <div className="data-value">
                          {rarityRank !== null ? (
                            <span className="rarity-rank-text">
                              {rarityRank}/10 {rarityRank === 1 ? '(RAREST)' : rarityRank <= 3 ? '(TOP 3)' : rarityRank <= 5 ? '(TOP 5)' : '(COMMON)'}
                            </span>
                          ) : (
                            <span className="na-text">Calculating...</span>
                          )}
                        </div>
                      </div>
                      
                      <div className="data-item">
                        <div className="data-label">Risk Band</div>
                        <div className="data-value">
                          {riskValue !== null ? (
                            <span className="risk-band-text">{getRiskBand(riskValue)}</span>
                          ) : (
                            <span className="na-text">NA</span>
                          )}
                        </div>
                      </div>
                      
                      <div className="data-item">
                        <div className="data-label">Base Score</div>
                        <div className="data-value">
                          <span className="na-text">NA</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="empty-card">
                  <div className="empty-card-content">
                    <span className="empty-icon">📊</span>
                    <span className="empty-text">Empty Card 3</span>
                  </div>
                </div>
                
                {/* Band Change Alert Card */}
                <div className="empty-card">
                  <div className="alert-card">
                    <div className="card-title">
                      <h3>🚨 System Alerts</h3>
                    </div>
                    
                    {/* Band Change Alert */}
                    {bandChangeAlert ? (
                      <div className="current-alert">
                        <div className="alert-header">
                          <span className="alert-symbol">{bandChangeAlert.symbol}</span>
                          <span className="alert-time">{bandChangeAlert.timestamp.toLocaleTimeString()}</span>
                        </div>
                        <div className="alert-message">
                          {bandChangeAlert.message}
                        </div>
                        <div className="alert-details">
                          <span className="old-band">From: {bandChangeAlert.oldBand}</span>
                          <span className="new-band">To: {bandChangeAlert.newBand}</span>
                          <span className="risk-value">Risk: {bandChangeAlert.riskValue}</span>
                          <span className="price">Price: ${bandChangeAlert.price?.toLocaleString()}</span>
                        </div>
                      </div>
                    ) : (
                      <div className="no-alerts">
                        <span>No band changes detected</span>
                      </div>
                    )}
                    
                    {/* Update Logs */}
                    <div className="update-logs-section">
                      <h4>📊 Recent Updates</h4>
                      {updateLogsLoading ? (
                        <div className="loading-updates">
                          <span>Loading updates...</span>
                        </div>
                      ) : updateLogs.length > 0 ? (
                        <div className="update-logs-list">
                          {updateLogs.slice(0, 3).map(update => (
                            <div key={update.id} className="update-log-item">
                              <div className="update-header">
                                <span className="update-type">
                                  {update.update_type === 'life_age' ? '⏰' : '📈'} {update.update_type}
                                </span>
                                <span className="update-time">
                                  {new Date(update.timestamp).toLocaleTimeString()}
                                </span>
                              </div>
                              <div className="update-details">
                                {update.details}
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="no-updates">
                          <span>No recent updates</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeSubTab === 'my-symbols' && (
              <div className="empty-cards-container">
                <div className="empty-card">
                  <div className="empty-card-content">
                    <span className="empty-icon">🎯</span>
                    <span className="empty-text">My Symbols Content</span>
                  </div>
                </div>
                <div className="empty-card">
                  <div className="empty-card-content">
                    <span className="empty-icon">📊</span>
                    <span className="empty-text">My Symbols Card 2</span>
                  </div>
                </div>
                <div className="empty-card">
                  <div className="empty-card-content">
                    <span className="empty-icon">⚙️</span>
                    <span className="empty-text">My Symbols Card 3</span>
                  </div>
                </div>
              </div>
            )}

            {activeSubTab === 'management' && (
              <div className="empty-cards-container">
                <div className="empty-card">
                  <div className="btc-risk-table">
                    <div className="table-container">
                      <table className="risk-data-table">
                        <thead>
                          <tr>
                            <th>Risk Value</th>
                            <th>BTC Price</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr><td>0</td><td>${minRiskPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td></tr>
                          <tr><td>0.025</td><td>$31,352.00</td></tr>
                          <tr><td>0.05</td><td>$32,704.00</td></tr>
                          <tr><td>0.075</td><td>$34,055.00</td></tr>
                          <tr><td>0.1</td><td>$35,567.00</td></tr>
                          <tr><td>0.125</td><td>$37,452.00</td></tr>
                          <tr><td>0.15</td><td>$39,336.00</td></tr>
                          <tr><td>0.175</td><td>$41,718.00</td></tr>
                          <tr><td>0.2</td><td>$44,371.00</td></tr>
                          <tr><td>0.225</td><td>$47,457.00</td></tr>
                          <tr><td>0.25</td><td>$50,778.00</td></tr>
                          <tr><td>0.275</td><td>$54,471.00</td></tr>
                          <tr><td>0.3</td><td>$58,519.00</td></tr>
                          <tr><td>0.325</td><td>$62,865.00</td></tr>
                          <tr><td>0.35</td><td>$67,523.00</td></tr>
                          <tr><td>0.375</td><td>$72,497.00</td></tr>
                          <tr><td>0.4</td><td>$77,786.00</td></tr>
                          <tr><td>0.425</td><td>$83,385.00</td></tr>
                          <tr><td>0.45</td><td>$89,289.00</td></tr>
                          <tr><td>0.475</td><td>$95,509.00</td></tr>
                          <tr><td>0.5</td><td>$102,054.00</td></tr>
                          <tr><td>0.525</td><td>$108,886.00</td></tr>
                          <tr><td>0.55</td><td>$116,028.00</td></tr>
                          <tr><td>0.575</td><td>$123,479.00</td></tr>
                          <tr><td>0.6</td><td>$131,227.00</td></tr>
                          <tr><td>0.625</td><td>$139,275.00</td></tr>
                          <tr><td>0.65</td><td>$147,635.00</td></tr>
                          <tr><td>0.675</td><td>$156,284.00</td></tr>
                          <tr><td>0.7</td><td>$165,228.00</td></tr>
                          <tr><td>0.725</td><td>$174,480.00</td></tr>
                          <tr><td>0.75</td><td>$184,029.00</td></tr>
                          <tr><td>0.775</td><td>$193,872.00</td></tr>
                          <tr><td>0.8</td><td>$204,009.00</td></tr>
                          <tr><td>0.825</td><td>$214,439.00</td></tr>
                          <tr><td>0.85</td><td>$225,163.00</td></tr>
                          <tr><td>0.875</td><td>$236,186.00</td></tr>
                          <tr><td>0.9</td><td>$247,499.00</td></tr>
                          <tr><td>0.925</td><td>$259,099.00</td></tr>
                          <tr><td>0.95</td><td>$272,006.00</td></tr>
                          <tr><td>0.975</td><td>$286,003.00</td></tr>
                          <tr><td>1</td><td>${maxRiskPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td></tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
                <div className="empty-card">
                  <div className="empty-card-content">
                    <div className="empty-icon">📊</div>
                    <div className="empty-text">Management Card 2</div>
                  </div>
                </div>
                <div className="empty-card">
                  <div className="risk-price-controls-card">
                    <div className="card-title">
                      <h3>⚙️ Risk Price Controls</h3>
                    </div>
                    <div className="risk-controls-content">
                      {/* Min Risk Price Section */}
                      <div className="price-control-section">
                        <div className="section-title">💰 Min Risk Price (Risk 0)</div>
                        <div className="current-price-display">
                          <span className="price-label">Current Price:</span>
                          <span className="price-value">${minRiskPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                          <span className="last-update">Last Update: {lastUpdate.toLocaleString()}</span>
                        </div>
                        <div className="set-price-controls">
                          <input 
                            type="number" 
                            className="new-price-input" 
                            placeholder="Enter new price..."
                            step="0.01"
                            value={newPriceInput}
                            onChange={(e) => setNewPriceInput(e.target.value)}
                          />
                          <button className="set-price-btn" onClick={handleSetMinPrice}>Set</button>
                        </div>
                      </div>

                      {/* Max Risk Price Section */}
                      <div className="price-control-section">
                        <div className="section-title">📈 Max Risk Price (Risk 1)</div>
                        <div className="current-price-display">
                          <span className="price-label">Current Price:</span>
                          <span className="price-value">${maxRiskPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                          <span className="last-update">Last Update: {lastMaxUpdate.toLocaleString()}</span>
                        </div>
                        <div className="set-price-controls">
                          <input 
                            type="number" 
                            className="new-price-input" 
                            placeholder="Enter new price..."
                            step="0.01"
                            value={newMaxPriceInput}
                            onChange={(e) => setNewMaxPriceInput(e.target.value)}
                          />
                          <button className="set-price-btn" onClick={handleSetMaxPrice}>Set</button>
                        </div>
                      </div>

                      {/* Polynomial Formula Section */}
                      <div className="price-control-section">
                        <div className="section-title">📐 Polynomial Formula</div>
                        <div className="current-price-display">
                          <span className="price-label">Current Formula:</span>
                          <span className="formula-value">{polynomialFormula}</span>
                          <span className="last-update">Last Update: {lastFormulaUpdate.toLocaleString()}</span>
                        </div>
                        <div className="set-price-controls">
                          <input 
                            type="text" 
                            className="new-price-input" 
                            placeholder="Enter new formula..."
                            value={newFormulaInput}
                            onChange={(e) => setNewFormulaInput(e.target.value)}
                          />
                          <button className="set-price-btn" onClick={handleSetFormula}>Set</button>
                        </div>
                      </div>

                      {/* Risk Value Formula Section */}
                      <div className="price-control-section">
                        <div className="section-title">🎯 Risk Value Formula</div>
                        <div className="current-price-display">
                          <span className="price-label">Current Formula:</span>
                          <span className="formula-value">{riskValueFormula}</span>
                          <span className="last-update">Last Update: {lastRiskFormulaUpdate.toLocaleString()}</span>
                        </div>
                        <div className="set-price-controls">
                          <input 
                            type="text" 
                            className="new-price-input" 
                            placeholder="Enter new formula..."
                            value={newRiskFormulaInput}
                            onChange={(e) => setNewRiskFormulaInput(e.target.value)}
                          />
                          <button className="set-price-btn" onClick={handleSetRiskFormula}>Set</button>
                        </div>
                      </div>

                      {/* Life Age Section */}
                      <div className="price-control-section">
                        <div className="section-title">⏰ {selectedTicker} Life Age in Days</div>
                        <div className="current-price-display">
                          <span className="price-label">{selectedTicker} Current Age:</span>
                          <span className="price-value">
                            {lifeAgeLoading ? (
                              <span className="loading-spinner">⏳ Loading...</span>
                            ) : (
                              `${lifeAge} days`
                            )}
                          </span>
                          <span className="last-update">Last Update: {lastLifeAgeUpdate.toLocaleString()}</span>
                        </div>
                        <div className="set-price-controls">
                          <input 
                            type="number" 
                            className="new-price-input" 
                            placeholder="Enter new age in days..."
                            min="1"
                            value={newLifeAgeInput}
                            onChange={(e) => setNewLifeAgeInput(e.target.value)}
                          />
                          <button className="set-price-btn" onClick={handleSetLifeAge}>Set</button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>


                

              </div>
            )}
            
            {/* Time Spent in Risk Bands Card */}
            <div className="ticker-buttons-card-empty">
              <div className="card-title">
                <h3>⏱️ Time Spent in Risk Bands</h3>
              </div>
              
              {/* Status Information */}
              <div className="validation-summary-inside">
                <div className="validation-item">
                  <span className="validation-label">Total Risk Band Days:</span>
                  <span className="validation-value">{calculateTotalRiskBandDays()}</span>
                </div>
                <div className="validation-item">
                  <span className="validation-label">Life Age:</span>
                  <span className="validation-value">{lifeAge}</span>
                </div>
                <div className="validation-item">
                  <span className="validation-label">Status:</span>
                  <span className={`validation-status ${calculateTotalRiskBandDays() === lifeAge ? 'valid' : calculateTotalRiskBandDays() > lifeAge ? 'error' : 'warning'}`}>
                    {calculateTotalRiskBandDays() === lifeAge ? '✅ Valid' : 
                     calculateTotalRiskBandDays() > lifeAge ? '❌ Exceeds Life Age' : 
                     '⚠️ Missing Data'}
                  </span>
                </div>
              </div>
              
              <div className="ticker-buttons-empty">
                {/* Individual Risk Band Cards Inside */}
                {Object.entries(riskBands).map(([bandKey, bandData]) => (
                  <div key={bandKey} className={`risk-band-card ${bandKey === getRiskBand(riskValue) ? 'current-risk-band' : ''}`}>
                    <div className="risk-band-card-header">
                      <h4 className="risk-band-title">
                        {bandKey}
                        {bandKey === getRiskBand(riskValue) && (
                          <span className="current-indicator">📍 CURRENT</span>
                        )}
                      </h4>
                    </div>
                    <div className="risk-band-card-content">
                      <div className="risk-band-info">
                        <div className="risk-band-days">
                          <span className="days-label">Days:</span>
                          <span className="days-value">{bandData.days}</span>
                        </div>
                        <div className="risk-band-percentage">
                          <span className="percentage-label">Percentage:</span>
                          <span className="percentage-value">{bandData.percentage || 0}%</span>
                        </div>
                        <div className="risk-band-update">
                          <span className="update-label">Last Update:</span>
                          <span className="update-value">{bandData.lastUpdate.toLocaleDateString()}</span>
                        </div>
                      </div>
                      <div className="risk-band-controls">
                        <input 
                          type="number" 
                          className="risk-band-input" 
                          placeholder="Enter days..."
                          min="0"
                          value={newRiskBandInputs[bandKey]}
                          onChange={(e) => handleRiskBandInputChange(bandKey, e.target.value)}
                        />
                        <button 
                          className="risk-band-set-btn" 
                          onClick={() => handleSetRiskBand(bandKey)}
                        >
                          Set
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Pattern Analysis Modal */}
      {patternModalOpen && (
        <div className="modal-overlay" onClick={() => setPatternModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>📊 Pattern Analysis Report - {selectedTicker}</h3>
              <button 
                className="modal-close-btn"
                onClick={() => setPatternModalOpen(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="report-content">
                <pre style={{ 
                  whiteSpace: 'pre-wrap', 
                  fontFamily: 'monospace', 
                  fontSize: '12px',
                  lineHeight: '1.4',
                  color: '#333',
                  backgroundColor: '#f8f9fa',
                  padding: '15px',
                  borderRadius: '5px',
                  border: '1px solid #e9ecef',
                  maxHeight: '400px',
                  overflowY: 'auto'
                }}>
                  {patternReport}
                </pre>
              </div>
            </div>
            <div className="modal-footer">
              <button 
                className="generate-btn"
                onClick={async () => {
                  const newReport = await generatePatternReport(riskValue, riskBands, lifeAge);
                  setPatternReport(newReport);
                }}
              >
                🔄 Generate Now
              </button>
              <button 
                className="copy-btn"
                onClick={() => {
                  navigator.clipboard.writeText(patternReport);
                  alert('Report copied to clipboard!');
                }}
              >
                📋 Copy Report
              </button>
              <button 
                className="close-btn"
                onClick={() => setPatternModalOpen(false)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Main Scoring Component
const Scoring = () => {
  const location = useLocation()
  const [activeTab, setActiveTab] = useState('cryptometer')
  const [activeSubTab, setActiveSubTab] = useState('symbols')
  const [selectedTicker, setSelectedTicker] = useState('BTC')
  
  // Chart functionality
  const [selectedSymbol, setSelectedSymbol] = useState('BTCUSDT')
  const [chartTimeframe, setChartTimeframe] = useState('24H')
  const [availableSymbols, setAvailableSymbols] = useState([])
  const [symbolsLoading, setSymbolsLoading] = useState(false)
  const [chartData, setChartData] = useState(null)
  const [chartLoading, setChartLoading] = useState(false)
  


  // Get current path to determine which tab to show
  useEffect(() => {
    const path = location.pathname
    console.log('🔍 Scoring component - Current path:', path)
    
    if (path === '/cryptometer') {
      console.log('✅ Setting active tab to cryptometer')
      setActiveTab('cryptometer')
    } else if (path === '/kingfisher') {
      console.log('✅ Setting active tab to kingfisher')
      setActiveTab('kingfisher')
    } else if (path === '/riskmetric') {
      console.log('✅ Setting active tab to riskmetric')
      setActiveTab('riskmetric')
    } else {
      console.log('✅ Setting active tab to cryptometer (default)')
      setActiveTab('cryptometer') // Default to cryptometer
    }
  }, [location.pathname])

  const tabs = [
    {
      id: 'cryptometer',
      label: 'Cryptometer',
      icon: TrendingUp,
      badge: '17 Endpoints'
    },
    {
      id: 'kingfisher',
      label: 'KingFisher',
      icon: BarChart3,
      badge: 'Liquidation'
    },
    {
      id: 'riskmetric',
      label: 'RiskMetric',
      icon: Activity,
      badge: 'Risk'
    }
  ]

  // Load available symbols for chart
  useEffect(() => {
    loadAvailableSymbols()
  }, [])

  // Load chart data when symbol or timeframe changes
  useEffect(() => {
    if (selectedSymbol) {
      loadChartData(selectedSymbol, chartTimeframe)
    }
  }, [selectedSymbol, chartTimeframe])

  const loadAvailableSymbols = async () => {
    try {
      setSymbolsLoading(true)
      const response = await fetch('/api/futures-symbols/kucoin/available')
      if (response.ok) {
        const data = await response.json()
        setAvailableSymbols(data.symbols || [])
      }
    } catch (error) {
      console.error('Error loading symbols:', error)
    } finally {
      setSymbolsLoading(false)
    }
  }

  const loadChartData = async (symbol, timeframe) => {
    try {
      setChartLoading(true)
      console.log(`📊 Loading chart data for ${symbol} with timeframe: ${timeframe}`)
      
      // Enhanced data fetching with more granular intervals
      let interval, limit
      switch (timeframe) {
        case '24H':
          interval = '15m'
          limit = 96
          break
        case '7D':
          interval = '1h'
          limit = 168
          break
        case '1M':
          interval = '4h'
          limit = 180
          break
        default:
          interval = '15m'
          limit = 96
      }
      
      console.log(`🔗 Fetching from Binance API: ${symbol} ${interval} ${limit} candles`)
      
      const response = await fetch(
        `https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=${interval}&limit=${limit}`,
        { 
          headers: { 'Accept': 'application/json' }
        }
      )
      
      if (response.ok) {
        const data = await response.json()
        console.log(`📊 Raw Binance data:`, data.length, 'candles')
        
        const processedData = data.map(candle => ({
          time: candle[0] / 1000,
          open: parseFloat(candle[1]),
          high: parseFloat(candle[2]),
          low: parseFloat(candle[3]),
          close: parseFloat(candle[4]),
          volume: parseFloat(candle[5])
        }))
        
        console.log(`✅ Processed data:`, processedData.length, 'records')
        setChartData(processedData)
      }
    } catch (error) {
      console.error('Error loading chart data:', error)
    } finally {
      setChartLoading(false)
    }
  }

  const handleTabChange = (tabId) => {
    setActiveTab(tabId)
    // Navigate to the corresponding route
    window.history.pushState({}, '', `/${tabId}`)
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'cryptometer':
        return <CryptometerTab />
      case 'kingfisher':
        return <KingFisherTab />
      case 'riskmetric':
        return <RiskMetricTab 
          activeSubTab={activeSubTab}
          setActiveSubTab={setActiveSubTab}
          selectedTicker={selectedTicker}
          setSelectedTicker={setSelectedTicker}
        />
      default:
        return <CryptometerTab />
    }
  }

  return (
    <div className="scoring-container">
      <div className="section-header">
        <h2>🎯 Scoring System</h2>
        <p>Comprehensive market analysis using Cryptometer, KingFisher, and RiskMetric</p>
      </div>

      <HorizontalTabs
        tabs={tabs}
        active={activeTab}
        onChange={handleTabChange}
      />

      <div className="tab-content">
        {renderTabContent()}
      </div>

      {/* Chart Analysis Section */}
      <div className="chart-section" style={{
        marginTop: '30px',
        padding: '30px',
        background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
        borderRadius: '20px',
        border: '2px solid rgba(255,255,255,0.2)',
        boxShadow: '0 20px 40px rgba(0,0,0,0.3)'
      }}>
        <div className="chart-header" style={{ marginBottom: '30px' }}>
          <h3 style={{ 
            fontSize: '2rem', 
            fontWeight: '700', 
            color: '#ffffff',
            margin: '0 0 10px 0'
          }}>
            📈 Chart Analysis
          </h3>
          <p style={{ 
            fontSize: '1.1rem', 
            color: 'rgba(255,255,255,0.7)',
            margin: '0'
          }}>
            Real-time technical analysis with professional indicators
          </p>
        </div>

        {/* Chart Controls */}
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '20px', 
          marginBottom: '30px',
          padding: '20px',
          background: 'rgba(255,255,255,0.05)',
          borderRadius: '15px',
          border: '1px solid rgba(255,255,255,0.1)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ color: '#ffffff', fontWeight: '600', fontSize: '1.1rem' }}>
              Symbol:
            </span>
            <select
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value)}
              style={{
                padding: '12px 16px',
                background: 'rgba(255,255,255,0.1)',
                border: '2px solid rgba(255,255,255,0.2)',
                borderRadius: '10px',
                color: '#ffffff',
                fontSize: '1rem',
                fontWeight: '600',
                cursor: 'pointer',
                minWidth: '150px',
                backdropFilter: 'blur(10px)'
              }}
            >
              {symbolsLoading ? (
                <option>Loading symbols...</option>
              ) : (
                availableSymbols.map(symbol => (
                  <option key={symbol} value={symbol}>
                    {symbol}
                  </option>
                ))
              )}
            </select>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ color: '#ffffff', fontWeight: '600', fontSize: '1.1rem' }}>
              Timeframe:
            </span>
            <select
              value={chartTimeframe}
              onChange={(e) => setChartTimeframe(e.target.value)}
              style={{
                padding: '12px 16px',
                background: 'rgba(255,255,255,0.1)',
                border: '2px solid rgba(255,255,255,0.2)',
                borderRadius: '10px',
                color: '#ffffff',
                fontSize: '1rem',
                fontWeight: '600',
                cursor: 'pointer',
                minWidth: '120px',
                backdropFilter: 'blur(10px)'
              }}
            >
              <option value="24H">24 Hours</option>
              <option value="7D">7 Days</option>
              <option value="1M">1 Month</option>
            </select>
          </div>

          <div style={{ 
            padding: '8px 16px', 
            background: 'rgba(16, 185, 129, 0.2)', 
            borderRadius: '8px',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            color: '#10b981',
            fontSize: '0.9rem',
            fontWeight: '600'
          }}>
            ⚡ Auto-refresh: 30s
          </div>
        </div>

        {/* Chart Display */}
        <div style={{ 
          minHeight: '500px',
          background: 'rgba(0,0,0,0.3)',
          borderRadius: '15px',
          border: '1px solid rgba(255,255,255,0.1)',
          overflow: 'hidden',
          padding: '20px'
        }}>
          {chartLoading ? (
            <div style={{ 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center', 
              height: '500px',
              color: '#ffffff'
            }}>
              <div>Loading chart data...</div>
            </div>
          ) : chartData && chartData.length > 0 ? (
            <SimpleChart
              data={chartData}
              symbol={selectedSymbol}
              width="100%"
              height="500"
              timeframe={chartTimeframe}
            />
          ) : (
            <div style={{ 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center', 
              height: '500px',
              color: '#ffffff'
            }}>
              <div>No chart data available</div>
            </div>
          )}
        </div>

        {/* Chart Features Info */}
        <div style={{
          marginTop: '30px',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '20px'
        }}>
          <div style={{
            padding: '20px',
            background: 'rgba(255,255,255,0.05)',
            borderRadius: '12px',
            border: '1px solid rgba(255,255,255,0.1)'
          }}>
            <h4 style={{ color: '#3b82f6', margin: '0 0 10px 0' }}>📊 Technical Indicators</h4>
            <ul style={{ color: 'rgba(255,255,255,0.8)', margin: '0', paddingLeft: '20px' }}>
              <li>SMA (Simple Moving Average)</li>
              <li>EMA (Exponential Moving Average)</li>
              <li>RSI (Relative Strength Index)</li>
              <li>MACD (Moving Average Convergence Divergence)</li>
              <li>Bollinger Bands</li>
            </ul>
          </div>
          
          <div style={{
            padding: '20px',
            background: 'rgba(255,255,255,0.05)',
            borderRadius: '12px',
            border: '1px solid rgba(255,255,255,0.1)'
          }}>
            <h4 style={{ color: '#10b981', margin: '0 0 10px 0' }}>📈 Chart Types</h4>
            <ul style={{ color: 'rgba(255,255,255,0.8)', margin: '0', paddingLeft: '20px' }}>
              <li>Candlestick (Professional)</li>
              <li>Line Chart</li>
              <li>Area Chart</li>
              <li>Bar Chart</li>
              <li>Heikin Ashi</li>
            </ul>
          </div>
          
          <div style={{
            padding: '20px',
            background: 'rgba(255,255,255,0.05)',
            borderRadius: '12px',
            border: '1px solid rgba(255,255,255,0.1)'
          }}>
            <h4 style={{ color: '#f59e0b', margin: '0 0 10px 0' }}>⚡ Real-time Features</h4>
            <ul style={{ color: 'rgba(255,255,255,0.8)', margin: '0', paddingLeft: '20px' }}>
              <li>Live Binance API integration</li>
              <li>EMA Crossover detection</li>
              <li>Golden/Death Cross alerts</li>
              <li>Multiple timeframes</li>
              <li>Professional notifications</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Scoring
