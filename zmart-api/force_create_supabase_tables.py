#!/usr/bin/env python3
"""
🔥 FORCE CREATE SUPABASE TABLES - Direct HTTP Approach
Bypasses all limitations and forces table creation using multiple methods
"""

import requests
import json
import time
from typing import Dict, Any

class ForceSupabaseTableCreator:
    def __init__(self):
        self.supabase_url = "https://asjtxrmftmutcsnqgidy.supabase.co"
        
        # Use the service role key provided by user
        self.service_role_key = "sbp_e127bdef496f6c59093093ec9a825a22ac624bd4"
        
        # Also try with anon key as backup
        self.anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzanR4cm1mdG11dGNzbnFnaWR5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1Nzc4NjgsImV4cCI6MjA2NTE1Mzg2OH0.ScIz31CxgxC2Knya-oHtMw5GQ7QL4QUHky-cEUdqpFM"
        
        print(f"🚀 Force Supabase Table Creator")
        print(f"📍 URL: {self.supabase_url}")
        print(f"🔑 Service Role Key: {self.service_role_key}")
    
    def create_headers(self, api_key: str) -> Dict[str, str]:
        """Create headers for API requests"""
        return {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    def test_api_key(self, api_key: str, key_name: str) -> bool:
        """Test if an API key works"""
        try:
            headers = self.create_headers(api_key)
            
            # Try to list tables
            response = requests.get(
                f"{self.supabase_url}/rest/v1/",
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 404]:
                print(f"✅ {key_name} key is valid")
                return True
            else:
                print(f"❌ {key_name} key failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ {key_name} key error: {e}")
            return False
    
    def force_create_table_via_rest(self, sql: str, api_key: str) -> bool:
        """Try to create table via REST API"""
        try:
            headers = self.create_headers(api_key)
            
            # Multiple endpoints to try
            endpoints = [
                f"{self.supabase_url}/rest/v1/rpc/exec",
                f"{self.supabase_url}/database/v1/exec",
                f"{self.supabase_url}/rest/v1/rpc/execute_sql",
                f"{self.supabase_url}/rest/v1/rpc/query"
            ]
            
            for endpoint in endpoints:
                try:
                    # Try different payload formats
                    payloads = [
                        {"sql": sql},
                        {"query": sql},
                        {"statement": sql},
                        {"command": sql}
                    ]
                    
                    for payload in payloads:
                        response = requests.post(
                            endpoint,
                            headers=headers,
                            json=payload,
                            timeout=30
                        )
                        
                        if response.status_code in [200, 201, 204]:
                            print(f"✅ Table created via {endpoint}")
                            return True
                        else:
                            print(f"⚠️ {endpoint} - {payload.keys()} - {response.status_code}: {response.text[:100]}")
                
                except Exception as e:
                    print(f"❌ {endpoint} failed: {e}")
                    continue
            
            return False
            
        except Exception as e:
            print(f"❌ REST API creation failed: {e}")
            return False
    
    def create_simple_table(self) -> bool:
        """Create one simple table to test permissions"""
        sql = """
        CREATE TABLE IF NOT EXISTS trading_analyses (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(20) NOT NULL,
            analysis_type VARCHAR(50) NOT NULL,
            ai_consensus JSONB DEFAULT '{}',
            confidence_score DECIMAL(5,2) DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        print("🧪 Testing table creation with simple table...")
        
        # Test both keys
        keys_to_try = [
            (self.service_role_key, "service_role"),
            (self.anon_key, "anon")
        ]
        
        for api_key, key_name in keys_to_try:
            print(f"\n🔑 Trying with {key_name} key...")
            
            if self.test_api_key(api_key, key_name):
                if self.force_create_table_via_rest(sql, api_key):
                    return True
        
        return False
    
    def create_all_tables(self) -> bool:
        """Create all trading intelligence tables"""
        tables_sql = """
        -- Trading Analyses Table
        CREATE TABLE IF NOT EXISTS trading_analyses (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(20) NOT NULL,
            analysis_type VARCHAR(50) NOT NULL,
            ai_consensus JSONB DEFAULT '{}',
            kingfisher_data JSONB DEFAULT '{}',
            cryptometer_data JSONB DEFAULT '{}',
            binance_data JSONB DEFAULT '{}',
            kucoin_data JSONB DEFAULT '{}',
            coingecko_data JSONB DEFAULT '{}',
            patterns_detected JSONB DEFAULT '[]',
            confidence_score DECIMAL(5,2) DEFAULT 0.0,
            risk_level VARCHAR(20) DEFAULT 'unknown',
            recommendation TEXT DEFAULT '',
            trading_signals JSONB DEFAULT '{}',
            market_conditions JSONB DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Pattern Library Table
        CREATE TABLE IF NOT EXISTS pattern_library (
            id SERIAL PRIMARY KEY,
            pattern_name VARCHAR(100) NOT NULL,
            pattern_type VARCHAR(50) NOT NULL,
            description TEXT DEFAULT '',
            historical_accuracy DECIMAL(5,2) DEFAULT 0.0,
            market_conditions VARCHAR(100) DEFAULT 'any',
            timeframe VARCHAR(20) DEFAULT '1h',
            pattern_data JSONB DEFAULT '{}',
            success_rate DECIMAL(5,2) DEFAULT 0.0,
            usage_count INTEGER DEFAULT 0,
            last_detected TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Smart Alerts Table
        CREATE TABLE IF NOT EXISTS smart_alerts (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(100) DEFAULT 'system',
            symbol VARCHAR(20) NOT NULL,
            alert_type VARCHAR(50) NOT NULL,
            trigger_condition JSONB DEFAULT '{}',
            threshold_value DECIMAL(15,8) DEFAULT 0.0,
            current_value DECIMAL(15,8) DEFAULT 0.0,
            status VARCHAR(20) DEFAULT 'ACTIVE',
            priority VARCHAR(10) DEFAULT 'MEDIUM',
            message TEXT DEFAULT '',
            alert_data JSONB DEFAULT '{}',
            triggered_at TIMESTAMP,
            acknowledged_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Portfolio Analytics Table
        CREATE TABLE IF NOT EXISTS portfolio_analytics (
            id SERIAL PRIMARY KEY,
            portfolio_id VARCHAR(100) NOT NULL,
            total_value DECIMAL(20,8) DEFAULT 0.0,
            daily_pnl DECIMAL(20,8) DEFAULT 0.0,
            weekly_pnl DECIMAL(20,8) DEFAULT 0.0,
            monthly_pnl DECIMAL(20,8) DEFAULT 0.0,
            risk_score DECIMAL(5,2) DEFAULT 0.0,
            diversification_score DECIMAL(5,2) DEFAULT 0.0,
            sharpe_ratio DECIMAL(8,4) DEFAULT 0.0,
            max_drawdown DECIMAL(5,2) DEFAULT 0.0,
            ai_recommendations JSONB DEFAULT '[]',
            optimization_suggestions JSONB DEFAULT '[]',
            performance_metrics JSONB DEFAULT '{}',
            allocation_data JSONB DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Market Sentiment History Table
        CREATE TABLE IF NOT EXISTS market_sentiment_history (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(20) NOT NULL,
            sentiment_score DECIMAL(5,2) DEFAULT 0.0,
            fear_greed_index INTEGER DEFAULT 50,
            social_sentiment JSONB DEFAULT '{}',
            news_sentiment JSONB DEFAULT '{}',
            technical_sentiment JSONB DEFAULT '{}',
            ai_sentiment JSONB DEFAULT '{}',
            overall_sentiment VARCHAR(20) DEFAULT 'NEUTRAL',
            confidence DECIMAL(5,2) DEFAULT 0.0,
            data_sources JSONB DEFAULT '[]',
            volume_24h DECIMAL(20,8) DEFAULT 0.0,
            price_change_24h DECIMAL(10,4) DEFAULT 0.0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- AI Model Performance Table
        CREATE TABLE IF NOT EXISTS ai_model_performance (
            id SERIAL PRIMARY KEY,
            model_name VARCHAR(100) NOT NULL,
            model_type VARCHAR(50) NOT NULL,
            prediction_accuracy DECIMAL(5,2) DEFAULT 0.0,
            total_predictions INTEGER DEFAULT 0,
            correct_predictions INTEGER DEFAULT 0,
            avg_confidence DECIMAL(5,2) DEFAULT 0.0,
            performance_metrics JSONB DEFAULT '{}',
            last_evaluation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Risk Assessments Table
        CREATE TABLE IF NOT EXISTS risk_assessments (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(20) NOT NULL,
            assessment_type VARCHAR(50) NOT NULL,
            risk_level VARCHAR(20) DEFAULT 'MEDIUM',
            risk_score DECIMAL(5,2) DEFAULT 0.0,
            volatility DECIMAL(8,4) DEFAULT 0.0,
            liquidity_risk DECIMAL(5,2) DEFAULT 0.0,
            market_risk DECIMAL(5,2) DEFAULT 0.0,
            correlation_risk DECIMAL(5,2) DEFAULT 0.0,
            risk_factors JSONB DEFAULT '[]',
            recommendations JSONB DEFAULT '[]',
            mitigation_strategies JSONB DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Intelligence Cache Table
        CREATE TABLE IF NOT EXISTS intelligence_cache (
            id SERIAL PRIMARY KEY,
            cache_key VARCHAR(255) NOT NULL UNIQUE,
            cache_data JSONB NOT NULL,
            data_type VARCHAR(50) NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            accessed_count INTEGER DEFAULT 0,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        print("🚀 Creating all trading intelligence tables...")
        
        # Test both keys
        keys_to_try = [
            (self.service_role_key, "service_role"),
            (self.anon_key, "anon")
        ]
        
        for api_key, key_name in keys_to_try:
            print(f"\n🔑 Trying with {key_name} key...")
            
            if self.test_api_key(api_key, key_name):
                if self.force_create_table_via_rest(tables_sql, api_key):
                    return True
        
        return False
    
    def run(self):
        """Main execution"""
        print("🎯 FORCE CREATE SUPABASE TABLES - Starting...")
        
        # First try to create a simple table
        if self.create_simple_table():
            print("✅ Simple table creation successful!")
            
            # Now try all tables
            if self.create_all_tables():
                print("🎉 ALL TRADING INTELLIGENCE TABLES CREATED!")
                return True
        
        print("❌ FAILED - Manual intervention required")
        print("\n📋 Manual Steps:")
        print("1. Go to https://supabase.com/dashboard/project/asjtxrmftmutcsnqgidy/sql")
        print("2. Paste the SQL from ADD_TRADING_TABLES.sql")
        print("3. Click Run")
        return False

if __name__ == "__main__":
    creator = ForceSupabaseTableCreator()
    creator.run()