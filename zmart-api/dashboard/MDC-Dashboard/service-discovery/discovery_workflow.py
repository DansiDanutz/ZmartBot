#!/usr/bin/env python3
"""
Comprehensive AI Service Discovery Workflow System
- Every 5 minutes: Generate connection analysis between 2 MDC files
- Every hour: Select best of 12 analyses and store as winner
- Every 4 hours: Aggregate all non-winner data for deep analysis
- Daily: 30 discoveries (24 hourly + 6 four-hourly)
"""

import os
import sys
import json
import time
import sqlite3
import requests
import schedule
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConnectionAnalysis:
    id: int
    timestamp: datetime
    service_a: str
    service_b: str
    mdc_content_a: str
    mdc_content_b: str
    ai_analysis: str
    quality_score: float
    is_winner: bool = False
    is_aggregated: bool = False

@dataclass  
class DailyDiscoveryCard:
    date: str
    hourly_winners: List[ConnectionAnalysis]
    four_hour_aggregations: List[Dict[str, Any]]
    total_discoveries: int = 30

class DiscoveryWorkflowDB:
    """Database manager for the discovery workflow"""
    
    def __init__(self, db_path: str = "discovery_workflow.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Connection analyses table (every 5 minutes)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS connection_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            service_a TEXT NOT NULL,
            service_b TEXT NOT NULL,
            mdc_content_a TEXT NOT NULL,
            mdc_content_b TEXT NOT NULL,
            ai_analysis TEXT NOT NULL,
            quality_score REAL DEFAULT 0.0,
            is_winner BOOLEAN DEFAULT FALSE,
            is_aggregated BOOLEAN DEFAULT FALSE
        )
        ''')
        
        # Hourly winners table (best of 12 every hour)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS hourly_winners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            analysis_id INTEGER,
            winner_reason TEXT,
            FOREIGN KEY (analysis_id) REFERENCES connection_analyses (id)
        )
        ''')
        
        # Four-hour aggregations table (every 4 hours)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS four_hour_aggregations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            analysis_period_start DATETIME,
            analysis_period_end DATETIME,
            aggregated_data TEXT,
            ai_summary TEXT,
            insights_count INTEGER DEFAULT 0
        )
        ''')
        
        # Daily cards table (summary per day)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,
            hourly_winners_count INTEGER DEFAULT 0,
            four_hour_aggregations_count INTEGER DEFAULT 0,
            total_discoveries INTEGER DEFAULT 30,
            card_data TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("📊 Discovery workflow database initialized")
    
    def store_analysis(self, analysis: ConnectionAnalysis) -> int:
        """Store a connection analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO connection_analyses (
            service_a, service_b, mdc_content_a, mdc_content_b, 
            ai_analysis, quality_score, is_winner, is_aggregated
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis.service_a, analysis.service_b,
            analysis.mdc_content_a, analysis.mdc_content_b,
            analysis.ai_analysis, analysis.quality_score,
            analysis.is_winner, analysis.is_aggregated
        ))
        
        analysis_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return analysis_id
    
    def get_last_n_analyses(self, n: int = 12) -> List[ConnectionAnalysis]:
        """Get last N analyses for selection"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, timestamp, service_a, service_b, mdc_content_a, mdc_content_b,
               ai_analysis, quality_score, is_winner, is_aggregated
        FROM connection_analyses
        WHERE is_winner = FALSE
        ORDER BY timestamp DESC
        LIMIT ?
        ''', (n,))
        
        analyses = []
        for row in cursor.fetchall():
            analyses.append(ConnectionAnalysis(
                id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                service_a=row[2],
                service_b=row[3],
                mdc_content_a=row[4],
                mdc_content_b=row[5],
                ai_analysis=row[6],
                quality_score=row[7],
                is_winner=bool(row[8]),
                is_aggregated=bool(row[9])
            ))
        
        conn.close()
        return analyses
    
    def mark_as_winner(self, analysis_id: int, reason: str):
        """Mark an analysis as winner"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE connection_analyses SET is_winner = TRUE WHERE id = ?', (analysis_id,))
        cursor.execute('INSERT INTO hourly_winners (analysis_id, winner_reason) VALUES (?, ?)', (analysis_id, reason))
        
        conn.commit()
        conn.close()
    
    def get_non_winner_analyses_since(self, since: datetime) -> List[ConnectionAnalysis]:
        """Get non-winner analyses since a specific time"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, timestamp, service_a, service_b, mdc_content_a, mdc_content_b,
               ai_analysis, quality_score, is_winner, is_aggregated
        FROM connection_analyses
        WHERE is_winner = FALSE AND is_aggregated = FALSE AND timestamp >= ?
        ORDER BY timestamp DESC
        ''', (since.isoformat(),))
        
        analyses = []
        for row in cursor.fetchall():
            analyses.append(ConnectionAnalysis(
                id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                service_a=row[2],
                service_b=row[3],
                mdc_content_a=row[4],
                mdc_content_b=row[5],
                ai_analysis=row[6],
                quality_score=row[7],
                is_winner=bool(row[8]),
                is_aggregated=bool(row[9])
            ))
        
        conn.close()
        return analyses

class AIDiscoveryWorkflow:
    """Main workflow orchestrator"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path("/Users/dansidanutz/Desktop/ZmartBot")
        self.mdc_dir = self.project_root / ".cursor" / "rules"
        self.db = DiscoveryWorkflowDB()
        
        # OpenAI configuration
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.warning("⚠️ OPENAI_API_KEY not found. Using fallback mode.")
        
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-4"
        
        # Workflow state
        self.mdc_files_cache = {}
        self.last_analysis_time = None
        
        logger.info("🤖 AI Discovery Workflow initialized")
    
    def load_mdc_files(self) -> Dict[str, str]:
        """Load all MDC files for analysis"""
        mdc_files = {}
        
        try:
            for mdc_file in self.mdc_dir.glob("*.mdc"):
                if "Auto-generated" not in mdc_file.name:
                    with open(mdc_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    mdc_files[mdc_file.stem] = content
            
            self.mdc_files_cache = mdc_files
            logger.info(f"📄 Loaded {len(mdc_files)} MDC files")
            
        except Exception as e:
            logger.error(f"❌ Error loading MDC files: {e}")
        
        return mdc_files
    
    def classify_service_type(self, service_name: str, content: str) -> str:
        """Classify service based on MDC content and naming patterns"""
        service_lower = service_name.lower()
        content_lower = content.lower()
        
        # Database services
        if 'database' in service_lower or 'db' in service_lower or 'storage' in content_lower:
            return 'database'
        
        # API/Backend services 
        if 'api' in service_lower or 'backend' in service_lower or 'fastapi' in content_lower or 'flask' in content_lower:
            return 'api'
        
        # Alert/Notification services
        if 'alert' in service_lower or 'notification' in content_lower or 'webhook' in content_lower:
            return 'alert'
        
        # Dashboard/UI services
        if 'dashboard' in service_lower or 'ui' in service_lower or 'frontend' in content_lower:
            return 'frontend'
        
        # Monitoring/Doctor services
        if 'doctor' in service_lower or 'monitor' in service_lower or 'health' in content_lower:
            return 'monitoring'
        
        # Orchestration services
        if 'orchestration' in service_lower or 'master' in service_lower or 'coordinator' in content_lower:
            return 'orchestration'
        
        # Data processing services
        if 'processor' in service_lower or 'worker' in service_lower or 'analyzer' in content_lower:
            return 'processor'
        
        # Trading/Financial services
        if 'trading' in service_lower or 'symbol' in service_lower or 'market' in content_lower:
            return 'trading'
        
        return 'general'
    
    def get_compatibility_score(self, type1: str, type2: str) -> float:
        """Calculate compatibility score between two service types"""
        # Compatibility matrix - higher scores mean better complementary services
        compatibility_matrix = {
            ('api', 'database'): 9.5,
            ('api', 'monitoring'): 8.5,
            ('trading', 'database'): 9.0,
            ('trading', 'alert'): 8.8,
            ('frontend', 'api'): 9.2,
            ('orchestration', 'monitoring'): 9.0,
            ('processor', 'database'): 8.5,
            ('alert', 'monitoring'): 8.0,
            ('orchestration', 'api'): 8.5,
            ('trading', 'processor'): 8.7,
            ('frontend', 'monitoring'): 7.5,
            ('database', 'monitoring'): 8.2,
            ('api', 'alert'): 8.0,
            ('processor', 'alert'): 7.8,
            ('orchestration', 'database'): 8.3
        }
        
        # Check both directions
        score = compatibility_matrix.get((type1, type2), 0.0)
        if score == 0.0:
            score = compatibility_matrix.get((type2, type1), 6.0)  # Default medium compatibility
        
        return score
    
    def get_or_create_combination(self, service1: str, service2: str) -> int:
        """Get or create service combination in database with usage tracking"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Add service_combinations table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS service_combinations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service1 TEXT NOT NULL,
                service2 TEXT NOT NULL,
                combination_type TEXT NOT NULL,
                compatibility_score REAL DEFAULT 0.0,
                used_count INTEGER DEFAULT 0,
                last_used DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(service1, service2)
            )
        ''')
        
        # Ensure consistent ordering (alphabetical)
        if service1 > service2:
            service1, service2 = service2, service1
        
        # Check if combination exists
        cursor.execute('''
            SELECT id, used_count FROM service_combinations 
            WHERE service1 = ? AND service2 = ?
        ''', (service1, service2))
        
        result = cursor.fetchone()
        if result:
            combination_id, used_count = result
            # Update usage count and timestamp
            cursor.execute('''
                UPDATE service_combinations 
                SET used_count = ?, last_used = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (used_count + 1, combination_id))
        else:
            # Create new combination
            content1 = self.mdc_files_cache.get(service1, '')
            content2 = self.mdc_files_cache.get(service2, '')
            
            type1 = self.classify_service_type(service1, content1)
            type2 = self.classify_service_type(service2, content2)
            compatibility_score = self.get_compatibility_score(type1, type2)
            
            cursor.execute('''
                INSERT INTO service_combinations (
                    service1, service2, combination_type, compatibility_score, used_count, last_used
                ) VALUES (?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
            ''', (service1, service2, f"{type1}+{type2}", compatibility_score))
            
            combination_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return combination_id
    
    def select_connection_pair(self) -> Tuple[str, str, str, str, int]:
        """Select two complementary MDC files for analysis avoiding overused combinations"""
        if not self.mdc_files_cache:
            self.load_mdc_files()
        
        # Get all services with their types and connection counts
        services_info = []
        for name, content in self.mdc_files_cache.items():
            if 'Auto-generated' not in name:  # Skip auto-generated files
                connection_count = (content.count('✅') + content.count('⏳') + content.count('🔥'))
                service_type = self.classify_service_type(name, content)
                services_info.append((name, content, connection_count, service_type))
        
        if len(services_info) < 2:
            raise Exception("Not enough valid MDC files for analysis")
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Ensure table exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS service_combinations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service1 TEXT NOT NULL,
                service2 TEXT NOT NULL,
                combination_type TEXT NOT NULL,
                compatibility_score REAL DEFAULT 0.0,
                used_count INTEGER DEFAULT 0,
                last_used DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(service1, service2)
            )
        ''')
        
        # Find the least used, most compatible combination
        best_combination = None
        best_score = 0
        
        for i, (name1, content1, conn1, type1) in enumerate(services_info):
            for name2, content2, conn2, type2 in services_info[i+1:]:
                # Calculate selection score
                compatibility = self.get_compatibility_score(type1, type2)
                connection_potential = (conn1 + conn2) * 0.1  # Bonus for services with connections
                
                # Check usage count (prefer less used combinations)
                service_a, service_b = (name1, name2) if name1 < name2 else (name2, name1)
                cursor.execute('''
                    SELECT used_count FROM service_combinations 
                    WHERE service1 = ? AND service2 = ?
                ''', (service_a, service_b))
                
                result = cursor.fetchone()
                usage_penalty = (result[0] * 2) if result else 0  # Penalty for overuse
                
                # Calculate final score
                final_score = compatibility + connection_potential - usage_penalty
                
                if final_score > best_score:
                    best_score = final_score
                    best_combination = (name1, content1, name2, content2, type1, type2)
        
        conn.close()
        
        if not best_combination:
            # Fallback to first two services
            name1, content1, _, type1 = services_info[0]
            name2, content2, _, type2 = services_info[1]
            best_combination = (name1, content1, name2, content2, type1, type2)
        
        # Get or create combination ID
        combination_id = self.get_or_create_combination(best_combination[0], best_combination[2])
        
        logger.info(f"🎯 Selected combination: {best_combination[0]} ↔ {best_combination[2]} ({best_combination[4]}+{best_combination[5]}, score: {best_score:.2f})")
        
        return best_combination[0], best_combination[1], best_combination[2], best_combination[3], combination_id
    
    def analyze_connection_pair(self, service_a: str, content_a: str, service_b: str, content_b: str) -> str:
        """Send connection pair to ChatGPT for analysis"""
        if not self.api_key:
            return self._fallback_analysis(service_a, service_b)
        
        try:
            prompt = f"""
Analyze the connection potential between these two ZmartBot services and provide implementation recommendations:

=== SERVICE A: {service_a} ===
{content_a[:2000]}...

=== SERVICE B: {service_b} ===
{content_b[:2000]}...

=== ANALYSIS REQUEST ===
1. **Connection Potential**: Rate 1-10 how beneficial connecting these services would be
2. **Implementation Strategy**: Specific steps to implement the connection
3. **Benefits**: What improvements this connection would bring to the system
4. **Technical Requirements**: What needs to be built/configured
5. **Priority Level**: High/Medium/Low based on impact vs effort
6. **Risk Assessment**: Potential challenges or risks

Provide a structured response with actionable implementation details.
"""
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are a expert system architect providing detailed implementation guidance for microservices connections in a cryptocurrency trading platform."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 1500,
                "temperature": 0.8
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            logger.error(f"❌ ChatGPT analysis error: {e}")
            return self._fallback_analysis(service_a, service_b)
    
    def _fallback_analysis(self, service_a: str, service_b: str) -> str:
        """Fallback analysis when ChatGPT is unavailable"""
        return f"""
**Connection Analysis: {service_a} ↔ {service_b}**

**Connection Potential**: 7/10
These services show good potential for integration based on their architectural patterns.

**Implementation Strategy**:
1. Create API endpoint bridge between services
2. Implement shared data models for communication
3. Add error handling and retry logic
4. Configure service discovery registration

**Benefits**:
- Improved data flow between services
- Reduced redundancy in processing
- Better system integration and monitoring

**Technical Requirements**:
- REST API endpoints for communication
- Shared configuration management
- Health check integration
- Logging and monitoring setup

**Priority Level**: Medium
Good potential benefits with moderate implementation effort.

**Risk Assessment**: Low
Standard microservices integration patterns with well-established practices.

*Note: This is a fallback analysis. Enable ChatGPT API for detailed AI-powered insights.*
"""
    
    def calculate_quality_score(self, analysis: str) -> float:
        """Calculate quality score for an analysis"""
        score = 0.0
        
        # Length and detail score (up to 3 points)
        if len(analysis) > 500:
            score += min(len(analysis) / 1000, 3.0)
        
        # Keyword presence (up to 4 points)
        keywords = ['implementation', 'strategy', 'benefits', 'technical', 'priority', 'risk']
        for keyword in keywords:
            if keyword.lower() in analysis.lower():
                score += 0.7
        
        # Structure indicators (up to 3 points)
        if '**' in analysis:  # Formatted sections
            score += 1.0
        if any(str(i) in analysis for i in range(1, 11)):  # Rating present
            score += 1.0
        if 'High' in analysis or 'Medium' in analysis or 'Low' in analysis:  # Priority present
            score += 1.0
        
        return min(score, 10.0)
    
    # Scheduled Tasks
    def five_minute_analysis(self):
        """Every 5 minutes: Generate connection analysis with combination tracking"""
        try:
            logger.info("🔄 Running 5-minute connection analysis...")
            
            # Select connection pair with combination tracking
            service_a, content_a, service_b, content_b, combination_id = self.select_connection_pair()
            
            # Generate analysis
            analysis_text = self.analyze_connection_pair(service_a, content_a, service_b, content_b)
            quality_score = self.calculate_quality_score(analysis_text)
            
            # Store in database with combination_id
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO connection_analyses (
                service_a, service_b, mdc_content_a, mdc_content_b, 
                ai_analysis, quality_score, is_winner, is_aggregated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                service_a, service_b,
                content_a[:1000],  # Truncate for storage
                content_b[:1000],
                analysis_text, 
                quality_score,
                False,  # is_winner
                False   # is_aggregated
            ))
            
            analysis_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Stored analysis {analysis_id}: {service_a}↔{service_b} (combination #{combination_id}, score: {quality_score:.2f})")
            
        except Exception as e:
            logger.error(f"❌ 5-minute analysis error: {e}")
    
    def hourly_winner_selection(self):
        """Every hour: Select best of last 12 analyses"""
        try:
            logger.info("🏆 Running hourly winner selection...")
            
            # Get last 12 analyses
            analyses = self.db.get_last_n_analyses(12)
            
            if not analyses:
                logger.warning("⚠️ No analyses found for winner selection")
                return
            
            if len(analyses) == 1:
                # Only one analysis, make it the winner
                winner = analyses[0]
                reason = "Only analysis available in this period"
            else:
                # Select winner using ChatGPT or fallback method
                winner = self.select_best_analysis(analyses)
                reason = f"Best of {len(analyses)} analyses based on quality and implementation potential"
            
            # Mark as winner
            self.db.mark_as_winner(winner.id, reason)
            logger.info(f"🏆 Winner selected: Analysis {winner.id} ({winner.service_a}↔{winner.service_b})")
            
        except Exception as e:
            logger.error(f"❌ Hourly winner selection error: {e}")
    
    def select_best_analysis(self, analyses: List[ConnectionAnalysis]) -> ConnectionAnalysis:
        """Select the best analysis from a list"""
        if not self.api_key:
            # Fallback: Select by highest quality score
            return max(analyses, key=lambda a: a.quality_score)
        
        try:
            # Prepare analyses for ChatGPT evaluation
            analyses_text = ""
            for i, analysis in enumerate(analyses, 1):
                analyses_text += f"\n=== ANALYSIS {i} ===\n"
                analyses_text += f"Services: {analysis.service_a} ↔ {analysis.service_b}\n"
                analyses_text += f"Quality Score: {analysis.quality_score:.2f}\n"
                analyses_text += f"Analysis: {analysis.ai_analysis[:500]}...\n"
            
            prompt = f"""
Select the BEST analysis from these {len(analyses)} connection analyses based on:
1. Implementation feasibility
2. System impact potential
3. Technical clarity
4. Business value

{analyses_text}

Respond with just the number (1-{len(analyses)}) of the best analysis and a brief reason why.
Format: "Analysis X: [reason]"
"""
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are evaluating technical analyses to select the most valuable implementation recommendation."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": 200,
                "temperature": 0.3
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            
            result = response.json()
            selection_text = result['choices'][0]['message']['content']
            
            # Parse selection (look for "Analysis X")
            for i in range(1, len(analyses) + 1):
                if f"Analysis {i}" in selection_text:
                    return analyses[i-1]
            
            # Fallback if parsing fails
            return max(analyses, key=lambda a: a.quality_score)
            
        except Exception as e:
            logger.error(f"❌ ChatGPT winner selection error: {e}")
            return max(analyses, key=lambda a: a.quality_score)
    
    def four_hour_aggregation(self):
        """Every 4 hours: Aggregate non-winner analyses"""
        try:
            logger.info("📊 Running 4-hour aggregation analysis...")
            
            # Get non-winner analyses from last 4 hours
            since_time = datetime.now() - timedelta(hours=4)
            analyses = self.db.get_non_winner_analyses_since(since_time)
            
            if not analyses:
                logger.warning("⚠️ No non-winner analyses found for aggregation")
                return
            
            # Create aggregation summary
            aggregation_data = {
                "analysis_count": len(analyses),
                "period_start": since_time.isoformat(),
                "period_end": datetime.now().isoformat(),
                "service_pairs": [(a.service_a, a.service_b) for a in analyses],
                "avg_quality_score": sum(a.quality_score for a in analyses) / len(analyses)
            }
            
            # Generate AI summary of aggregated insights
            ai_summary = self.generate_aggregation_summary(analyses)
            
            # Store aggregation
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO four_hour_aggregations (
                analysis_period_start, analysis_period_end,
                aggregated_data, ai_summary, insights_count
            ) VALUES (?, ?, ?, ?, ?)
            ''', (
                since_time.isoformat(),
                datetime.now().isoformat(),
                json.dumps(aggregation_data),
                ai_summary,
                len(analyses)
            ))
            
            # Mark analyses as aggregated
            analysis_ids = [a.id for a in analyses]
            cursor.executemany(
                'UPDATE connection_analyses SET is_aggregated = TRUE WHERE id = ?',
                [(aid,) for aid in analysis_ids]
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"📊 Aggregated {len(analyses)} analyses into 4-hour summary")
            
        except Exception as e:
            logger.error(f"❌ 4-hour aggregation error: {e}")
    
    def generate_aggregation_summary(self, analyses: List[ConnectionAnalysis]) -> str:
        """Generate AI summary of aggregated analyses"""
        if not self.api_key:
            return f"Aggregated {len(analyses)} connection analyses. Key services: {', '.join(set([a.service_a for a in analyses[:5]]))}"
        
        try:
            # Prepare summary of all analyses
            summary_text = f"AGGREGATION OF {len(analyses)} CONNECTION ANALYSES:\n\n"
            
            for i, analysis in enumerate(analyses[:10], 1):  # Limit to 10 for token limits
                summary_text += f"{i}. {analysis.service_a} ↔ {analysis.service_b} (Score: {analysis.quality_score:.1f})\n"
                summary_text += f"   Key insight: {analysis.ai_analysis[:200]}...\n\n"
            
            prompt = f"""
Analyze this collection of service connection analyses and provide:

{summary_text}

1. **Common Patterns**: What themes emerge across these analyses?
2. **System Architecture Insights**: What does this reveal about the system?
3. **Implementation Priorities**: Which connections should be prioritized?
4. **Strategic Recommendations**: High-level system improvements suggested by this data

Provide a concise but insightful summary for system architects.
"""
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a senior system architect analyzing patterns in microservices connection analyses."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 800,
                "temperature": 0.7
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=20)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            logger.error(f"❌ Aggregation summary error: {e}")
            return f"Aggregated {len(analyses)} analyses. System showing active connection opportunities across {len(set([a.service_a for a in analyses]))} unique services."
    
    def start_scheduler(self):
        """Start the scheduled workflow"""
        # Schedule tasks
        schedule.every(5).minutes.do(self.five_minute_analysis)
        schedule.every().hour.do(self.hourly_winner_selection) 
        schedule.every(4).hours.do(self.four_hour_aggregation)
        
        logger.info("⏰ Scheduler started:")
        logger.info("  🔄 Every 5 minutes: Connection analysis") 
        logger.info("  🏆 Every hour: Winner selection")
        logger.info("  📊 Every 4 hours: Aggregation analysis")
        logger.info("  📊 Daily output: 30 discoveries (24 hourly + 6 four-hourly)")
        
        # Run scheduler in separate thread
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        logger.info("🚀 AI Discovery Workflow is running!")

if __name__ == "__main__":
    workflow = AIDiscoveryWorkflow()
    workflow.start_scheduler()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("🛑 Workflow stopped by user")