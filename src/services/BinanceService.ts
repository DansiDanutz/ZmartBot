import axios from 'axios';

// Binance API endpoints
const BINANCE_BASE_URL = 'https://api.binance.com';
const BINANCE_FUTURES_URL = 'https://fapi.binance.com';

export interface BinanceTicker {
  symbol: string;
  priceChange: string;
  priceChangePercent: string;
  weightedAvgPrice: string;
  prevClosePrice: string;
  lastPrice: string;
  lastQty: string;
  bidPrice: string;
  bidQty: string;
  askPrice: string;
  askQty: string;
  openPrice: string;
  highPrice: string;
  lowPrice: string;
  volume: string;
  quoteVolume: string;
  openTime: number;
  closeTime: number;
  firstId: number;
  lastId: number;
  count: number;
}

export interface BinanceKline {
  openTime: number;
  open: string;
  high: string;
  low: string;
  close: string;
  volume: string;
  closeTime: number;
  quoteAssetVolume: string;
  numberOfTrades: number;
  takerBuyBaseAssetVolume: string;
  takerBuyQuoteAssetVolume: string;
  ignore: string;
}

export class BinanceService {
  private static instance: BinanceService;

  private constructor() {}

  public static getInstance(): BinanceService {
    if (!BinanceService.instance) {
      BinanceService.instance = new BinanceService();
    }
    return BinanceService.instance;
  }

  // Get 24hr ticker for all symbols
  async getAllTickers(): Promise<BinanceTicker[]> {
    try {
      const response = await axios.get(`${BINANCE_BASE_URL}/api/v3/ticker/24hr`);
      return response.data;
    } catch (error) {
      console.error('Error fetching Binance tickers:', error);
      throw error;
    }
  }

  // Get ticker for specific symbol
  async getTicker(symbol: string): Promise<BinanceTicker> {
    try {
      const response = await axios.get(`${BINANCE_BASE_URL}/api/v3/ticker/24hr`, {
        params: { symbol: symbol.toUpperCase() }
      });
      return response.data;
    } catch (error) {
      console.error(`Error fetching Binance ticker for ${symbol}:`, error);
      throw error;
    }
  }

  // Get kline/candlestick data
  async getKlines(symbol: string, interval: string, limit: number = 100): Promise<BinanceKline[]> {
    try {
      const response = await axios.get(`${BINANCE_BASE_URL}/api/v3/klines`, {
        params: {
          symbol: symbol.toUpperCase(),
          interval,
          limit
        }
      });
      
      return response.data.map((kline: any[]) => ({
        openTime: kline[0],
        open: kline[1],
        high: kline[2],
        low: kline[3],
        close: kline[4],
        volume: kline[5],
        closeTime: kline[6],
        quoteAssetVolume: kline[7],
        numberOfTrades: kline[8],
        takerBuyBaseAssetVolume: kline[9],
        takerBuyQuoteAssetVolume: kline[10],
        ignore: kline[11]
      }));
    } catch (error) {
      console.error(`Error fetching Binance klines for ${symbol}:`, error);
      throw error;
    }
  }

  // Get futures ticker (for futures trading)
  async getFuturesTicker(symbol: string): Promise<BinanceTicker> {
    try {
      const response = await axios.get(`${BINANCE_FUTURES_URL}/fapi/v1/ticker/24hr`, {
        params: { symbol: symbol.toUpperCase() }
      });
      return response.data;
    } catch (error) {
      console.error(`Error fetching Binance futures ticker for ${symbol}:`, error);
      throw error;
    }
  }

  // Get order book
  async getOrderBook(symbol: string, limit: number = 100): Promise<any> {
    try {
      const response = await axios.get(`${BINANCE_BASE_URL}/api/v3/depth`, {
        params: {
          symbol: symbol.toUpperCase(),
          limit
        }
      });
      return response.data;
    } catch (error) {
      console.error(`Error fetching Binance order book for ${symbol}:`, error);
      throw error;
    }
  }

  // Get recent trades
  async getRecentTrades(symbol: string, limit: number = 100): Promise<any[]> {
    try {
      const response = await axios.get(`${BINANCE_BASE_URL}/api/v3/trades`, {
        params: {
          symbol: symbol.toUpperCase(),
          limit
        }
      });
      return response.data;
    } catch (error) {
      console.error(`Error fetching Binance recent trades for ${symbol}:`, error);
      throw error;
    }
  }
}

export default BinanceService.getInstance();
