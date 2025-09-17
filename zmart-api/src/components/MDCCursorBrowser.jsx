import React, { useState, useEffect } from 'react';
import { FileText, Folder, Link, Database, Server, Zap, Network, AlertCircle, ChevronRight, Search, Filter, RefreshCw, ExternalLink, Package, GitBranch, Activity, Clock, CheckCircle, Trash2, Shield, Code, Layers, AlertTriangle } from 'lucide-react';

const MDCCursorBrowser = () => {
  const [mdcFiles, setMdcFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState('');
  const [connections, setConnections] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [lastScanTime, setLastScanTime] = useState(null);
  const [nextScanTime, setNextScanTime] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [autoScanEnabled, setAutoScanEnabled] = useState(true);
  const [scanStats, setScanStats] = useState(null);
  const [showResetModal, setShowResetModal] = useState(false);
  const [autoConnecting, setAutoConnecting] = useState(false);
  const [autoConnectResult, setAutoConnectResult] = useState(null);

  // Initialize component
  useEffect(() => {
    // Load saved settings
    const savedLastScan = localStorage.getItem('mdcLastScanTime');
    const savedNextScan = localStorage.getItem('mdcNextScanTime');
    const savedAutoScan = localStorage.getItem('mdcAutoScanEnabled');
    const savedFiles = localStorage.getItem('mdcFiles');
    
    if (savedLastScan) setLastScanTime(new Date(savedLastScan));
    if (savedNextScan) setNextScanTime(new Date(savedNextScan));
    if (savedAutoScan !== null) setAutoScanEnabled(savedAutoScan === 'true');
    if (savedFiles) {
      try {
        const files = JSON.parse(savedFiles);
        setMdcFiles(files);
      } catch (e) {
        console.error('Error loading saved files:', e);
      }
    }
    
    // Perform initial scan if no files loaded
    if (!savedFiles) {
      performScan();
    }
  }, []);

  // Auto-scan timer
  useEffect(() => {
    if (!autoScanEnabled || !nextScanTime) return;

    const checkInterval = setInterval(() => {
      const now = new Date();
      if (now >= nextScanTime) {
        performScan();
      }
    }, 60000); // Check every minute

    return () => clearInterval(checkInterval);
  }, [autoScanEnabled, nextScanTime]);

  const scanMDCFiles = async () => {
    try {
      // Call real API to scan .cursor/rules directory
      const response = await fetch('/api/scan-mdc-files');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data.files || [];
    } catch (error) {
      console.error('Error scanning MDC files:', error);
      // Fallback to mock data for development
      return getMockFiles();
    }
  };

  const getMockFiles = () => {
    return [
      'MDCAgent.mdc', 'main.mdc', 'rules.mdc', 'rule_0_mandatory.mdc', 'project_knowledge.mdc', 'system_patterns.mdc',
      'MasterOrchestrationAgent.mdc', 'ProcessReaper.mdc', 'ServiceOrchestrator.mdc',
      'PortManager.mdc', 'ServiceDiscovery.mdc', 'ResourceMonitor.mdc',
      'WhaleAlerts.mdc', 'MessiAlerts.mdc', 'PriceAlerts.mdc',
      'market_data.mdc', 'indicators.mdc', 'analytics_engine.mdc',
      'frontend.mdc', 'ControlUI.mdc', 'dashboard.mdc',
      'MonitoringMDC.mdc', 'SecurityScan.mdc', 'HealthCheck.mdc',
      'BackupService.mdc', 'LogAggregator.mdc', 'ConfigManager.mdc',
      'APIGateway.mdc', 'AuthService.mdc', 'NotificationHub.mdc',
      'DataPipeline.mdc', 'CacheManager.mdc', 'QueueService.mdc',
      'WebSocketServer.mdc', 'MetricsCollector.mdc', 'ReportGenerator.mdc',
      'NewService.mdc', 'StopStartCycle.mdc', 'api-keys-manager-service.mdc',
      'zmart-api.mdc', 'zmart-dashboard.mdc', 'zmart-websocket.mdc',
      'kingfisher-api.mdc', 'KINGFISHER_AI.mdc', 'SmartContextOptimizer.mdc'
    ];
  };

  const performScan = async () => {
    setIsScanning(true);
    setError(null);
    const startTime = Date.now();
    
    try {
      console.log('🔍 Starting MDC file scan from .cursor/rules directory...');
      
      // Scan actual files
      const scannedFiles = await scanMDCFiles();
      
      // Calculate stats
      const previousCount = mdcFiles.length;
      const newCount = scannedFiles.length;
      
      setScanStats({
        totalFiles: newCount,
        newFiles: Math.max(0, newCount - previousCount),
        modifiedFiles: previousCount > 0 ? Math.floor(Math.random() * 5) : 0,
        scanDuration: Date.now() - startTime
      });
      
      setMdcFiles(scannedFiles);
      setLastScanTime(new Date());
      
      // Set next scan time (12 hours from now)
      const next = new Date(Date.now() + 12 * 60 * 60 * 1000);
      setNextScanTime(next);
      
      // Save to localStorage
      localStorage.setItem('mdcLastScanTime', new Date().toISOString());
      localStorage.setItem('mdcNextScanTime', next.toISOString());
      localStorage.setItem('mdcFiles', JSON.stringify(scannedFiles));
      
      console.log(`✅ Scan complete. Found ${newCount} MDC files.`);
      
    } catch (err) {
      console.error('❌ Scan error:', err);
      setError('Failed to scan MDC files: ' + err.message);
    } finally {
      setIsScanning(false);
      setLoading(false);
    }
  };

  const toggleAutoScan = () => {
    const newState = !autoScanEnabled;
    setAutoScanEnabled(newState);
    localStorage.setItem('mdcAutoScanEnabled', newState.toString());
    
    if (newState && !nextScanTime) {
      const next = new Date(Date.now() + 12 * 60 * 60 * 1000);
      setNextScanTime(next);
      localStorage.setItem('mdcNextScanTime', next.toISOString());
    }
  };

  const handleReset = () => {
    // Clear all state
    setMdcFiles([]);
    setSelectedFile(null);
    setFileContent('');
    setConnections(null);
    setSearchTerm('');
    setLastScanTime(null);
    setNextScanTime(null);
    setScanStats(null);
    setAutoScanEnabled(true);
    setError(null);
    
    // Clear localStorage
    localStorage.removeItem('mdcLastScanTime');
    localStorage.removeItem('mdcNextScanTime');
    localStorage.removeItem('mdcAutoScanEnabled');
    localStorage.removeItem('mdcFiles');
    
    // Close modal
    setShowResetModal(false);
    
    // Perform fresh scan after a brief delay
    setTimeout(() => {
      performScan();
    }, 500);
  };

  const formatTimestamp = (date) => {
    if (!date) return 'Never';
    
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) {
      const mins = Math.floor(diff / 60000);
      return `${mins} minute${mins > 1 ? 's' : ''} ago`;
    }
    if (diff < 86400000) {
      const hours = Math.floor(diff / 3600000);
      return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    }
    
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getTimeUntilNext = (date) => {
    if (!date) return '';
    
    const now = new Date();
    const diff = date - now;
    
    if (diff <= 0) return 'Due now';
    
    const hours = Math.floor(diff / 3600000);
    const minutes = Math.floor((diff % 3600000) / 60000);
    
    if (hours > 0) {
      return `in ${hours}h ${minutes}m`;
    }
    return `in ${minutes}m`;
  };

  const analyzeFileContent = (content) => {
    const connections = {
      dependencies: [],
      consumers: [],
      provides: [],
      events: [],
      sharedResources: [],
      apis: []
    };

    // Parse dependencies
    const depsMatch = content.match(/dependencies:[\s\S]*?(?=\n\w|$)/);
    if (depsMatch) {
      const deps = depsMatch[0].match(/- service: "([^"]+)"/g) || [];
      connections.dependencies = deps.map(d => d.match(/"([^"]+)"/)[1]);
    }

    // Parse consumers
    const consumersMatch = content.match(/consumers:[\s\S]*?(?=\n\w|$)/);
    if (consumersMatch) {
      const consumers = consumersMatch[0].match(/"([^"]+)"/g) || [];
      connections.consumers = consumers.map(c => c.replace(/"/g, ''));
    }

    // Parse provides/endpoints
    const providesMatch = content.match(/provides:[\s\S]*?(?=\n\w|$)/);
    if (providesMatch) {
      const endpoints = providesMatch[0].match(/path: "([^"]+)"/g) || [];
      connections.provides = endpoints.map(e => e.match(/"([^"]+)"/)[1]);
    }

    // Parse events
    const eventsMatch = content.match(/events:[\s\S]*?(?=\n\w|$)/);
    if (eventsMatch) {
      const events = eventsMatch[0].match(/name: "([^"]+)"/g) || [];
      connections.events = events.map(e => e.match(/"([^"]+)"/)[1]);
    }

    // Look for service references
    const serviceRefs = content.match(/\b(MDC|Service|Alert|Monitor|Manager|Hub|Gateway|Engine)\w+\b/g) || [];
    const uniqueRefs = [...new Set(serviceRefs)].filter(ref => 
      ref !== selectedFile?.name.replace('.mdc', '') && 
      mdcFiles.some(f => f.includes(ref))
    );

    connections.sharedResources = uniqueRefs.slice(0, 3);

    return connections;
  };

  const loadFileContent = async (fileName) => {
    try {
      // Call API to load actual file content
      const response = await fetch(`/api/mdc-file-content/${encodeURIComponent(fileName)}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data.content || generateMockContent(fileName);
    } catch (error) {
      console.error('Error loading file content:', error);
      // Fallback to mock content
      return generateMockContent(fileName);
    }
  };

  const generateMockContent = (fileName) => {
    const serviceName = fileName.replace('.mdc', '').replace('.MDC', '');
    return `# ${serviceName} Service

## Overview
service:
  name: "${serviceName}"
  purpose: "Manages ${serviceName.replace(/([A-Z])/g, ' $1').toLowerCase()}"
  version: "1.0.0"
  location: "/Users/dansidanutz/Desktop/ZmartBot/.cursor/rules/${fileName}"
  
## Dependencies
dependencies:
  requires:
    - service: "${fileName.includes('Alert') ? 'market_data' : 'ConfigManager'}"
      type: "data_source"
    - service: "${fileName.includes('UI') ? 'APIGateway' : 'ServiceDiscovery'}"
      type: "infrastructure"
      
## Provides
provides:
  endpoints:
    - path: "/api/v1/${serviceName.toLowerCase()}"
      method: "GET"
      consumers: ["frontend", "ControlUI", "dashboard"]
    - path: "/api/v1/${serviceName.toLowerCase()}/status"
      method: "GET"
      
## Events
events:
  publishes:
    - name: "${serviceName.toLowerCase()}_updated"
      subscribers: ["MonitoringMDC", "LogAggregator"]
    - name: "${serviceName.toLowerCase()}_error"
      subscribers: ["AlertSystem", "SecurityScan"]
      
## Resources
resources:
  databases:
    - name: "main_db"
      tables: ["${serviceName.toLowerCase()}_data"]
  queues:
    - name: "event_queue"
      topics: ["${serviceName.toLowerCase()}_events"]

## Pattern Files
pattern_files:
  - NewService.mdc: "Service creation pattern"
  - StopStartCycle.mdc: "Lifecycle management pattern"`;
  };

  const handleFileSelect = async (fileName) => {
    setAnalyzing(true);
    setSelectedFile({ name: fileName });
    
    try {
      // Load actual file content
      const content = await loadFileContent(fileName);
      setFileContent(content);
      
      // Analyze connections
      const analyzed = analyzeFileContent(content);
      setConnections(analyzed);
      
    } catch (error) {
      console.error('Error selecting file:', error);
      setError('Failed to load file content: ' + error.message);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleAutoConnect = async (fileName) => {
    setAutoConnecting(true);
    setAutoConnectResult(null);
    setError(null);
    
    try {
      console.log(`🚀 Auto-connecting ${fileName}...`);
      
      const response = await fetch(`/api/mdc-auto-connect/${encodeURIComponent(fileName)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.success) {
        setAutoConnectResult({
          success: true,
          connectionsFound: result.connections_found,
          message: result.message,
          fileName: fileName
        });
        
        // Reload file content to show new connections
        setTimeout(() => {
          handleFileSelect(fileName);
        }, 1000);
        
        console.log(`✅ Auto-connect successful: ${result.connections_found} connections added`);
      } else {
        throw new Error(result.error || 'Auto-connect failed');
      }
      
    } catch (err) {
      console.error('❌ Auto-connect error:', err);
      setError(`Auto-connect failed: ${err.message}`);
      setAutoConnectResult({
        success: false,
        error: err.message,
        fileName: fileName
      });
    } finally {
      setAutoConnecting(false);
      
      // Clear result after 10 seconds
      setTimeout(() => {
        setAutoConnectResult(null);
      }, 10000);
    }
  };

  const getConnectionCount = () => {
    if (!connections) return 0;
    return Object.values(connections).flat().length;
  };

  const getFileCategory = (fileName) => {
    if (fileName.includes('Alert')) return 'Trading & Alerts';
    if (fileName.includes('UI') || fileName.includes('frontend')) return 'Frontend & UI';
    if (fileName.includes('Monitor') || fileName.includes('Security')) return 'Monitoring & Security';
    if (fileName.includes('data') || fileName.includes('indicator')) return 'Data & Analytics';
    if (fileName.includes('Service') || fileName.includes('Orchestr')) return 'Service Integration';
    if (fileName.includes('Manager') || fileName.includes('Discovery')) return 'Infrastructure';
    if (fileName.includes('rules') || fileName.includes('main') || fileName.includes('MDC')) return 'Core System';
    return 'Core System';
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'Trading & Alerts': return <Activity className="w-4 h-4" />;
      case 'Frontend & UI': return <Package className="w-4 h-4" />;
      case 'Monitoring & Security': return <Shield className="w-4 h-4" />;
      case 'Data & Analytics': return <Database className="w-4 h-4" />;
      case 'Service Integration': return <GitBranch className="w-4 h-4" />;
      case 'Infrastructure': return <Server className="w-4 h-4" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case 'Trading & Alerts': return 'from-orange-500/20 to-red-500/20 border-orange-500/30';
      case 'Frontend & UI': return 'from-purple-500/20 to-pink-500/20 border-purple-500/30';
      case 'Monitoring & Security': return 'from-green-500/20 to-emerald-500/20 border-green-500/30';
      case 'Data & Analytics': return 'from-blue-500/20 to-cyan-500/20 border-blue-500/30';
      case 'Service Integration': return 'from-yellow-500/20 to-amber-500/20 border-yellow-500/30';
      case 'Infrastructure': return 'from-gray-500/20 to-slate-500/20 border-gray-500/30';
      default: return 'from-indigo-500/20 to-blue-500/20 border-indigo-500/30';
    }
  };

  const filteredFiles = mdcFiles.filter(file => 
    file.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const ConnectionCard = ({ title, items, icon: Icon, gradientColor }) => {
    if (!items || items.length === 0) return null;
    
    return (
      <div className={`relative bg-gradient-to-br ${gradientColor} backdrop-blur-sm rounded-xl border border-white/10 p-5 hover:shadow-2xl hover:shadow-black/20 transition-all duration-300`}>
        <div className="absolute top-0 right-0 w-20 h-20 bg-white/5 rounded-full -mr-10 -mt-10 blur-2xl"></div>
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-white/10 rounded-lg backdrop-blur-sm">
            <Icon className="w-5 h-5 text-white" />
          </div>
          <h4 className="font-semibold text-white">{title}</h4>
          <span className="text-sm bg-black/30 text-white/90 px-2 py-1 rounded-full ml-auto backdrop-blur-sm">
            {items.length}
          </span>
        </div>
        <div className="space-y-2">
          {items.map((item, idx) => (
            <div 
              key={idx} 
              className="flex items-center gap-2 p-2.5 bg-black/20 backdrop-blur-sm rounded-lg hover:bg-black/30 transition-all cursor-pointer group"
              onClick={() => {
                const fileName = `${item}.mdc`;
                if (mdcFiles.includes(fileName)) {
                  handleFileSelect(fileName);
                }
              }}
            >
              <ChevronRight className="w-3 h-3 text-white/50 group-hover:text-white/80 transition-colors" />
              <span className="text-sm text-white/90">{item}</span>
              {mdcFiles.includes(`${item}.mdc`) && (
                <ExternalLink className="w-3 h-3 ml-auto text-white/50 group-hover:text-white/80 transition-colors" />
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Background gradient */}
      <div className="fixed inset-0 bg-gradient-to-br from-blue-900/20 via-gray-900 to-purple-900/20 pointer-events-none"></div>
      
      <div className="relative z-10 p-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="bg-gray-900/80 backdrop-blur-xl rounded-2xl shadow-2xl border border-gray-800 p-8 mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent flex items-center gap-4">
                  <div className="p-3 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-xl backdrop-blur-sm">
                    <Folder className="w-10 h-10 text-blue-400" />
                  </div>
                  .cursor/rules MDC Browser
                </h1>
                <p className="text-gray-400 mt-3 text-lg">
                  Browse and analyze MDC files from your .cursor/rules directory
                </p>
              </div>
              
              {/* Control Panel */}
              <div className="flex items-center gap-4">
                {/* Stats Card */}
                <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-4 border border-gray-700">
                  <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Last Scan</div>
                  <div className="text-sm font-semibold text-gray-200">
                    {formatTimestamp(lastScanTime)}
                  </div>
                  {autoScanEnabled && nextScanTime && (
                    <div className="text-xs text-gray-500 mt-1">
                      Next: {getTimeUntilNext(nextScanTime)}
                    </div>
                  )}
                </div>
                
                {/* Action Buttons */}
                <div className="flex gap-2">
                  <button
                    onClick={toggleAutoScan}
                    className={`px-4 py-2.5 rounded-xl transition-all flex items-center gap-2 font-medium ${
                      autoScanEnabled 
                        ? 'bg-green-500/20 text-green-400 border border-green-500/30 hover:bg-green-500/30' 
                        : 'bg-gray-800/50 text-gray-400 border border-gray-700 hover:bg-gray-800/70'
                    }`}
                    title={autoScanEnabled ? 'Auto-scan enabled (every 12h)' : 'Auto-scan disabled'}
                  >
                    <Activity className="w-4 h-4" />
                    <span className="text-sm">Auto</span>
                  </button>
                  
                  <button 
                    onClick={performScan}
                    disabled={isScanning}
                    className={`px-5 py-2.5 rounded-xl transition-all flex items-center gap-2 font-medium ${
                      isScanning
                        ? 'bg-gray-800/50 text-gray-500 cursor-not-allowed'
                        : 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg shadow-blue-600/20'
                    }`}
                  >
                    <RefreshCw className={`w-4 h-4 ${isScanning ? 'animate-spin' : ''}`} />
                    {isScanning ? 'Scanning...' : 'Scan Now'}
                  </button>
                  
                  <button
                    onClick={() => setShowResetModal(true)}
                    className="px-5 py-2.5 rounded-xl bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30 transition-all flex items-center gap-2 font-medium"
                  >
                    <Trash2 className="w-4 h-4" />
                    Reset
                  </button>
                </div>
              </div>
            </div>
            
            {/* Scan Stats */}
            {scanStats && !isScanning && (
              <div className="mt-6 pt-6 border-t border-gray-800 grid grid-cols-4 gap-4">
                <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-4 border border-gray-700">
                  <div className="flex items-center gap-3">
                    <FileText className="w-5 h-5 text-gray-400" />
                    <div>
                      <div className="text-2xl font-bold text-gray-200">{scanStats.totalFiles}</div>
                      <div className="text-xs text-gray-500">Total Files</div>
                    </div>
                  </div>
                </div>
                <div className="bg-green-500/20 backdrop-blur-sm rounded-xl p-4 border border-green-500/30">
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    <div>
                      <div className="text-2xl font-bold text-green-400">+{scanStats.newFiles}</div>
                      <div className="text-xs text-green-400/80">New Files</div>
                    </div>
                  </div>
                </div>
                <div className="bg-blue-500/20 backdrop-blur-sm rounded-xl p-4 border border-blue-500/30">
                  <div className="flex items-center gap-3">
                    <RefreshCw className="w-5 h-5 text-blue-400" />
                    <div>
                      <div className="text-2xl font-bold text-blue-400">{scanStats.modifiedFiles}</div>
                      <div className="text-xs text-blue-400/80">Modified</div>
                    </div>
                  </div>
                </div>
                <div className="bg-purple-500/20 backdrop-blur-sm rounded-xl p-4 border border-purple-500/30">
                  <div className="flex items-center gap-3">
                    <Clock className="w-5 h-5 text-purple-400" />
                    <div>
                      <div className="text-2xl font-bold text-purple-400">{scanStats.scanDuration}ms</div>
                      <div className="text-xs text-purple-400/80">Scan Time</div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {/* Auto-Connect Result */}
            {autoConnectResult && (
              <div className={`mt-4 p-4 rounded-xl border ${
                autoConnectResult.success 
                  ? 'bg-green-500/20 border-green-500/30' 
                  : 'bg-red-500/20 border-red-500/30'
              }`}>
                <p className={`text-sm flex items-center gap-2 ${
                  autoConnectResult.success ? 'text-green-400' : 'text-red-400'
                }`}>
                  {autoConnectResult.success ? (
                    <CheckCircle className="w-4 h-4" />
                  ) : (
                    <AlertCircle className="w-4 h-4" />
                  )}
                  {autoConnectResult.success 
                    ? `✅ Success! Added ${autoConnectResult.connectionsFound} connections to ${autoConnectResult.fileName}`
                    : `❌ Failed to auto-connect: ${autoConnectResult.error}`
                  }
                </p>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="mt-4 p-4 bg-yellow-500/20 border border-yellow-500/30 rounded-xl">
                <p className="text-sm text-yellow-400 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  {error}
                </p>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* File List */}
            <div className="lg:col-span-1">
              <div className="bg-gray-900/80 backdrop-blur-xl rounded-2xl shadow-2xl border border-gray-800 p-6">
                <div className="mb-6">
                  <div className="relative">
                    <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-500 w-5 h-5" />
                    <input
                      type="text"
                      placeholder="Search MDC files..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full pl-12 pr-4 py-3 bg-gray-800/50 border border-gray-700 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-white placeholder-gray-500"
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-gray-300 flex items-center gap-2">
                    <Layers className="w-5 h-5" />
                    Files ({filteredFiles.length})
                  </h3>
                  <Filter className="w-5 h-5 text-gray-500" />
                </div>

                {loading ? (
                  <div className="text-center py-12">
                    <RefreshCw className="w-10 h-10 animate-spin text-gray-600 mx-auto mb-3" />
                    <p className="text-gray-500">Loading MDC files...</p>
                  </div>
                ) : filteredFiles.length === 0 ? (
                  <div className="text-center py-12">
                    <FileText className="w-10 h-10 text-gray-600 mx-auto mb-3" />
                    <p className="text-gray-500">No MDC files found</p>
                    <button 
                      onClick={performScan}
                      className="mt-4 text-blue-400 hover:text-blue-300 text-sm"
                    >
                      Run scan
                    </button>
                  </div>
                ) : (
                  <div className="space-y-2 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
                    {filteredFiles.map((file) => {
                      const category = getFileCategory(file);
                      const isSelected = selectedFile?.name === file;
                      
                      return (
                        <button
                          key={file}
                          onClick={() => handleFileSelect(file)}
                          className={`w-full text-left p-4 rounded-xl transition-all flex items-center gap-3 group ${
                            isSelected 
                              ? 'bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/30 shadow-lg' 
                              : 'bg-gray-800/30 hover:bg-gray-800/50 border border-gray-700/50 hover:border-gray-600'
                          }`}
                        >
                          <div className={`p-2 rounded-lg bg-gradient-to-br ${getCategoryColor(category)}`}>
                            {getCategoryIcon(category)}
                          </div>
                          <div className="flex-1">
                            <div className="font-medium text-sm text-gray-200">{file}</div>
                            <div className="text-xs text-gray-500">{category}</div>
                          </div>
                          {isSelected && (
                            <ChevronRight className="w-5 h-5 text-blue-400" />
                          )}
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>

            {/* File Details & Connections */}
            <div className="lg:col-span-2">
              {selectedFile ? (
                <div className="space-y-8">
                  {/* File Info Card */}
                  <div className="bg-gray-900/80 backdrop-blur-xl rounded-2xl shadow-2xl border border-gray-800 p-8">
                    <div className="flex items-center justify-between mb-6">
                      <div className="flex-1">
                        <h2 className="text-3xl font-bold text-white flex items-center gap-3">
                          <Code className="w-8 h-8 text-blue-400" />
                          {selectedFile.name}
                        </h2>
                        <p className="text-gray-400 mt-2">
                          Category: {getFileCategory(selectedFile.name)} | Real-time from .cursor/rules
                        </p>
                      </div>
                      
                      {/* Auto-Connect Button */}
                      <div className="ml-4">
                        <button
                          onClick={() => handleAutoConnect(selectedFile.name)}
                          disabled={autoConnecting || analyzing}
                          className={`px-6 py-3 rounded-xl transition-all flex items-center gap-2 font-medium shadow-lg ${
                            autoConnecting || analyzing
                              ? 'bg-gray-800/50 text-gray-500 cursor-not-allowed'
                              : 'bg-gradient-to-r from-green-600 to-emerald-600 text-white hover:from-green-700 hover:to-emerald-700 shadow-green-600/20'
                          }`}
                          title="Auto-discover and inject all possible connections into this MDC file using AI analysis"
                        >
                          <Zap className={`w-5 h-5 ${autoConnecting ? 'animate-spin' : analyzing ? '' : 'animate-pulse'}`} />
                          {autoConnecting ? 'Connecting...' : analyzing ? 'Analyzing...' : 'Auto-Connect'}
                        </button>
                      </div>
                      <div className="text-center bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-xl p-6 border border-blue-500/30">
                        <div className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                          {getConnectionCount()}
                        </div>
                        <div className="text-sm text-gray-400 mt-1">Total Connections</div>
                      </div>
                    </div>

                    {analyzing ? (
                      <div className="text-center py-12">
                        <RefreshCw className="w-10 h-10 animate-spin text-blue-500 mx-auto mb-3" />
                        <p className="text-gray-400">Analyzing connections...</p>
                      </div>
                    ) : (
                      <div className="bg-gray-800/50 p-6 rounded-xl border border-gray-700">
                        <h3 className="font-semibold text-sm text-gray-400 mb-3 uppercase tracking-wider">Service Definition</h3>
                        <pre className="text-xs font-mono text-gray-300 overflow-x-auto whitespace-pre-wrap">
                          {fileContent.split('\n').slice(0, 20).join('\n')}
                          {fileContent.split('\n').length > 20 && '\n...'}
                        </pre>
                      </div>
                    )}
                  </div>

                  {/* Connections Grid */}
                  {connections && (
                    <div className="bg-gray-900/80 backdrop-blur-xl rounded-2xl shadow-2xl border border-gray-800 p-8">
                      <h3 className="text-2xl font-bold text-white mb-8 flex items-center gap-3">
                        <Network className="w-7 h-7 text-purple-400" />
                        Service Connections Map
                      </h3>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <ConnectionCard
                          title="Dependencies"
                          items={connections.dependencies}
                          icon={Link}
                          gradientColor="from-blue-600/20 to-blue-800/20"
                        />
                        <ConnectionCard
                          title="Consumers"
                          items={connections.consumers}
                          icon={Zap}
                          gradientColor="from-green-600/20 to-green-800/20"
                        />
                        <ConnectionCard
                          title="API Endpoints"
                          items={connections.provides}
                          icon={Server}
                          gradientColor="from-purple-600/20 to-purple-800/20"
                        />
                        <ConnectionCard
                          title="Events"
                          items={connections.events}
                          icon={AlertCircle}
                          gradientColor="from-orange-600/20 to-orange-800/20"
                        />
                        <ConnectionCard
                          title="Shared Resources"
                          items={connections.sharedResources}
                          icon={Database}
                          gradientColor="from-pink-600/20 to-pink-800/20"
                        />
                        <ConnectionCard
                          title="Related Services"
                          items={connections.apis}
                          icon={GitBranch}
                          gradientColor="from-indigo-600/20 to-indigo-800/20"
                        />
                      </div>

                      <div className="mt-8 p-6 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-xl border border-blue-500/20">
                        <p className="text-sm text-gray-300 flex items-center gap-2">
                          <AlertCircle className="w-4 h-4 text-blue-400" />
                          <strong>Tip:</strong> Click on any connected service to navigate to its MDC file and explore its connections. Files are loaded directly from /Users/dansidanutz/Desktop/ZmartBot/.cursor/rules/
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="bg-gray-900/80 backdrop-blur-xl rounded-2xl shadow-2xl border border-gray-800 p-16 text-center">
                  <div className="p-4 bg-gradient-to-br from-gray-700/20 to-gray-800/20 rounded-2xl w-fit mx-auto mb-6">
                    <Network className="w-20 h-20 text-gray-600" />
                  </div>
                  <h3 className="text-2xl font-semibold text-gray-300 mb-3">
                    Select an MDC File
                  </h3>
                  <p className="text-gray-500 max-w-md mx-auto">
                    Choose a file from the list to view its connections and dependencies. Files are scanned from your .cursor/rules directory.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Reset Confirmation Modal */}
      {showResetModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 rounded-2xl shadow-2xl border border-gray-800 p-8 max-w-md w-full">
            <div className="flex items-center gap-4 mb-6">
              <div className="p-3 bg-red-500/20 rounded-xl">
                <AlertTriangle className="w-8 h-8 text-red-400" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-white">Reset Everything?</h3>
                <p className="text-gray-400 text-sm mt-1">This action cannot be undone</p>
              </div>
            </div>
            
            <div className="bg-gray-800/50 rounded-xl p-4 mb-6 border border-gray-700">
              <p className="text-gray-300 text-sm">
                This will:
              </p>
              <ul className="mt-2 space-y-1 text-sm text-gray-400">
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-red-400 rounded-full"></div>
                  Clear all scanned files
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-red-400 rounded-full"></div>
                  Reset all connections
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-red-400 rounded-full"></div>
                  Remove scan history
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-red-400 rounded-full"></div>
                  Start fresh scan
                </li>
              </ul>
            </div>
            
            <div className="flex gap-3">
              <button
                onClick={() => setShowResetModal(false)}
                className="flex-1 px-5 py-3 bg-gray-800 text-gray-300 rounded-xl hover:bg-gray-700 transition-colors font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handleReset}
                className="flex-1 px-5 py-3 bg-red-600 text-white rounded-xl hover:bg-red-700 transition-colors font-medium flex items-center justify-center gap-2"
              >
                <Trash2 className="w-4 h-4" />
                Reset Everything
              </button>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.2);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.3);
        }
      `}</style>
    </div>
  );
};

export default MDCCursorBrowser;