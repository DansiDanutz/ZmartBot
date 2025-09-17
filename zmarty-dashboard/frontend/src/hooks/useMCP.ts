import { useState, useEffect } from 'react';
import { useQuery, UseQueryResult } from 'react-query';
import { mcpService, MCPAsset, FigmaDesignTokens } from '../services/mcp';

// Hook to get a specific asset
export function useMCPAsset(assetId: string, fallback?: string): {
  url: string;
  loading: boolean;
  error: boolean;
  asset: MCPAsset | null;
} {
  const [asset, setAsset] = useState<MCPAsset | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let mounted = true;

    const fetchAsset = async () => {
      try {
        setLoading(true);
        setError(false);
        
        const fetchedAsset = await mcpService.getAsset(assetId);
        
        if (mounted) {
          setAsset(fetchedAsset);
          setError(!fetchedAsset);
        }
      } catch (err) {
        if (mounted) {
          setError(true);
          setAsset(null);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    if (assetId) {
      fetchAsset();
    } else {
      setLoading(false);
      setAsset(null);
    }

    return () => {
      mounted = false;
    };
  }, [assetId]);

  return {
    url: asset?.url || fallback || '',
    loading,
    error,
    asset
  };
}

// Hook to get design tokens
export function useMCPDesignTokens(): UseQueryResult<FigmaDesignTokens, Error> {
  return useQuery(
    'figma-design-tokens',
    () => mcpService.getDesignTokens(),
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      retry: 2,
      retryDelay: 1000
    }
  );
}

// Hook to get icon by name
export function useMCPIcon(iconName: string, fallback?: string): {
  url: string;
  loading: boolean;
  error: boolean;
} {
  const [url, setUrl] = useState<string>(fallback || '');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let mounted = true;

    const fetchIcon = async () => {
      try {
        setLoading(true);
        setError(false);
        
        const iconUrl = await mcpService.getIcon(iconName);
        
        if (mounted) {
          setUrl(iconUrl || fallback || '');
          setError(!iconUrl && !fallback);
        }
      } catch (err) {
        if (mounted) {
          setError(true);
          setUrl(fallback || '');
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    if (iconName) {
      fetchIcon();
    } else {
      setLoading(false);
      setUrl(fallback || '');
    }

    return () => {
      mounted = false;
    };
  }, [iconName, fallback]);

  return { url, loading, error };
}

// Hook to get multiple assets
export function useMCPAssets(category?: string): UseQueryResult<MCPAsset[], Error> {
  return useQuery(
    ['figma-assets', category],
    () => mcpService.getAssets(category),
    {
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
      retry: 2
    }
  );
}

// Hook to preload assets
export function useMCPPreload(assetIds: string[]): {
  loading: boolean;
  error: boolean;
  preload: () => Promise<void>;
} {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  const preload = async () => {
    try {
      setLoading(true);
      setError(false);
      await mcpService.preloadAssets(assetIds);
    } catch (err) {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  return { loading, error, preload };
}

// Hook to check MCP server availability
export function useMCPStatus(): {
  available: boolean;
  checking: boolean;
  checkStatus: () => Promise<void>;
} {
  const [available, setAvailable] = useState(false);
  const [checking, setChecking] = useState(false);

  const checkStatus = async () => {
    setChecking(true);
    try {
      const isAvailable = await mcpService.isAvailable();
      setAvailable(isAvailable);
    } catch (err) {
      setAvailable(false);
    } finally {
      setChecking(false);
    }
  };

  useEffect(() => {
    checkStatus();
  }, []);

  return { available, checking, checkStatus };
}