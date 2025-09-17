import axios from 'axios';

const MCP_BASE_URL = 'http://localhost:3001';

export interface MCPAsset {
  id: string;
  url: string;
  type: 'image' | 'svg' | 'icon';
  name: string;
  category?: string;
}

export interface FigmaDesignTokens {
  colors: {
    [key: string]: string;
  };
  spacing: {
    [key: string]: string;
  };
  typography: {
    [key: string]: {
      fontSize: string;
      fontWeight: string;
      lineHeight: string;
    };
  };
  shadows: {
    [key: string]: string;
  };
  radii: {
    [key: string]: string;
  };
}

class MCPService {
  private cache = new Map<string, any>();
  private cacheExpiry = new Map<string, number>();
  private readonly CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

  private isExpired(key: string): boolean {
    const expiry = this.cacheExpiry.get(key);
    return !expiry || Date.now() > expiry;
  }

  private setCache(key: string, value: any): void {
    this.cache.set(key, value);
    this.cacheExpiry.set(key, Date.now() + this.CACHE_DURATION);
  }

  private getCache(key: string): any | null {
    if (this.isExpired(key)) {
      this.cache.delete(key);
      this.cacheExpiry.delete(key);
      return null;
    }
    return this.cache.get(key) || null;
  }

  async getAssets(category?: string): Promise<MCPAsset[]> {
    const cacheKey = `assets-${category || 'all'}`;
    const cached = this.getCache(cacheKey);
    
    if (cached) {
      return cached;
    }

    try {
      const response = await axios.get(`${MCP_BASE_URL}/api/figma/assets`, {
        params: { category },
        timeout: 10000
      });
      
      const assets = response.data.assets || [];
      this.setCache(cacheKey, assets);
      return assets;
      
    } catch (error) {
      console.warn('Failed to fetch MCP assets:', error);
      return [];
    }
  }

  async getAsset(assetId: string): Promise<MCPAsset | null> {
    const cacheKey = `asset-${assetId}`;
    const cached = this.getCache(cacheKey);
    
    if (cached) {
      return cached;
    }

    try {
      const response = await axios.get(`${MCP_BASE_URL}/api/figma/assets/${assetId}`, {
        timeout: 10000
      });
      
      const asset = response.data.asset;
      if (asset) {
        this.setCache(cacheKey, asset);
      }
      return asset || null;
      
    } catch (error) {
      console.warn(`Failed to fetch MCP asset ${assetId}:`, error);
      return null;
    }
  }

  async getDesignTokens(): Promise<FigmaDesignTokens | null> {
    const cacheKey = 'design-tokens';
    const cached = this.getCache(cacheKey);
    
    if (cached) {
      return cached;
    }

    try {
      const response = await axios.get(`${MCP_BASE_URL}/api/figma/tokens`, {
        timeout: 10000
      });
      
      const tokens = response.data.tokens;
      if (tokens) {
        this.setCache(cacheKey, tokens);
      }
      return tokens || null;
      
    } catch (error) {
      console.warn('Failed to fetch design tokens:', error);
      return null;
    }
  }

  async getIcon(iconName: string): Promise<string | null> {
    const assets = await this.getAssets('icons');
    const icon = assets.find(asset => 
      asset.name.toLowerCase().includes(iconName.toLowerCase()) ||
      asset.id === iconName
    );
    
    return icon ? icon.url : null;
  }

  // Preload commonly used assets
  async preloadAssets(assetIds: string[]): Promise<void> {
    const promises = assetIds.map(id => this.getAsset(id));
    await Promise.allSettled(promises);
  }

  // Clear cache (useful for development)
  clearCache(): void {
    this.cache.clear();
    this.cacheExpiry.clear();
  }

  // Get asset URL with fallback
  async getAssetUrl(assetId: string, fallback?: string): Promise<string> {
    const asset = await this.getAsset(assetId);
    return asset?.url || fallback || '';
  }

  // Check if MCP server is available
  async isAvailable(): Promise<boolean> {
    try {
      const response = await axios.get(`${MCP_BASE_URL}/health`, {
        timeout: 3000
      });
      return response.status === 200;
    } catch (error) {
      return false;
    }
  }
}

export const mcpService = new MCPService();

// React hooks for easy usage
export { useMCPAsset, useMCPDesignTokens, useMCPIcon } from './hooks/useMCP';