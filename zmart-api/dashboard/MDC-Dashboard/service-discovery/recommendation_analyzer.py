#!/usr/bin/env python3
"""
Automated Recommendation Analysis System
Analyzes MDC pairs every 15 minutes, selects winners every 4 hours
"""

import os
import json
import sqlite3
import time
import asyncio
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests
from dataclasses import dataclass
import hashlib

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MDCPairAnalysis:
    """Represents analysis of an MDC pair"""
    pair_id: str
    service_a: str
    service_b: str
    analysis_content: str
    score: float
    commonalities: str
    complementaries: str
    integration_potential: str
    analyzed_at: str
    is_winner: bool = False
    winner_selected_at: Optional[str] = None

class RecommendationAnalyzer:
    """Automated system for analyzing MDC pairs and selecting winners"""
    
    def __init__(self, project_root: str, openai_api_key: str):
        self.project_root = Path(project_root)
        self.mdc_dir = self.project_root / ".cursor" / "rules"
        self.db_path = self.project_root / "zmart-api" / "services" / "service-discovery" / "recommendations.db"
        self.openai_api_key = openai_api_key
        self.running = False
        self.analysis_thread = None
        self.winner_thread = None
        
        # Initialize database
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for recommendations"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mdc_pair_analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pair_id TEXT UNIQUE NOT NULL,
                    service_a TEXT NOT NULL,
                    service_b TEXT NOT NULL,
                    analysis_content TEXT NOT NULL,
                    score REAL NOT NULL,
                    commonalities TEXT NOT NULL,
                    complementaries TEXT NOT NULL,
                    integration_potential TEXT NOT NULL,
                    analyzed_at TIMESTAMP NOT NULL,
                    is_winner BOOLEAN DEFAULT FALSE,
                    winner_selected_at TIMESTAMP NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS recommendation_cycles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_start TIMESTAMP NOT NULL,
                    cycle_end TIMESTAMP NOT NULL,
                    winner_pair_id TEXT NOT NULL,
                    total_analyses INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (winner_pair_id) REFERENCES mdc_pair_analyses (pair_id)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_pair_id ON mdc_pair_analyses (pair_id)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_score ON mdc_pair_analyses (score DESC)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_winner ON mdc_pair_analyses (is_winner, winner_selected_at)
            """)
            
        logger.info("✅ Database initialized successfully")

    def _get_mdc_files(self) -> List[Path]:
        """Get all MDC files from the rules directory"""
        mdc_files = []
        for file_path in self.mdc_dir.glob("*.mdc"):
            if file_path.is_file() and file_path.stat().st_size > 100:  # Skip very small files
                mdc_files.append(file_path)
        return mdc_files

    def _get_pair_id(self, service_a: str, service_b: str) -> str:
        """Generate consistent pair ID regardless of order"""
        services = sorted([service_a, service_b])
        pair_string = f"{services[0]}|{services[1]}"
        return hashlib.md5(pair_string.encode()).hexdigest()

    def _has_commonalities_and_complementaries(self, content_a: str, content_b: str) -> Tuple[bool, str, str]:
        """Check if two MDC files have commonalities and complementaries"""
        # Simple analysis - could be enhanced with NLP
        common_keywords = []
        complementary_aspects = []
        
        # Keywords that suggest commonalities
        common_patterns = [
            "API", "REST", "WebSocket", "Database", "Authentication", "Monitoring",
            "Trading", "Market", "Data", "Signal", "Process", "Service", "Port",
            "Security", "Health", "Status", "Configuration"
        ]
        
        # Check for common patterns
        for pattern in common_patterns:
            if pattern.lower() in content_a.lower() and pattern.lower() in content_b.lower():
                common_keywords.append(pattern)
        
        # Look for complementary aspects (one has what the other needs)
        if ("producer" in content_a.lower() and "consumer" in content_b.lower()) or \
           ("consumer" in content_a.lower() and "producer" in content_b.lower()):
            complementary_aspects.append("Producer-Consumer pattern")
            
        if ("frontend" in content_a.lower() and "backend" in content_b.lower()) or \
           ("backend" in content_a.lower() and "frontend" in content_b.lower()):
            complementary_aspects.append("Frontend-Backend integration")
            
        if ("client" in content_a.lower() and "server" in content_b.lower()) or \
           ("server" in content_a.lower() and "client" in content_b.lower()):
            complementary_aspects.append("Client-Server architecture")
        
        has_potential = len(common_keywords) >= 2 and len(complementary_aspects) >= 1
        
        return (
            has_potential,
            ", ".join(common_keywords) if common_keywords else "None identified",
            ", ".join(complementary_aspects) if complementary_aspects else "None identified"
        )

    async def _analyze_pair_with_chatgpt(self, service_a: str, service_b: str, content_a: str, content_b: str, commonalities: str, complementaries: str) -> Dict:
        """Analyze MDC pair using ChatGPT"""
        prompt = f"""
