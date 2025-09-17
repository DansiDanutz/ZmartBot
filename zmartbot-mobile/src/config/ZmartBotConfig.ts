// ZmartBot Ecosystem Configuration
// This file configures the mobile app to connect with your ZmartBot infrastructure

export interface ZmartBotEcosystemConfig {
  zmartApi: {
    baseUrl: string;
    port: number;
    endpoints: {
      health: string;
      marketData: string;
      portfolio: string;
      tradingSignals: string;
      iotDevices: string;
    };
  };
  mobileService: {
    baseUrl: string;
    port: number;
    endpoints: {
      health: string;
      marketData: string;
      portfolio: string;
      tradingSignals: string;
      iotDevices: string;
      zmartIntegration: string;
    };
  };
  exchanges: {
    binance: {
      baseUrl: string;
      apiKey?: string;
    };
    kucoin: {
      baseUrl: string;
      apiKey?: string;
    };
  };
  iot: {
    baseUrl: string;
    endpoints: {
      devices: string;
      data: string;
    };
  };
}

export const DEFAULT_ZMARTBOT_CONFIG: ZmartBotEcosystemConfig = {
  zmartApi: {
    baseUrl: 'http://localhost',
    port: 8000,
    endpoints: {
      health: '/health',
      marketData: '/api/market-data',
      portfolio: '/api/portfolio',
      tradingSignals: '/api/trading-signals',
      iotDevices: '/api/iot-devices',
    },
  },
  mobileService: {
    baseUrl: 'http://localhost',
    port: 7777, // RESERVED PORT FOR MOBILE APP SERVICE - NO EXCEPTIONS
    endpoints: {
      health: '/health',
      marketData: '/api/market-data',
      portfolio: '/api/portfolio',
      tradingSignals: '/api/trading-signals',
      iotDevices: '/api/iot-devices',
      zmartIntegration: '/api/zmart-integration',
    },
  },
  exchanges: {
    binance: {
      baseUrl: 'https://api.binance.com',
    },
    kucoin: {
      baseUrl: 'https://api.kucoin.com',
    },
  },
  iot: {
    baseUrl: 'http://localhost:8000',
    endpoints: {
      devices: '/api/iot-devices',
      data: '/api/iot-data',
    },
  },
};

// Configuration management
let currentConfig = { ...DEFAULT_ZMARTBOT_CONFIG };

export function getZmartBotConfig(): ZmartBotEcosystemConfig {
  return { ...currentConfig };
}

export function setZmartBotConfig(newConfig: Partial<ZmartBotEcosystemConfig>): void {
  currentConfig = { ...currentConfig, ...newConfig };
}

// URL building utilities
export function buildApiUrl(endpoint: string): string {
  return `${currentConfig.zmartApi.baseUrl}:${currentConfig.zmartApi.port}${endpoint}`;
}

export function buildMobileServiceUrl(endpoint: string): string {
  return `${currentConfig.mobileService.baseUrl}:${currentConfig.mobileService.port}${endpoint}`;
}

export function buildExchangeUrl(exchange: 'binance' | 'kucoin', endpoint: string): string {
  return `${currentConfig.exchanges[exchange].baseUrl}${endpoint}`;
}

export function buildIoTUrl(endpoint: string): string {
  return `${currentConfig.iot.baseUrl}${endpoint}`;
}

// Configuration validation
export function validateConfig(config: ZmartBotEcosystemConfig): boolean {
  // Ensure mobile service uses port 7777
  if (config.mobileService.port !== 7777) {
    console.error('❌ INVALID CONFIGURATION: Mobile service MUST use port 7777');
    return false;
  }
  
  // Ensure zmart-api uses port 8000
  if (config.zmartApi.port !== 8000) {
    console.error('❌ INVALID CONFIGURATION: ZmartBot API MUST use port 8000');
    return false;
  }
  
  return true;
}

// Port constants for easy reference
export const PORTS = {
  MOBILE_SERVICE: 7777, // RESERVED FOR MOBILE APP SERVICE ONLY
  ZMART_API: 8000,      // Main backend API
  MASTER_ORCHESTRATION: 8002, // Master orchestration agent
  PROFESSIONAL_DASHBOARD: 3400, // Frontend dashboard
} as const;

// Port validation
export function validatePortAssignment(serviceName: string, port: number): boolean {
  if (serviceName === 'mobile-service' && port !== PORTS.MOBILE_SERVICE) {
    console.error(`❌ PORT VIOLATION: ${serviceName} MUST use port ${PORTS.MOBILE_SERVICE}, not ${port}`);
    return false;
  }
  
  if (serviceName === 'zmart-api' && port !== PORTS.ZMART_API) {
    console.error(`❌ PORT VIOLATION: ${serviceName} MUST use port ${PORTS.ZMART_API}, not ${port}`);
    return false;
  }
  
  return true;
}
