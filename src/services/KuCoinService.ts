import axios from 'axios';

// KuCoin API endpoints
const KUCOIN_BASE_URL = 'https://api.kucoin.com';

export interface KuCoinTicker {
  symbol: string;
  symbolName: string;
  buy: string;
  sell: string;
  changeRate: string;
  changePrice: string;
  high: string;
  low: string;
  vol: string;
  volValue: string;
  last: string;
  averagePrice: string;
  takerFeeRate: string;
  makerFeeRate: string;
  takerCoefficient: string;
  makerCoefficient: string;
}

export interface KuCoinKline {
  time: number;
  open: string;
  close: string;
  high: string;
  low: string;
  volume: string;
  turnover: string;
}

export class KuCoinService {
  private static instance: KuCoinService;

  private constructor() {}

  public static getInstance(): KuCoinService {
    if (!KuCoinService.instance) {
      KuCoinService.instance = new KuCoinService();
    }
    return KuCoinService.instance;
  }

  // Get all tickers
  async getAllTickers(): Promise<KuCoinTicker[]> {
    try {
      const response = await axios.get(`${KUCOIN_BASE_URL}/api/v1/market/allTickers`);
      return response.data.data.ticker;
    } catch (error) {
      console.error('Error fetching KuCoin tickers:', error);
      throw error;
    }
  }

  // Get ticker for specific symbol
  async getTicker(symbol: string): Promise<KuCoinTicker> {
    try {
      const response = await axios.get(`${KUCOIN_BASE_URL}/api/v1/market/orderbook`, {
        params: { symbol: symbol.toUpperCase() }
      });
      
      // KuCoin doesn't have a direct ticker endpoint, so we'll use orderbook data
      const orderbook = response.data.data;
      return {
        symbol: symbol.toUpperCase(),
        symbolName: symbol.toUpperCase(),
        buy: orderbook.bids[0]?.[0] || '0',
        sell: orderbook.asks[0]?.[0] || '0',
        changeRate: '0',
        changePrice: '0',
        high: '0',
        low: '0',
        vol: '0',
        volValue: '0',
        last: orderbook.bids[0]?.[0] || '0',
        averagePrice: '0',
        takerFeeRate: '0.001',
        makerFeeRate: '0.001',
        takerCoefficient: '1',
        makerCoefficient: '1'
      };
    } catch (error) {
      console.error(`Error fetching KuCoin ticker for ${symbol}:`, error);
      throw error;
    }
  }

  // Get kline/candlestick data
  async getKlines(symbol: string, type: string = '1min', startAt?: number, endAt?: number): Promise<KuCoinKline[]> {
    try {
      const params: any = {
        symbol: symbol.toUpperCase(),
        type
      };
      
      if (startAt) params.startAt = startAt;
      if (endAt) params.endAt = endAt;

      const response = await axios.get(`${KUCOIN_BASE_URL}/api/v1/market/candles`, { params });
      
      return response.data.data.map((kline: any[]) => ({
        time: kline[0],
        open: kline[1],
        close: kline[2],
        high: kline[3],
        low: kline[4],
        volume: kline[5],
        turnover: kline[6]
      }));
    } catch (error) {
      console.error(`Error fetching KuCoin klines for ${symbol}:`, error);
      throw error;
    }
  }

  // Get order book
  async getOrderBook(symbol: string): Promise<any> {
    try {
      const response = await axios.get(`${KUCOIN_BASE_URL}/api/v1/market/orderbook`, {
        params: { symbol: symbol.toUpperCase() }
      });
      return response.data.data;
    } catch (error) {
      console.error(`Error fetching KuCoin order book for ${symbol}:`, error);
      throw error;
    }
  }

  // Get recent trades
  async getRecentTrades(symbol: string): Promise<any[]> {
    try {
      const response = await axios.get(`${KUCOIN_BASE_URL}/api/v1/market/histories`, {
        params: { symbol: symbol.toUpperCase() }
      });
      return response.data.data;
    } catch (error) {
      console.error(`Error fetching KuCoin recent trades for ${symbol}:`, error);
      throw error;
    }
  }

  // Get market stats
  async getMarketStats(symbol: string): Promise<any> {
    try {
      const response = await axios.get(`${KUCOIN_BASE_URL}/api/v1/market/stats`, {
        params: { symbol: symbol.toUpperCase() }
      });
      return response.data.data;
    } catch (error) {
      console.error(`Error fetching KuCoin market stats for ${symbol}:`, error);
      throw error;
    }
  }

  // Get supported symbols
  async getSupportedSymbols(): Promise<string[]> {
    try {
      const response = await axios.get(`${KUCOIN_BASE_URL}/api/v1/symbols`);
      return response.data.data.map((symbol: any) => symbol.symbol);
    } catch (error) {
      console.error('Error fetching KuCoin supported symbols:', error);
      throw error;
    }
  }
}

export default KuCoinService.getInstance();