Analyze the integration potential between these two services for a cryptocurrency trading platform.

SERVICE A: {service_a}
{content_a[:1500]}...

SERVICE B: {service_b}  
{content_b[:1500]}...

IDENTIFIED COMMONALITIES: {commonalities}
IDENTIFIED COMPLEMENTARIES: {complementaries}

Please analyze and provide:
1. Integration Score (0-100): How well these services would work together
2. Key Benefits: Top 3 benefits of integrating these services
3. Implementation Complexity: Low/Medium/High and why
4. Integration Pattern: What type of integration would work best
5. Potential Challenges: Main challenges in integration
6. ROI Assessment: Expected return on investment for this integration

Format your response as JSON:
{{
    "integration_score": 85,
    "key_benefits": ["benefit1", "benefit2", "benefit3"],
    "implementation_complexity": "Medium",
    "complexity_reason": "explanation",
    "integration_pattern": "pattern type",
    "potential_challenges": ["challenge1", "challenge2"],
    "roi_assessment": "assessment text",
    "recommendation_summary": "brief summary"
}}
"""

        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert system architect specializing in microservice integration for cryptocurrency trading platforms. Provide detailed technical analysis."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.3
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Try to parse JSON response
                try:
                    analysis = json.loads(content)
                    return analysis
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    return {
                        "integration_score": 50,
                        "key_benefits": ["Enhanced system integration"],
                        "implementation_complexity": "Medium",
                        "integration_pattern": "API Integration",
                        "roi_assessment": "Moderate ROI expected",
                        "recommendation_summary": content[:200]
                    }
            else:
                logger.error(f"ChatGPT API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling ChatGPT API: {e}")
            return None

    async def _analyze_random_pair(self):
        """Analyze a random MDC pair that hasn't been analyzed recently"""
        mdc_files = self._get_mdc_files()
        if len(mdc_files) < 2:
            logger.warning("Not enough MDC files for analysis")
            return
        
        # Try to find unanalyzed pairs
        import random
        max_attempts = 20
        
        for _ in range(max_attempts):
            file_a, file_b = random.sample(mdc_files, 2)
            service_a = file_a.stem
            service_b = file_b.stem
            pair_id = self._get_pair_id(service_a, service_b)
            
            # Check if already analyzed recently (within last 4 hours)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM mdc_pair_analyses WHERE pair_id = ? AND analyzed_at > datetime('now', '-4 hours')",
                    (pair_id,)
                )
                if cursor.fetchone()[0] > 0:
                    continue  # Skip recently analyzed pairs
            
            # Read file contents
            try:
                content_a = file_a.read_text(encoding='utf-8')
                content_b = file_b.read_text(encoding='utf-8')
            except Exception as e:
                logger.error(f"Error reading files {file_a}, {file_b}: {e}")
                continue
            
            # Check for commonalities and complementaries
            has_potential, commonalities, complementaries = self._has_commonalities_and_complementaries(content_a, content_b)
            
            if not has_potential:
                continue  # Skip pairs without clear integration potential
            
            # Analyze with ChatGPT
            logger.info(f"🔍 Analyzing pair: {service_a} ↔ {service_b}")
            analysis = await self._analyze_pair_with_chatgpt(service_a, service_b, content_a, content_b, commonalities, complementaries)
            
            if analysis:
                # Store analysis in database
                analysis_record = MDCPairAnalysis(
                    pair_id=pair_id,
                    service_a=service_a,
                    service_b=service_b,
                    analysis_content=json.dumps(analysis),
                    score=analysis.get("integration_score", 50),
                    commonalities=commonalities,
                    complementaries=complementaries,
                    integration_potential=analysis.get("recommendation_summary", ""),
                    analyzed_at=datetime.now().isoformat()
                )
                
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO mdc_pair_analyses 
                        (pair_id, service_a, service_b, analysis_content, score, commonalities, 
                         complementaries, integration_potential, analyzed_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        analysis_record.pair_id,
                        analysis_record.service_a,
                        analysis_record.service_b,
                        analysis_record.analysis_content,
                        analysis_record.score,
                        analysis_record.commonalities,
                        analysis_record.complementaries,
                        analysis_record.integration_potential,
                        analysis_record.analyzed_at
                    ))
                
                logger.info(f"✅ Stored analysis for {service_a} ↔ {service_b} (Score: {analysis_record.score})")
                return
        
        logger.info("No suitable unanalyzed pairs found")

    def _select_cycle_winner(self):
        """Select winner from the last 4 hours of analyses"""
        four_hours_ago = (datetime.now() - timedelta(hours=4)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Get best scoring pair from last 4 hours
            cursor = conn.execute("""
                SELECT pair_id, service_a, service_b, score, analysis_content
                FROM mdc_pair_analyses 
                WHERE analyzed_at > ? AND is_winner = FALSE
                ORDER BY score DESC, analyzed_at DESC
                LIMIT 1
            """, (four_hours_ago,))
            
            winner = cursor.fetchone()
            if winner:
                pair_id, service_a, service_b, score, analysis_content = winner
                
                # Mark as winner
                conn.execute("""
                    UPDATE mdc_pair_analyses 
                    SET is_winner = TRUE, winner_selected_at = ?
                    WHERE pair_id = ?
                """, (datetime.now().isoformat(), pair_id))
                
                # Record cycle
                conn.execute("""
                    INSERT INTO recommendation_cycles 
                    (cycle_start, cycle_end, winner_pair_id, total_analyses)
                    VALUES (?, ?, ?, 
                            (SELECT COUNT(*) FROM mdc_pair_analyses WHERE analyzed_at > ?))
                """, (four_hours_ago, datetime.now().isoformat(), pair_id, four_hours_ago))
                
                logger.info(f"🏆 Winner selected: {service_a} ↔ {service_b} (Score: {score})")
                
                # Generate merged MDC for winner (this will be used in recommendations)
                self._generate_winner_mdc(service_a, service_b, analysis_content)
            else:
                logger.info("No analyses found for winner selection")

    def _generate_winner_mdc(self, service_a: str, service_b: str, analysis_content: str):
        """Generate merged MDC file for the winner pair"""
        try:
            analysis = json.loads(analysis_content)
            integration_name = f"integration-{service_a}-{service_b}"
            
            # Read original MDC files
            file_a = self.mdc_dir / f"{service_a}.mdc"
            file_b = self.mdc_dir / f"{service_b}.mdc"
            
            content_a = file_a.read_text(encoding='utf-8') if file_a.exists() else ""
            content_b = file_b.read_text(encoding='utf-8') if file_b.exists() else ""
            
            # Create enhanced integration MDC
            winner_mdc_content = f"""# {integration_name}.mdc
> Type: integration | Version: 1.0.0 | Owner: zmartbot | Components: {service_a} + {service_b}
> Winner: Selected from automated analysis (Score: {analysis.get('integration_score', 0)})

## Purpose
{analysis.get('recommendation_summary', 'Automated integration recommendation')}

## Integration Analysis
**Score**: {analysis.get('integration_score', 0)}/100
**Complexity**: {analysis.get('implementation_complexity', 'Medium')}
**Pattern**: {analysis.get('integration_pattern', 'API Integration')}

## Key Benefits
{chr(10).join([f"- {benefit}" for benefit in analysis.get('key_benefits', [])])}

## Implementation Details
**Complexity Reason**: {analysis.get('complexity_reason', 'Standard integration complexity')}

## Potential Challenges
{chr(10).join([f"- {challenge}" for challenge in analysis.get('potential_challenges', [])])}

## ROI Assessment
{analysis.get('roi_assessment', 'Positive ROI expected')}

## Source Services Combined
### {service_a}
{content_a[:500]}...

### {service_b} 
{content_b[:500]}...

---
**🤖 Generated by**: Automated Recommendation System
**📊 Analysis Score**: {analysis.get('integration_score', 0)}/100
**🕐 Winner Selected**: {datetime.now().isoformat()}
**⚡ Integration Pattern**: {analysis.get('integration_pattern', 'API Integration')}
"""

            # Save winner MDC to integration directory
            integration_dir = self.project_root / ".cursor" / "rules" / "integration" / "winners"
            integration_dir.mkdir(parents=True, exist_ok=True)
            
            winner_file = integration_dir / f"{integration_name}.mdc"
            winner_file.write_text(winner_mdc_content, encoding='utf-8')
            
            logger.info(f"🎯 Winner MDC generated: {winner_file}")
            
        except Exception as e:
            logger.error(f"Error generating winner MDC: {e}")

    def get_all_analyses(self) -> List[tuple]:
        """Get all MDC pair analyses from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT id, service_a, service_b, integration_potential, analysis_content, 
                           score, analyzed_at, is_winner
                    FROM mdc_pair_analyses 
                    ORDER BY analyzed_at DESC
                """)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting all analyses: {e}")
            return []
    
    def get_winners(self) -> List[tuple]:
        """Get all winner analyses from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT id, service_a, service_b, integration_potential, analysis_content,
                           score, analyzed_at, winner_selected_at
                    FROM mdc_pair_analyses 
                    WHERE is_winner = 1
                    ORDER BY winner_selected_at DESC
                """)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting winners: {e}")
            return []

    def get_top_recommendations(self, limit: int = 3) -> List[Dict]:
        """Get top unprocessed recommendations for manual triggers"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT service_a, service_b, score, analysis_content, commonalities, complementaries
                FROM mdc_pair_analyses 
                WHERE is_winner = FALSE
                ORDER BY score DESC, analyzed_at DESC
                LIMIT ?
            """, (limit,))
            
            results = []
            for row in cursor.fetchall():
                service_a, service_b, score, analysis_content, commonalities, complementaries = row
                try:
                    analysis = json.loads(analysis_content)
                    results.append({
                        "service_a": service_a,
                        "service_b": service_b,
                        "score": score,
                        "benefit": analysis.get("recommendation_summary", f"Integration between {service_a} and {service_b}"),
                        "implementation_effort": analysis.get("implementation_complexity", "medium").lower(),
                        "analysis": analysis,
                        "commonalities": commonalities,
                        "complementaries": complementaries
                    })
                except:
                    continue
            
            return results

    def start_automated_analysis(self):
        """Start the automated analysis system"""
        if self.running:
            logger.warning("Analysis system already running")
            return
        
        self.running = True
        logger.info("🚀 Starting automated recommendation analysis system")
        
        # Start 15-minute analysis cycle
        def analysis_loop():
            while self.running:
                try:
                    asyncio.run(self._analyze_random_pair())
                except Exception as e:
                    logger.error(f"Error in analysis loop: {e}")
                
                # Wait 15 minutes
                for _ in range(900):  # 900 seconds = 15 minutes
                    if not self.running:
                        break
                    time.sleep(1)
        
        # Start 4-hour winner selection cycle
        def winner_loop():
            while self.running:
                try:
                    self._select_cycle_winner()
                except Exception as e:
                    logger.error(f"Error in winner loop: {e}")
                
                # Wait 4 hours
                for _ in range(14400):  # 14400 seconds = 4 hours
                    if not self.running:
                        break
                    time.sleep(1)
        
        self.analysis_thread = threading.Thread(target=analysis_loop, daemon=True)
        self.winner_thread = threading.Thread(target=winner_loop, daemon=True)
        
        self.analysis_thread.start()
        self.winner_thread.start()
        
        logger.info("✅ Automated analysis system started (15min cycles + 4hr winner selection)")

    def stop_automated_analysis(self):
        """Stop the automated analysis system"""
        if not self.running:
            return
        
        self.running = False
        logger.info("🛑 Stopping automated analysis system")
        
        if self.analysis_thread:
            self.analysis_thread.join(timeout=5)
        if self.winner_thread:
            self.winner_thread.join(timeout=5)
        
        logger.info("✅ Automated analysis system stopped")

def main():
    """For testing purposes"""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python recommendation_analyzer.py <project_root> <openai_api_key>")
        return
    
    project_root = sys.argv[1]
    openai_api_key = sys.argv[2]
    
    analyzer = RecommendationAnalyzer(project_root, openai_api_key)
    
    try:
        analyzer.start_automated_analysis()
        # Keep running
        while True:
            time.sleep(60)
            print(f"System running... {datetime.now()}")
    except KeyboardInterrupt:
        analyzer.stop_automated_analysis()
        print("System stopped")

if __name__ == "__main__":
    main()