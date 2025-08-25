#!/usr/bin/env python3
"""
AVAX USDT Comprehensive Analysis with Live Cryptometer API Data
The most advanced cryptocurrency analysis combining multiple data sources
"""

import requests
import time
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import statistics

# API Configuration
API_KEY = "k77U187e08zGf4I3SLz3sYzTEyM2KNoJ9i1N4xg2"
BASE_URL = "https://api.cryptometer.io"
TARGET_SYMBOL = "AVAX-USDT"
TARGET_EXCHANGE = "binance"

class ComprehensiveCryptometerAnalyzer:
    def __init__(self):
        self.api_key = API_KEY
        self.base_url = BASE_URL
        self.symbol = TARGET_SYMBOL
        self.exchange = TARGET_EXCHANGE
        self.all_data = {}
        self.analysis_results = {}
        
    def make_api_request(self, endpoint, params=None):
        """Make API request with proper rate limiting and error handling"""
        if params is None:
            params = {}
        
        params['api_key'] = self.api_key
        
        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=params)
            time.sleep(1.0)  # Rate limiting: 1 request per second
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error {response.status_code} for endpoint {endpoint}")
                return {"success": "false", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            print(f"Exception for endpoint {endpoint}: {str(e)}")
            return {"success": "false", "error": str(e)}
    
    def collect_all_cryptometer_data(self):
        """Collect data from all 18 Cryptometer endpoints"""
        print("Starting Comprehensive AVAX USDT Cryptometer API Collection...")
        print(f"Timestamp: {datetime.now()}")
        print(f"API Key: {self.api_key[:10]}...")
        print(f"Target: {self.symbol} on {self.exchange}")
        print("-" * 60)
        
        # Define all endpoints with their parameters
        endpoints = [
            {
                'name': 'market_list',
                'endpoint': '/coinlist/',
                'params': {'e': self.exchange},
                'description': 'Market List - Available trading pairs'
            },
            {
                'name': 'crypto_info',
                'endpoint': '/cryptocurrency-info/',
                'params': {'e': self.exchange, 'filter': 'defi'},
                'description': 'Cryptocurrency Info - Market data and metrics'
            },
            {
                'name': 'coin_info',
                'endpoint': '/coininfo/',
                'params': {},
                'description': 'Coin Info - Fundamental data'
            },
            {
                'name': 'forex_rates',
                'endpoint': '/forex-rates/',
                'params': {'source': 'USD'},
                'description': 'Forex Rates - Currency conversion rates'
            },
            {
                'name': 'volume_flow',
                'endpoint': '/volume-flow/',
                'params': {'timeframe': '1h'},
                'description': 'Volume Flow - Money flow analysis'
            },
            {
                'name': 'liquidity_lens',
                'endpoint': '/liquidity-lens/',
                'params': {'timeframe': '1h'},
                'description': 'Liquidity Lens - Liquidity analysis'
            },
            {
                'name': 'volatility_index',
                'endpoint': '/volatility-index/',
                'params': {'e': self.exchange, 'timeframe': '1h'},
                'description': 'Volatility Index - Market volatility metrics'
            },
            {
                'name': 'ohlcv',
                'endpoint': '/ohlcv/',
                'params': {'e': self.exchange, 'pair': self.symbol, 'timeframe': '1h'},
                'description': 'OHLCV - Price and volume data'
            },
            {
                'name': 'ls_ratio',
                'endpoint': '/ls-ratio/',
                'params': {'e': 'binance_futures', 'pair': self.symbol, 'timeframe': '1h'},
                'description': 'LS Ratio - Long/Short positioning data'
            },
            {
                'name': 'tickerlist_pro',
                'endpoint': '/tickerlist-pro/',
                'params': {'e': self.exchange},
                'description': 'Tickerlist Pro - Enhanced market data'
            },
            {
                'name': 'merged_volume',
                'endpoint': '/merged-trade-volume/',
                'params': {'symbol': 'AVAX', 'timeframe': '1h', 'exchange_type': 'spot'},
                'description': 'Merged Volume - Buy/Sell volume analysis'
            },
            {
                'name': 'liquidation_data',
                'endpoint': '/liquidation-data-v2/',
                'params': {'symbol': 'avax'},
                'description': 'Liquidation Data - Liquidation metrics'
            },
            {
                'name': 'trend_indicator',
                'endpoint': '/trend-indicator-v3/',
                'params': {},
                'description': 'Trend Indicator - Market trend analysis'
            },
            {
                'name': 'rapid_movements',
                'endpoint': '/rapid-movements/',
                'params': {},
                'description': 'Rapid Movements - Price movement detection'
            },
            {
                'name': 'whale_trades',
                'endpoint': '/xtrades/',
                'params': {'e': self.exchange, 'symbol': 'avax'},
                'description': 'Whale Trades - Large transaction analysis'
            },
            {
                'name': 'large_trades',
                'endpoint': '/large-trades-activity/',
                'params': {'e': self.exchange, 'pair': self.symbol},
                'description': 'Large Trades - Institutional activity'
            },
            {
                'name': 'ai_screener',
                'endpoint': '/ai-screener/',
                'params': {'type': 'full'},
                'description': 'AI Screener - AI-powered market analysis'
            },
            {
                'name': 'ai_screener_analysis',
                'endpoint': '/ai-screener-analysis/',
                'params': {'symbol': 'AVAX'},
                'description': 'AI Analysis - AVAX-specific AI insights'
            }
        ]
        
        # Collect data from each endpoint
        for i, endpoint_config in enumerate(endpoints, 1):
            print(f"{i:2d}. Collecting {endpoint_config['description']}...")
            
            data = self.make_api_request(endpoint_config['endpoint'], endpoint_config['params'])
            self.all_data[endpoint_config['name']] = {
                'data': data,
                'description': endpoint_config['description'],
                'endpoint': endpoint_config['endpoint'],
                'params': endpoint_config['params']
            }
            
            # Check if data was successfully retrieved
            success = data.get('success') == 'true' if isinstance(data, dict) else False
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"    {status} - {endpoint_config['description']}")
        
        print("-" * 60)
        successful_endpoints = sum(1 for data in self.all_data.values() 
                                 if data['data'].get('success') == 'true')
        total_endpoints = len(self.all_data)
        print(f"Data Collection Summary: {successful_endpoints}/{total_endpoints} endpoints successful")
        
        return self.all_data
    
    def extract_comprehensive_metrics(self):
        """Extract and analyze metrics from all successful endpoints"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'symbol': self.symbol,
            'data_sources': [],
            'technical_indicators': {},
            'sentiment_indicators': {},
            'volume_indicators': {},
            'liquidation_indicators': {},
            'ai_indicators': {},
            'trend_indicators': {}
        }
        
        # Process each endpoint data
        for endpoint_name, endpoint_info in self.all_data.items():
            data = endpoint_info['data']
            
            if data.get('success') == 'true':
                metrics['data_sources'].append({
                    'name': endpoint_name,
                    'description': endpoint_info['description'],
                    'status': 'active'
                })
                
                # Extract specific metrics based on endpoint
                if endpoint_name == 'trend_indicator':
                    trend_data = data.get('data', [])
                    if trend_data:
                        avax_trend = None
                        for item in trend_data:
                            if 'AVAX' in item.get('symbol', '').upper():
                                avax_trend = item
                                break
                        
                        if avax_trend:
                            metrics['trend_indicators'] = {
                                'trend_score': float(avax_trend.get('trend_score', 50)),
                                'buy_pressure': float(avax_trend.get('buy_pressure', 50)),
                                'sell_pressure': float(avax_trend.get('sell_pressure', 50)),
                                'momentum': float(avax_trend.get('momentum', 50))
                            }
                
                elif endpoint_name == 'ls_ratio':
                    ls_data = data.get('data', [])
                    if ls_data:
                        latest_ls = ls_data[0]
                        metrics['sentiment_indicators']['ls_ratio'] = {
                            'ratio': float(latest_ls.get('ratio', 0.5)),
                            'long_percentage': float(latest_ls.get('buy', 50)),
                            'short_percentage': float(latest_ls.get('sell', 50)),
                            'timestamp': latest_ls.get('timestamp')
                        }
                
                elif endpoint_name == 'volume_flow':
                    volume_data = data.get('data', {})
                    inflow = volume_data.get('inflow', [])
                    outflow = volume_data.get('outflow', [])
                    
                    if inflow and outflow:
                        total_inflow = sum([float(item.get('volume', 0)) for item in inflow[:10]])
                        total_outflow = sum([float(item.get('volume', 0)) for item in outflow[:10]])
                        net_flow = total_inflow - total_outflow
                        
                        metrics['volume_indicators']['flow_analysis'] = {
                            'total_inflow': total_inflow,
                            'total_outflow': total_outflow,
                            'net_flow': net_flow,
                            'flow_ratio': total_inflow / total_outflow if total_outflow > 0 else 0
                        }
                
                elif endpoint_name == 'liquidity_lens':
                    liquidity_data = data.get('data', {})
                    avax_liquidity = liquidity_data.get('AVAX', {})
                    
                    if avax_liquidity:
                        metrics['volume_indicators']['liquidity_analysis'] = {
                            'avax_inflow': float(avax_liquidity.get('inflow', 0)),
                            'avax_outflow': float(avax_liquidity.get('outflow', 0)),
                            'avax_netflow': float(avax_liquidity.get('netflow', 0))
                        }
                
                elif endpoint_name == 'liquidation_data':
                    liq_data = data.get('data', [])
                    if liq_data and isinstance(liq_data, list) and len(liq_data) > 0:
                        total_longs = 0
                        total_shorts = 0
                        exchanges = []
                        
                        for exchange_data in liq_data[0].values():
                            if isinstance(exchange_data, dict):
                                longs = float(exchange_data.get('longs', 0))
                                shorts = float(exchange_data.get('shorts', 0))
                                total_longs += longs
                                total_shorts += shorts
                                if longs > 0 or shorts > 0:
                                    exchanges.append({
                                        'longs': longs,
                                        'shorts': shorts,
                                        'ratio': longs / shorts if shorts > 0 else float('inf')
                                    })
                        
                        metrics['liquidation_indicators'] = {
                            'total_long_liquidations': total_longs,
                            'total_short_liquidations': total_shorts,
                            'liquidation_ratio': total_longs / total_shorts if total_shorts > 0 else float('inf'),
                            'exchanges_count': len(exchanges)
                        }
                
                elif endpoint_name == 'ai_screener':
                    ai_data = data.get('data', [])
                    avax_ai_data = [item for item in ai_data if 'AVAX' in item.get('symbol', '')]
                    
                    if avax_ai_data:
                        ai_item = avax_ai_data[0]
                        metrics['ai_indicators']['screener'] = {
                            'ai_score': float(ai_item.get('pnl', 0)),
                            'symbol': ai_item.get('symbol'),
                            'recommendation': ai_item.get('recommendation', 'neutral')
                        }
                
                elif endpoint_name == 'ai_screener_analysis':
                    ai_analysis = data.get('data', {})
                    if ai_analysis:
                        metrics['ai_indicators']['analysis'] = {
                            'sentiment_score': ai_analysis.get('sentiment_score', 50),
                            'technical_score': ai_analysis.get('technical_score', 50),
                            'fundamental_score': ai_analysis.get('fundamental_score', 50)
                        }
                
                elif endpoint_name == 'volatility_index':
                    vol_data = data.get('data', [])
                    avax_vol = [item for item in vol_data if 'AVAX' in item.get('symbol', '')]
                    
                    if avax_vol:
                        vol_item = avax_vol[0]
                        metrics['technical_indicators']['volatility'] = {
                            'volatility_index': float(vol_item.get('volatility', 50)),
                            'volatility_rank': vol_item.get('rank', 'unknown')
                        }
                
                elif endpoint_name == 'large_trades':
                    trades_data = data.get('data', [])
                    if trades_data:
                        buy_volume = sum([float(t.get('total', 0)) for t in trades_data if t.get('side') == 'BUY'])
                        sell_volume = sum([float(t.get('total', 0)) for t in trades_data if t.get('side') == 'SELL'])
                        
                        metrics['volume_indicators']['large_trades'] = {
                            'buy_volume': buy_volume,
                            'sell_volume': sell_volume,
                            'buy_sell_ratio': buy_volume / sell_volume if sell_volume > 0 else 0,
                            'total_trades': len(trades_data)
                        }
                
                elif endpoint_name == 'whale_trades':
                    whale_data = data.get('data', [])
                    if whale_data:
                        metrics['volume_indicators']['whale_activity'] = {
                            'whale_trades_count': len(whale_data),
                            'whale_activity_score': min(100, len(whale_data) * 5)  # Scale whale activity
                        }
        
        return metrics
    
    def calculate_advanced_composite_scores(self, metrics):
        """Calculate advanced composite scores using all available data"""
        scores = {
            'methodology': 'Advanced Multi-Source Composite Scoring',
            'data_sources_used': len(metrics['data_sources']),
            'components': {},
            'final_scores': {}
        }
        
        # Technical Analysis Component (Weight: 30%)
        technical_factors = []
        
        if 'volatility' in metrics['technical_indicators']:
            vol_score = metrics['technical_indicators']['volatility']['volatility_index']
            # Moderate volatility is optimal for trading
            if 30 <= vol_score <= 70:
                technical_factors.append(vol_score)
            else:
                technical_factors.append(50)  # Neutral for extreme volatility
        
        # Add trend indicators if available
        if metrics['trend_indicators']:
            trend_score = metrics['trend_indicators'].get('trend_score', 50)
            buy_pressure = metrics['trend_indicators'].get('buy_pressure', 50)
            sell_pressure = metrics['trend_indicators'].get('sell_pressure', 50)
            
            technical_factors.extend([trend_score, buy_pressure, 100 - sell_pressure])
        
        technical_score = np.mean(technical_factors) if technical_factors else 50
        scores['components']['technical_analysis'] = {
            'score': technical_score,
            'factors_count': len(technical_factors),
            'weight': 0.30
        }
        
        # Sentiment Analysis Component (Weight: 25%)
        sentiment_factors = []
        
        if 'ls_ratio' in metrics['sentiment_indicators']:
            ls_data = metrics['sentiment_indicators']['ls_ratio']
            long_pct = ls_data['long_percentage']
            
            # Contrarian sentiment analysis
            if long_pct > 75:  # Extreme long positioning
                sentiment_factors.append(30)  # Bearish contrarian signal
            elif long_pct < 25:  # Extreme short positioning
                sentiment_factors.append(70)  # Bullish contrarian signal
            else:
                sentiment_factors.append(50 + (long_pct - 50) * 0.5)  # Moderate adjustment
        
        # Add AI sentiment if available
        if 'analysis' in metrics['ai_indicators']:
            ai_sentiment = metrics['ai_indicators']['analysis'].get('sentiment_score', 50)
            sentiment_factors.append(ai_sentiment)
        
        sentiment_score = np.mean(sentiment_factors) if sentiment_factors else 50
        scores['components']['sentiment_analysis'] = {
            'score': sentiment_score,
            'factors_count': len(sentiment_factors),
            'weight': 0.25
        }
        
        # Volume Analysis Component (Weight: 25%)
        volume_factors = []
        
        if 'flow_analysis' in metrics['volume_indicators']:
            flow_data = metrics['volume_indicators']['flow_analysis']
            net_flow = flow_data['net_flow']
            flow_ratio = flow_data['flow_ratio']
            
            # Positive net flow is bullish
            if net_flow > 0:
                flow_score = min(75, 50 + (net_flow / 1000000) * 10)  # Scale by millions
            else:
                flow_score = max(25, 50 + (net_flow / 1000000) * 10)
            
            volume_factors.append(flow_score)
        
        if 'liquidity_analysis' in metrics['volume_indicators']:
            avax_netflow = metrics['volume_indicators']['liquidity_analysis']['avax_netflow']
            if avax_netflow > 0:
                liquidity_score = min(75, 50 + abs(avax_netflow) / 100000 * 10)
            else:
                liquidity_score = max(25, 50 - abs(avax_netflow) / 100000 * 10)
            
            volume_factors.append(liquidity_score)
        
        if 'large_trades' in metrics['volume_indicators']:
            buy_sell_ratio = metrics['volume_indicators']['large_trades']['buy_sell_ratio']
            if buy_sell_ratio > 1:
                large_trade_score = min(75, 50 + (buy_sell_ratio - 1) * 25)
            else:
                large_trade_score = max(25, 50 - (1 - buy_sell_ratio) * 25)
            
            volume_factors.append(large_trade_score)
        
        volume_score = np.mean(volume_factors) if volume_factors else 50
        scores['components']['volume_analysis'] = {
            'score': volume_score,
            'factors_count': len(volume_factors),
            'weight': 0.25
        }
        
        # Liquidation Analysis Component (Weight: 20%)
        liquidation_factors = []
        
        if metrics['liquidation_indicators']:
            liq_data = metrics['liquidation_indicators']
            total_longs = liq_data['total_long_liquidations']
            total_shorts = liq_data['total_short_liquidations']
            
            if total_longs + total_shorts > 0:
                long_liq_pct = total_longs / (total_longs + total_shorts) * 100
                
                # Heavy long liquidations can indicate oversold conditions
                if long_liq_pct > 80:
                    liquidation_factors.append(65)  # Potential bounce
                elif long_liq_pct < 20:
                    liquidation_factors.append(35)  # Potential decline
                else:
                    liquidation_factors.append(50)
        
        liquidation_score = np.mean(liquidation_factors) if liquidation_factors else 50
        scores['components']['liquidation_analysis'] = {
            'score': liquidation_score,
            'factors_count': len(liquidation_factors),
            'weight': 0.20
        }
        
        # Calculate weighted composite scores
        weights = {
            'technical_analysis': 0.30,
            'sentiment_analysis': 0.25,
            'volume_analysis': 0.25,
            'liquidation_analysis': 0.20
        }
        
        # Long position score
        long_score = sum([
            scores['components'][component]['score'] * weights[component]
            for component in weights.keys()
        ])
        
        # Short position score (inverse some components)
        short_technical = 100 - scores['components']['technical_analysis']['score']
        short_sentiment = scores['components']['sentiment_analysis']['score'] * 0.8  # Sentiment less impactful for shorts
        short_volume = 100 - scores['components']['volume_analysis']['score']
        short_liquidation = 100 - scores['components']['liquidation_analysis']['score']
        
        short_score = (
            short_technical * weights['technical_analysis'] +
            short_sentiment * weights['sentiment_analysis'] +
            short_volume * weights['volume_analysis'] +
            short_liquidation * weights['liquidation_analysis']
        )
        
        scores['final_scores'] = {
            'long_score': max(20, min(80, long_score)),
            'short_score': max(20, min(80, short_score)),
            'confidence_level': min(len(metrics['data_sources']) / 18 * 100, 100)
        }
        
        return scores
    
    def calculate_enhanced_win_rates(self, composite_scores, metrics):
        """Calculate enhanced win rates using comprehensive data"""
        
        def advanced_score_to_win_rate(score, timeframe, position, confidence):
            """Advanced win rate calculation with confidence adjustment"""
            # Base conversion with AVAX-specific characteristics
            base_rate = score * 0.85  # AVAX range-bound nature
            
            # Confidence adjustment
            confidence_factor = 0.8 + (confidence / 100) * 0.4  # 0.8 to 1.2 range
            
            # Timeframe adjustments
            timeframe_factors = {
                '24-48h': 0.85,  # Higher uncertainty short-term
                '7d': 1.0,       # Balanced
                '1m': 1.15       # More predictable long-term
            }
            
            # Position-specific adjustments for AVAX
            if position == 'long':
                # AVAX has shown resilience and growth potential
                position_factor = 1.05 if timeframe == '1m' else 1.0
            else:  # short
                # Range-bound nature makes shorts challenging long-term
                position_factor = 0.95 if timeframe == '1m' else 1.0
            
            # Data quality adjustment
            data_sources_count = len(metrics['data_sources'])
            data_quality_factor = 0.9 + (data_sources_count / 18) * 0.2  # 0.9 to 1.1 range
            
            # Calculate final win rate
            win_rate = (base_rate * confidence_factor * 
                       timeframe_factors[timeframe] * 
                       position_factor * data_quality_factor)
            
            # Cap between realistic bounds
            return max(25, min(85, win_rate))
        
        confidence = composite_scores['final_scores']['confidence_level']
        long_score = composite_scores['final_scores']['long_score']
        short_score = composite_scores['final_scores']['short_score']
        
        win_rates = {
            'methodology': 'Enhanced Multi-Factor Win Rate Calculation',
            'confidence_level': confidence,
            'data_quality_score': len(metrics['data_sources']) / 18 * 100,
            'timeframes': {
                '24-48h': {
                    'long': advanced_score_to_win_rate(long_score, '24-48h', 'long', confidence),
                    'short': advanced_score_to_win_rate(short_score, '24-48h', 'short', confidence)
                },
                '7d': {
                    'long': advanced_score_to_win_rate(long_score, '7d', 'long', confidence),
                    'short': advanced_score_to_win_rate(short_score, '7d', 'short', confidence)
                },
                '1m': {
                    'long': advanced_score_to_win_rate(long_score, '1m', 'long', confidence),
                    'short': advanced_score_to_win_rate(short_score, '1m', 'short', confidence)
                }
            }
        }
        
        return win_rates
    
    def generate_comprehensive_analysis(self):
        """Generate the most comprehensive analysis possible"""
        print("\n" + "="*60)
        print("GENERATING COMPREHENSIVE ANALYSIS")
        print("="*60)
        
        # Step 1: Collect all Cryptometer data
        print("Step 1: Collecting live Cryptometer API data...")
        cryptometer_data = self.collect_all_cryptometer_data()
        
        # Step 2: Extract comprehensive metrics
        print("\nStep 2: Extracting comprehensive metrics...")
        metrics = self.extract_comprehensive_metrics()
        
        # Step 3: Calculate advanced composite scores
        print("Step 3: Calculating advanced composite scores...")
        composite_scores = self.calculate_advanced_composite_scores(metrics)
        
        # Step 4: Calculate enhanced win rates
        print("Step 4: Calculating enhanced win rates...")
        win_rates = self.calculate_enhanced_win_rates(composite_scores, metrics)
        
        # Step 5: Compile comprehensive analysis
        analysis = {
            'analysis_metadata': {
                'timestamp': datetime.now().isoformat(),
                'symbol': self.symbol,
                'analysis_type': 'Comprehensive Multi-Source Professional Analysis',
                'data_sources_count': len(metrics['data_sources']),
                'api_endpoints_used': [source['name'] for source in metrics['data_sources']],
                'confidence_level': composite_scores['final_scores']['confidence_level']
            },
            'raw_cryptometer_data': cryptometer_data,
            'extracted_metrics': metrics,
            'composite_scores': composite_scores,
            'win_rates': win_rates,
            'data_source_summary': {
                'cryptometer_endpoints': len([s for s in metrics['data_sources'] if s['status'] == 'active']),
                'total_endpoints_attempted': 18,
                'success_rate': len(metrics['data_sources']) / 18 * 100
            }
        }
        
        return analysis

def main():
    """Main execution function"""
    print("Starting Most Comprehensive AVAX USDT Analysis...")
    print("Using Live Cryptometer API + Advanced Analytics")
    print("="*60)
    
    # Initialize analyzer
    analyzer = ComprehensiveCryptometerAnalyzer()
    
    # Generate comprehensive analysis
    analysis = analyzer.generate_comprehensive_analysis()
    
    # Save complete results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"/home/ubuntu/avax_comprehensive_analysis_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    
    print(f"\n" + "="*60)
    print("COMPREHENSIVE ANALYSIS COMPLETED")
    print("="*60)
    print(f"Results saved to: {results_file}")
    
    # Display key results
    print(f"\nDATA COLLECTION SUMMARY:")
    print(f"Cryptometer Endpoints: {analysis['data_source_summary']['cryptometer_endpoints']}/18")
    print(f"Success Rate: {analysis['data_source_summary']['success_rate']:.1f}%")
    print(f"Confidence Level: {analysis['analysis_metadata']['confidence_level']:.1f}%")
    
    print(f"\nCOMPOSITE SCORES:")
    print(f"Long Position Score:  {analysis['composite_scores']['final_scores']['long_score']:.1f}/100")
    print(f"Short Position Score: {analysis['composite_scores']['final_scores']['short_score']:.1f}/100")
    
    print(f"\nENHANCED WIN RATES:")
    for timeframe, rates in analysis['win_rates']['timeframes'].items():
        print(f"{timeframe.upper()}:")
        print(f"  Long:  {rates['long']:.1f}% win rate")
        print(f"  Short: {rates['short']:.1f}% win rate")
    
    print(f"\nACTIVE DATA SOURCES:")
    for source in analysis['extracted_metrics']['data_sources']:
        print(f"  ✅ {source['description']}")
    
    return analysis, results_file

if __name__ == "__main__":
    final_analysis, results_file = main()

