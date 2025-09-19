export interface AIProvider {
  name: string;
  analyze(data: MarketData): Promise<AIAnalysis>;
  getConfidence(): number;
  isAvailable(): boolean;
}

export interface MarketData {
  symbol: string;
  price: number;
  volume: number;
  timestamp: Date;
  indicators?: {
    rsi?: number;
    macd?: number;
    bollinger?: { upper: number; lower: number; middle: number };
  };
}

export interface AIAnalysis {
  provider: string;
  signal: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  reasoning: string;
  targetPrice?: number;
  stopLoss?: number;
  timeframe: string;
}

class OpenAIProvider implements AIProvider {
  name = 'OpenAI GPT-4';

  async analyze(data: MarketData): Promise<AIAnalysis> {
    try {
      const response = await fetch('/api/ai/openai/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      return await response.json();
    } catch (error) {
      throw new Error(`OpenAI analysis failed: ${error}`);
    }
  }

  getConfidence(): number {
    return 0.85;
  }

  isAvailable(): boolean {
    return true;
  }
}

class ClaudeProvider implements AIProvider {
  name = 'Claude 3';

  async analyze(data: MarketData): Promise<AIAnalysis> {
    try {
      const response = await fetch('/api/ai/claude/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      return await response.json();
    } catch (error) {
      throw new Error(`Claude analysis failed: ${error}`);
    }
  }

  getConfidence(): number {
    return 0.88;
  }

  isAvailable(): boolean {
    return true;
  }
}

class GeminiProvider implements AIProvider {
  name = 'Google Gemini';

  async analyze(data: MarketData): Promise<AIAnalysis> {
    try {
      const response = await fetch('/api/ai/gemini/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      return await response.json();
    } catch (error) {
      throw new Error(`Gemini analysis failed: ${error}`);
    }
  }

  getConfidence(): number {
    return 0.82;
  }

  isAvailable(): boolean {
    return true;
  }
}

class LocalMLProvider implements AIProvider {
  name = 'Local ML Model';

  async analyze(data: MarketData): Promise<AIAnalysis> {
    const rsi = data.indicators?.rsi || 50;
    const signal = rsi > 70 ? 'SELL' : rsi < 30 ? 'BUY' : 'HOLD';

    return {
      provider: this.name,
      signal,
      confidence: Math.abs(50 - rsi) / 50,
      reasoning: `RSI-based analysis: ${rsi.toFixed(2)}`,
      targetPrice: data.price * (signal === 'BUY' ? 1.05 : 0.95),
      stopLoss: data.price * (signal === 'BUY' ? 0.97 : 1.03),
      timeframe: '4H'
    };
  }

  getConfidence(): number {
    return 0.75;
  }

  isAvailable(): boolean {
    return true;
  }
}

export class MultiProviderAIService {
  private providers: AIProvider[] = [
    new OpenAIProvider(),
    new ClaudeProvider(),
    new GeminiProvider(),
    new LocalMLProvider()
  ];

  async getConsensusAnalysis(data: MarketData): Promise<{
    consensus: 'BUY' | 'SELL' | 'HOLD';
    confidence: number;
    analyses: AIAnalysis[];
    reasoning: string;
  }> {
    const availableProviders = this.providers.filter(p => p.isAvailable());

    const analysisPromises = availableProviders.map(provider =>
      provider.analyze(data).catch(err => {
        console.error(`Provider ${provider.name} failed:`, err);
        return null;
      })
    );

    const analyses = (await Promise.all(analysisPromises))
      .filter((a): a is AIAnalysis => a !== null);

    if (analyses.length === 0) {
      throw new Error('No AI providers available');
    }

    const votes = { BUY: 0, SELL: 0, HOLD: 0 };
    let totalConfidence = 0;

    analyses.forEach(analysis => {
      const weight = analysis.confidence;
      votes[analysis.signal] += weight;
      totalConfidence += analysis.confidence;
    });

    const consensus = Object.entries(votes).reduce((a, b) =>
      votes[a[0] as keyof typeof votes] > votes[b[0] as keyof typeof votes] ? a : b
    )[0] as 'BUY' | 'SELL' | 'HOLD';

    const avgConfidence = totalConfidence / analyses.length;

    const reasoning = `Consensus from ${analyses.length} AI providers: ` +
      `${(votes.BUY / totalConfidence * 100).toFixed(0)}% BUY, ` +
      `${(votes.SELL / totalConfidence * 100).toFixed(0)}% SELL, ` +
      `${(votes.HOLD / totalConfidence * 100).toFixed(0)}% HOLD`;

    return {
      consensus,
      confidence: avgConfidence,
      analyses,
      reasoning
    };
  }

  async getProviderAnalysis(providerName: string, data: MarketData): Promise<AIAnalysis> {
    const provider = this.providers.find(p => p.name === providerName);
    if (!provider) {
      throw new Error(`Provider ${providerName} not found`);
    }
    if (!provider.isAvailable()) {
      throw new Error(`Provider ${providerName} is not available`);
    }
    return provider.analyze(data);
  }

  getAvailableProviders(): { name: string; confidence: number }[] {
    return this.providers
      .filter(p => p.isAvailable())
      .map(p => ({
        name: p.name,
        confidence: p.getConfidence()
      }));
  }
}