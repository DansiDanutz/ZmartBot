#!/usr/bin/env python3
"""
Memory Adapter Service for ZmartBot
Provides conversation persistence and memory context for Claude and OpenAI interactions
"""

import os
import sys
import json
import logging
import argparse
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConversationMemory:
    """Represents a conversation memory entry"""
    memory_id: str
    user_id: str
    session_id: str
    message_type: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: str
    ai_model: str  # 'claude', 'openai', 'hybrid'
    context_tags: List[str]
    importance_score: float = 0.5
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class MemoryContext:
    """Memory context for AI interactions"""
    recent_conversations: List[Dict]
    relevant_memories: List[Dict]
    user_preferences: Dict
    conversation_summary: str
    total_interactions: int

class MemoryAdapterService:
    """
    Memory Adapter Service that provides persistent conversation storage
    and intelligent memory context for AI interactions
    """
    
    def __init__(self, project_root: str = None, port: int = 8008):
        self.project_root = Path(project_root) if project_root else Path("../.")
        self.port = port
        self.db_path = self.project_root / "zmart-api" / "memory_database.db"
        
        # Initialize database
        self.init_database()
        
        # Initialize Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        self.setup_routes()
        
        logger.info(f"Memory Adapter Service initialized - Port: {self.port}")
    
    def init_database(self):
        """Initialize the memory database"""
        try:
            # Ensure database directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create database connection
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create conversation_memories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ai_model TEXT NOT NULL,
                    context_tags TEXT,
                    importance_score REAL DEFAULT 0.5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create user_preferences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    preferences TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create memory_summaries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_timestamp ON conversation_memories(user_id, timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_timestamp ON conversation_memories(session_id, timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_importance ON conversation_memories(importance_score)")
            
            conn.commit()
            conn.close()
            logger.info("Memory database initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def setup_routes(self):
        """Setup Flask API routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "memory-adapter-service"
            })
        
        @self.app.route('/memory/store', methods=['POST'])
        def store_memory():
            """Store a conversation memory"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"error": "No data provided"}), 400
                
                # Generate unique memory ID
                memory_id = hashlib.sha256(f"{data.get('user_id')}_{data.get('content')}_{datetime.now()}".encode()).hexdigest()[:16]
                
                # Create memory object
                memory = ConversationMemory(
                    memory_id=memory_id,
                    user_id=data.get('user_id'),
                    session_id=data.get('session_id'),
                    message_type=data.get('message_type'),
                    content=data.get('content'),
                    timestamp=datetime.now().isoformat(),
                    ai_model=data.get('ai_model', 'unknown'),
                    context_tags=data.get('context_tags', []),
                    importance_score=data.get('importance_score', 0.5)
                )
                
                # Store in database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO conversation_memories 
                    (memory_id, user_id, session_id, message_type, content, ai_model, context_tags, importance_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    memory.memory_id,
                    memory.user_id,
                    memory.session_id,
                    memory.message_type,
                    memory.content,
                    memory.ai_model,
                    json.dumps(memory.context_tags),
                    memory.importance_score
                ))
                
                conn.commit()
                conn.close()
                
                logger.info(f"Stored memory for user {memory.user_id}")
                
                return jsonify({
                    "success": True,
                    "memory_id": memory.memory_id,
                    "message": "Memory stored successfully"
                })
                
            except Exception as e:
                logger.error(f"Memory storage failed: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/memory/context/<user_id>', methods=['GET'])
        def get_memory_context(user_id):
            """Get memory context for a user"""
            try:
                session_id = request.args.get('session_id')
                limit = int(request.args.get('limit', 10))
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get recent conversations
                cursor.execute("""
                    SELECT memory_id, session_id, message_type, content, timestamp, ai_model, context_tags, importance_score
                    FROM conversation_memories 
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (user_id, limit))
                recent_memories = cursor.fetchall()
                
                # Get relevant high-importance memories
                cursor.execute("""
                    SELECT memory_id, session_id, message_type, content, timestamp, ai_model, context_tags, importance_score
                    FROM conversation_memories 
                    WHERE user_id = ? AND importance_score > 0.7
                    ORDER BY importance_score DESC, timestamp DESC
                    LIMIT 5
                """, (user_id,))
                important_memories = cursor.fetchall()
                
                # Get user preferences
                cursor.execute("SELECT preferences FROM user_preferences WHERE user_id = ?", (user_id,))
                prefs_row = cursor.fetchone()
                user_preferences = json.loads(prefs_row[0]) if prefs_row else {}
                
                # Get total interactions count
                cursor.execute("SELECT COUNT(*) FROM conversation_memories WHERE user_id = ?", (user_id,))
                total_interactions = cursor.fetchone()[0]
                
                conn.close()
                
                # Format response
                def format_memory(row):
                    return {
                        "memory_id": row[0],
                        "session_id": row[1],
                        "message_type": row[2],
                        "content": row[3],
                        "timestamp": row[4],
                        "ai_model": row[5],
                        "context_tags": json.loads(row[6]) if row[6] else [],
                        "importance_score": row[7]
                    }
                
                recent_conversations = [format_memory(row) for row in recent_memories]
                relevant_memories = [format_memory(row) for row in important_memories]
                
                # Generate conversation summary
                conversation_summary = self.generate_conversation_summary(recent_conversations)
                
                context = MemoryContext(
                    recent_conversations=recent_conversations,
                    relevant_memories=relevant_memories,
                    user_preferences=user_preferences,
                    conversation_summary=conversation_summary,
                    total_interactions=total_interactions
                )
                
                return jsonify(asdict(context))
                
            except Exception as e:
                logger.error(f"Memory context retrieval failed: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/memory/preferences/<user_id>', methods=['POST'])
        def update_preferences(user_id):
            """Update user preferences"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"error": "No preferences provided"}), 400
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Upsert preferences
                cursor.execute("""
                    INSERT OR REPLACE INTO user_preferences (user_id, preferences, updated_at)
                    VALUES (?, ?, datetime('now'))
                """, (user_id, json.dumps(data)))
                
                conn.commit()
                conn.close()
                
                return jsonify({
                    "success": True,
                    "message": "Preferences updated successfully"
                })
                
            except Exception as e:
                logger.error(f"Preferences update failed: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/memory/summary/<user_id>', methods=['GET'])
        def get_user_summary(user_id):
            """Get comprehensive user summary"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get conversation statistics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_messages,
                        COUNT(DISTINCT session_id) as total_sessions,
                        AVG(importance_score) as avg_importance,
                        ai_model,
                        COUNT(*) as model_count
                    FROM conversation_memories 
                    WHERE user_id = ?
                    GROUP BY ai_model
                """, (user_id,))
                stats = cursor.fetchall()
                
                # Get recent topics (from context tags)
                cursor.execute("""
                    SELECT context_tags, COUNT(*) as frequency
                    FROM conversation_memories 
                    WHERE user_id = ? AND context_tags IS NOT NULL AND context_tags != '[]'
                    GROUP BY context_tags
                    ORDER BY frequency DESC
                    LIMIT 10
                """, (user_id,))
                topics = cursor.fetchall()
                
                conn.close()
                
                return jsonify({
                    "user_id": user_id,
                    "conversation_stats": [
                        {
                            "ai_model": row[3],
                            "message_count": row[4],
                            "avg_importance": row[2]
                        } for row in stats
                    ],
                    "total_messages": sum(row[4] for row in stats),
                    "total_sessions": stats[0][1] if stats else 0,
                    "popular_topics": [
                        {
                            "tags": json.loads(row[0]) if row[0] else [],
                            "frequency": row[1]
                        } for row in topics
                    ]
                })
                
            except Exception as e:
                logger.error(f"User summary failed: {e}")
                return jsonify({"error": str(e)}), 500
    
    def generate_conversation_summary(self, conversations: List[Dict]) -> str:
        """Generate a brief summary of recent conversations"""
        if not conversations:
            return "No recent conversations"
        
        # Simple summarization logic
        user_messages = [c for c in conversations if c['message_type'] == 'user']
        assistant_messages = [c for c in conversations if c['message_type'] == 'assistant']
        
        topics = set()
        for conv in conversations:
            topics.update(conv.get('context_tags', []))
        
        summary = f"Recent activity: {len(user_messages)} user messages, {len(assistant_messages)} responses"
        if topics:
            summary += f". Topics discussed: {', '.join(list(topics)[:3])}"
        
        return summary
    
    def run(self):
        """Run the Memory Adapter service"""
        logger.info(f"Starting Memory Adapter Service on port {self.port}")
        self.app.run(host='0.0.0.0', port=self.port, debug=False)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Memory Adapter Service')
    parser.add_argument('--port', type=int, default=8008, help='Port to run on')
    parser.add_argument('--project-root', type=str, help='Project root directory')
    
    args = parser.parse_args()
    
    # Create and run service
    service = MemoryAdapterService(
        project_root=args.project_root,
        port=args.port
    )
    
    service.run()

if __name__ == '__main__':
    main()