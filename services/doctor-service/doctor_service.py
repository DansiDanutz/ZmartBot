#!/usr/bin/env python3
"""
ZmartBot Doctor Service - AI-Powered System Diagnostics & Recovery
Port: 8700
Author: ZmartBot Team

Advanced AI diagnostic service that analyzes service problems, generates intelligent 
solutions, and provides automated recovery strategies when auto-fix mechanisms fail.
"""

import os
import sys
import json
import sqlite3
import hashlib
import secrets
import asyncio
import aiohttp
import argparse
import traceback
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import time
import subprocess
from dataclasses import dataclass, asdict

from fastapi import FastAPI, HTTPException, Depends, Request, status, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, field_validator
import uvicorn

# Pydantic Models
class DiagnoseRequest(BaseModel):
    service_name: str = Field(..., description="Name of the service with problems")
    problem_description: str = Field(..., description="Description of the problem")
    service_details: Dict[str, Any] = Field(default_factory=dict, description="Service configuration details")
    mdc_content: str = Field("", description="MDC file content with problem report")
    health_status: Dict[str, Any] = Field(default_factory=dict, description="Current health status")
    auto_fix_attempted: bool = Field(False, description="Whether auto-fix was attempted")
    priority: str = Field("normal", description="Priority level: low, normal, high, critical")
    
    @field_validator('priority')
    @classmethod  
    def validate_priority(cls, v: str) -> str:
        if v not in ['low', 'normal', 'high', 'critical']:
            raise ValueError('Priority must be one of: low, normal, high, critical')
        return v

class SolutionRequest(BaseModel):
    diagnosis_id: str = Field(..., description="Diagnosis ID to execute")
    solution_id: str = Field(..., description="Solution ID to execute")
    confirmation: bool = Field(False, description="User confirmation for execution")

class FeedbackRequest(BaseModel):
    diagnosis_id: str = Field(..., description="Diagnosis ID")
    solution_id: str = Field(..., description="Solution ID")
    success: bool = Field(..., description="Whether solution was successful")
    feedback: str = Field("", description="Additional feedback")
    execution_time: int = Field(0, description="Execution time in seconds")

class DiagnosisResponse(BaseModel):
    diagnosis_id: str
    service_name: str
    problem_description: str
    diagnosis: str
    root_cause: str
    solutions: List[Dict[str, Any]]
    prevention: str
    monitoring: str
    status: str
    created_at: str
    estimated_resolution_time: str

class HistoryResponse(BaseModel):
    diagnoses: List[DiagnosisResponse]
    total_count: int
    page: int
    page_size: int

@dataclass
class SafetyRule:
    """Safety rule for command validation"""
    pattern: str
    risk_level: str
    allowed: bool
    description: str

class DoctorService:
    """Main Doctor Service class"""
    
    def __init__(self, db_path: str = None, openai_api_key: str = None):
        self.db_path = db_path or "/Users/dansidanutz/Desktop/ZmartBot/data/doctor_service.db"
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.service_token = os.getenv("DOCTOR_SERVICE_TOKEN", "doctor-service-token")
        self.orchestration_url = os.getenv("ORCHESTRATION_SERVICE_URL", "http://localhost:8002")
        self.passport_url = os.getenv("PASSPORT_SERVICE_URL", "http://localhost:8620")
        self.max_concurrent = int(os.getenv("MAX_CONCURRENT_DIAGNOSES", "5"))
        self.ai_timeout = int(os.getenv("AI_TIMEOUT_SECONDS", "60"))
        self.enable_auto_execution = os.getenv("ENABLE_AUTO_EXECUTION", "false").lower() == "true"
        
        # Safety rules for command validation
        self.safety_rules = self.load_safety_rules()
        
        # Active diagnoses tracking
        self.active_diagnoses = {}
        self.diagnosis_queue = asyncio.Queue()
        
        self.init_database()
        print("✅ Doctor Service initialized successfully")

    def init_database(self):
        """Initialize SQLite database with required tables"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # Diagnoses table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS diagnoses (
                    id TEXT PRIMARY KEY,
                    service_name TEXT NOT NULL,
                    problem_description TEXT NOT NULL,
                    problem_level TEXT NOT NULL,
                    mdc_content TEXT,
                    service_details JSON,
                    health_status JSON,
                    auto_fix_attempted BOOLEAN DEFAULT FALSE,
                    diagnosis_result JSON NOT NULL,
                    ai_model_version TEXT,
                    processing_time_seconds REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    execution_result JSON,
                    client_ip TEXT,
                    user_agent TEXT
                );
            """)
            
            # Solutions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS solutions (
                    id TEXT PRIMARY KEY,
                    diagnosis_id TEXT NOT NULL,
                    solution_data JSON NOT NULL,
                    priority INTEGER DEFAULT 1,
                    risk_level TEXT DEFAULT 'low',
                    execution_status TEXT DEFAULT 'pending',
                    success_rate REAL DEFAULT 0.0,
                    execution_time_seconds INTEGER DEFAULT 0,
                    commands JSON,
                    rollback_plan JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    executed_at TIMESTAMP,
                    FOREIGN KEY (diagnosis_id) REFERENCES diagnoses (id)
                );
            """)
            
            # Feedback table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id TEXT PRIMARY KEY,
                    diagnosis_id TEXT NOT NULL,
                    solution_id TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    feedback_text TEXT,
                    execution_time_seconds INTEGER,
                    improvements JSON,
                    user_rating INTEGER CHECK(user_rating >= 1 AND user_rating <= 5),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (diagnosis_id) REFERENCES diagnoses (id),
                    FOREIGN KEY (solution_id) REFERENCES solutions (id)
                );
            """)
            
            # Learning table for AI improvement
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learning_data (
                    id TEXT PRIMARY KEY,
                    problem_pattern TEXT NOT NULL,
                    solution_pattern TEXT NOT NULL,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    avg_execution_time REAL DEFAULT 0.0,
                    confidence_score REAL DEFAULT 0.0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_diagnoses_service ON diagnoses(service_name);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_diagnoses_status ON diagnoses(status);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_diagnoses_created ON diagnoses(created_at);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_solutions_diagnosis ON solutions(diagnosis_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_feedback_diagnosis ON feedback(diagnosis_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_learning_pattern ON learning_data(problem_pattern);")
            
            conn.commit()
            print("✅ Doctor Service database initialized")

    def load_safety_rules(self) -> List[SafetyRule]:
        """Load safety rules for command validation"""
        return [
            SafetyRule("rm -rf", "critical", False, "Dangerous recursive delete"),
            SafetyRule("sudo", "high", False, "Requires administrative privileges"),
            SafetyRule("chmod 777", "high", False, "Overly permissive permissions"),
            SafetyRule("killall", "medium", False, "Mass process termination"),
            SafetyRule("systemctl stop", "high", True, "System service stop (allowed)"),
            SafetyRule("systemctl start", "high", True, "System service start (allowed)"),
            SafetyRule("systemctl restart", "high", True, "System service restart (allowed)"),
            SafetyRule("docker stop", "medium", True, "Docker container stop (allowed)"),
            SafetyRule("docker start", "medium", True, "Docker container start (allowed)"),
            SafetyRule("docker restart", "medium", True, "Docker container restart (allowed)"),
            SafetyRule("pkill -f", "medium", True, "Process kill by name (allowed)"),
            SafetyRule("curl", "low", True, "HTTP requests (allowed)"),
            SafetyRule("wget", "low", True, "File downloads (allowed)"),
            SafetyRule("python3", "low", True, "Python script execution (allowed)"),
            SafetyRule("./", "medium", True, "Script execution (allowed)"),
            SafetyRule("ps aux", "low", True, "Process listing (allowed)"),
            SafetyRule("ls", "low", True, "Directory listing (allowed)"),
            SafetyRule("cat", "low", True, "File reading (allowed)"),
            SafetyRule("grep", "low", True, "Text searching (allowed)"),
            SafetyRule("tail", "low", True, "Log reading (allowed)"),
            SafetyRule("head", "low", True, "File preview (allowed)"),
        ]

    def generate_diagnosis_id(self) -> str:
        """Generate unique diagnosis ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_hash = secrets.token_hex(4).upper()
        return f"DIAG-{timestamp}-{random_hash}"

    def generate_solution_id(self, diagnosis_id: str) -> str:
        """Generate unique solution ID"""
        timestamp = datetime.now().strftime("%H%M%S")
        random_hash = secrets.token_hex(3).upper()
        return f"SOL-{diagnosis_id.split('-')[1]}-{timestamp}-{random_hash}"

    async def diagnose_problem(self, request: DiagnoseRequest, client_ip: str = None, user_agent: str = None) -> Dict[str, Any]:
        """Main diagnosis function with AI integration"""
        start_time = time.time()
        diagnosis_id = self.generate_diagnosis_id()
        
        try:
            print(f"🩺 Starting diagnosis {diagnosis_id} for service: {request.service_name}")
            
            # Store initial diagnosis record
            self.store_diagnosis_record(diagnosis_id, request, client_ip, user_agent, "processing")
            
            # Check if we have cached/learned solution for this problem
            cached_solution = await self.check_learned_solution(request.problem_description, request.service_name)
            
            if cached_solution and cached_solution['confidence_score'] > 0.8:
                print(f"📚 Using learned solution for {request.service_name}: {cached_solution['solution_pattern']}")
                diagnosis_result = self.format_cached_solution(cached_solution, request)
            else:
                # Get AI analysis
                print(f"🤖 Requesting AI analysis for {request.service_name}...")
                diagnosis_result = await self.get_ai_analysis(request)
            
            # Validate and enhance solutions
            enhanced_solutions = []
            for i, solution in enumerate(diagnosis_result.get('solutions', [])):
                solution_id = self.generate_solution_id(diagnosis_id)
                
                # Validate commands for safety
                if 'commands' in solution:
                    safety_result = self.validate_command_safety(solution['commands'])
                    solution['safety_validation'] = safety_result
                    solution['executable'] = safety_result['all_safe']
                else:
                    solution['safety_validation'] = {'all_safe': False, 'reason': 'No commands provided'}
                    solution['executable'] = False
                
                # Add solution metadata
                solution['solution_id'] = solution_id
                solution['priority'] = solution.get('priority', i + 1)
                solution['estimated_success_rate'] = self.estimate_success_rate(request.problem_description, solution)
                
                enhanced_solutions.append(solution)
                
                # Store solution in database
                self.store_solution_record(solution_id, diagnosis_id, solution)
            
            diagnosis_result['solutions'] = enhanced_solutions
            diagnosis_result['diagnosis_id'] = diagnosis_id
            diagnosis_result['service_name'] = request.service_name
            diagnosis_result['estimated_resolution_time'] = self.estimate_resolution_time(enhanced_solutions)
            
            # Update diagnosis with results
            processing_time = time.time() - start_time
            self.update_diagnosis_result(diagnosis_id, diagnosis_result, processing_time, "completed")
            
            print(f"✅ Diagnosis {diagnosis_id} completed in {processing_time:.2f}s")
            
            return diagnosis_result
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_result = {
                'diagnosis_id': diagnosis_id,
                'service_name': request.service_name,
                'error': str(e),
                'diagnosis': f"Analysis failed: {str(e)}",
                'root_cause': "Unable to determine due to analysis failure",
                'solutions': [],
                'prevention': "Ensure AI service is available and properly configured",
                'monitoring': "Monitor AI service health and response times",
                'status': 'failed'
            }
            
            self.update_diagnosis_result(diagnosis_id, error_result, processing_time, "failed")
            print(f"❌ Diagnosis {diagnosis_id} failed: {str(e)}")
            
            return error_result

    async def get_ai_analysis(self, request: DiagnoseRequest) -> Dict[str, Any]:
        """Get AI analysis from ChatGPT"""
        if not self.openai_api_key:
            return self.get_fallback_analysis(request)
        
        # Construct AI prompt
        prompt = self.build_ai_prompt(request)
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.ai_timeout)) as session:
                headers = {
                    'Authorization': f'Bearer {self.openai_api_key}',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    "model": "gpt-4",
                    "messages": [
                        {"role": "system", "content": "You are an expert system administrator and DevOps engineer specializing in service diagnostics and recovery. Respond only with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 2000,
                    "temperature": 0.3
                }
                
                async with session.post('https://api.openai.com/v1/chat/completions', 
                                      headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        ai_content = result['choices'][0]['message']['content']
                        
                        # Parse AI response
                        try:
                            return json.loads(ai_content)
                        except json.JSONDecodeError:
                            print(f"⚠️ AI response is not valid JSON, using fallback")
                            return self.get_fallback_analysis(request)
                    else:
                        error_text = await response.text()
                        print(f"❌ AI API error ({response.status}): {error_text}")
                        return self.get_fallback_analysis(request)
                        
        except Exception as e:
            print(f"❌ AI analysis failed: {str(e)}")
            return self.get_fallback_analysis(request)

    def build_ai_prompt(self, request: DiagnoseRequest) -> str:
        """Build comprehensive AI prompt for analysis"""
        return f"""
You are analyzing a service problem in the ZmartBot trading platform. Provide a comprehensive analysis in JSON format.

CONTEXT:
- Service: {request.service_name}
- Problem: {request.problem_description}
- Priority: {request.priority}
- Auto-fix attempted: {request.auto_fix_attempted}

SERVICE DETAILS:
{json.dumps(request.service_details, indent=2) if request.service_details else "No details provided"}

HEALTH STATUS:
{json.dumps(request.health_status, indent=2) if request.health_status else "No health status provided"}

MDC DOCUMENTATION:
{request.mdc_content[:2000] if request.mdc_content else "No MDC content provided"}

REQUIREMENTS:
1. Root cause analysis based on the information provided
2. Multiple solutions ranked by priority (most likely to succeed first)
3. Each solution must include specific commands that are safe to execute
4. Provide rollback plans for each solution
5. Include prevention recommendations
6. Suggest monitoring improvements

RESPONSE FORMAT (JSON only, no markdown):
{{
  "diagnosis": "Detailed analysis of the problem including symptoms and potential causes",
  "root_cause": "Primary root cause identification with reasoning",
  "solutions": [
    {{
      "priority": 1,
      "description": "Clear description of what this solution does",
      "commands": ["command1", "command2"],
      "risk_level": "low|medium|high",
      "estimated_time": "5 minutes",
      "success_probability": "90%",
      "rollback_plan": ["rollback_command1", "rollback_command2"],
      "requires_downtime": false
    }}
  ],
  "prevention": "Specific recommendations to prevent this issue in the future",
  "monitoring": "Monitoring improvements to detect this issue earlier"
}}

Focus on practical, executable solutions for ZmartBot services running on macOS. Prioritize service restart, configuration fixes, and dependency checks. Avoid destructive operations.
"""

    def get_fallback_analysis(self, request: DiagnoseRequest) -> Dict[str, Any]:
        """Fallback analysis when AI is unavailable"""
        problem_lower = request.problem_description.lower()
        
        # Rule-based analysis for common problems
        if "health check not responding" in problem_lower:
            return {
                "diagnosis": "Service health endpoint is not responding, indicating the service may be down or unresponsive.",
                "root_cause": "Service process may have crashed, be overloaded, or have network connectivity issues.",
                "solutions": [
                    {
                        "priority": 1,
                        "description": "Restart the service using orchestration system",
                        "commands": [f"curl -X POST {self.orchestration_url}/api/orchestration/services/{request.service_name}/restart"],
                        "risk_level": "low",
                        "estimated_time": "30 seconds",
                        "success_probability": "85%",
                        "rollback_plan": ["curl -X POST " + self.orchestration_url + f"/api/orchestration/services/{request.service_name}/stop"],
                        "requires_downtime": True
                    },
                    {
                        "priority": 2,
                        "description": "Check service process and logs",
                        "commands": [f"ps aux | grep {request.service_name}", f"tail -50 /Users/dansidanutz/Desktop/ZmartBot/logs/{request.service_name}.log"],
                        "risk_level": "low",
                        "estimated_time": "2 minutes",
                        "success_probability": "70%",
                        "rollback_plan": [],
                        "requires_downtime": False
                    }
                ],
                "prevention": "Implement better health monitoring with timeout alerts and automatic restart policies.",
                "monitoring": "Add health check frequency monitoring and alerting for consecutive failures."
            }
        elif "connection failed" in problem_lower:
            return {
                "diagnosis": "Service connection is failing, likely due to network issues or service being down.",
                "root_cause": "Port may be closed, service not listening, or network connectivity problems.",
                "solutions": [
                    {
                        "priority": 1,
                        "description": "Check if service is running and restart if needed",
                        "commands": [f"lsof -i :{request.service_details.get('port', '8000')}", f"curl -X POST {self.orchestration_url}/api/orchestration/services/{request.service_name}/restart"],
                        "risk_level": "low",
                        "estimated_time": "1 minute",
                        "success_probability": "80%",
                        "rollback_plan": [],
                        "requires_downtime": True
                    }
                ],
                "prevention": "Implement connection pooling and retry mechanisms with circuit breakers.",
                "monitoring": "Monitor connection success rates and response times continuously."
            }
        else:
            return {
                "diagnosis": f"Generic analysis for problem: {request.problem_description}",
                "root_cause": "Unable to determine specific root cause without AI analysis. Manual investigation required.",
                "solutions": [
                    {
                        "priority": 1,
                        "description": "Manual investigation and service restart",
                        "commands": [f"curl -X POST {self.orchestration_url}/api/orchestration/services/{request.service_name}/restart"],
                        "risk_level": "medium",
                        "estimated_time": "5 minutes",
                        "success_probability": "60%",
                        "rollback_plan": [],
                        "requires_downtime": True
                    }
                ],
                "prevention": "Enable AI diagnostics for better analysis of this issue type.",
                "monitoring": "Implement comprehensive monitoring for early problem detection."
            }

    def validate_command_safety(self, commands: List[str]) -> Dict[str, Any]:
        """Validate command safety against safety rules"""
        results = []
        all_safe = True
        
        for command in commands:
            command_result = {
                'command': command,
                'safe': True,
                'risk_level': 'low',
                'violations': []
            }
            
            for rule in self.safety_rules:
                if rule.pattern in command:
                    if not rule.allowed:
                        command_result['safe'] = False
                        command_result['risk_level'] = rule.risk_level
                        command_result['violations'].append({
                            'rule': rule.pattern,
                            'description': rule.description,
                            'risk_level': rule.risk_level
                        })
                        all_safe = False
                    elif rule.risk_level in ['high', 'critical']:
                        command_result['risk_level'] = rule.risk_level
            
            results.append(command_result)
        
        return {
            'all_safe': all_safe,
            'command_results': results,
            'highest_risk': max([r['risk_level'] for r in results] + ['low'], key=lambda x: ['low', 'medium', 'high', 'critical'].index(x))
        }

    def estimate_success_rate(self, problem_description: str, solution: Dict[str, Any]) -> float:
        """Estimate solution success rate based on historical data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT success_count, failure_count, confidence_score
                    FROM learning_data 
                    WHERE problem_pattern LIKE ? 
                    ORDER BY confidence_score DESC 
                    LIMIT 1
                """, (f"%{problem_description[:50]}%",))
                
                result = cursor.fetchone()
                if result:
                    success_count, failure_count, confidence_score = result
                    total_attempts = success_count + failure_count
                    if total_attempts > 0:
                        return (success_count / total_attempts) * confidence_score
                
                # Fallback to solution's own estimate or default
                return float(solution.get('success_probability', '75%').rstrip('%')) / 100.0
                
        except Exception as e:
            print(f"⚠️ Error estimating success rate: {e}")
            return 0.75  # Default 75% success rate

    def estimate_resolution_time(self, solutions: List[Dict[str, Any]]) -> str:
        """Estimate total resolution time for all solutions"""
        if not solutions:
            return "Unknown"
        
        # Take the fastest solution time
        times = []
        for solution in solutions:
            time_str = solution.get('estimated_time', '5 minutes')
            # Parse time string and convert to minutes
            if 'minute' in time_str:
                minutes = int(time_str.split()[0])
                times.append(minutes)
            elif 'second' in time_str:
                seconds = int(time_str.split()[0])
                times.append(seconds / 60)  # Convert to minutes
            else:
                times.append(5)  # Default 5 minutes
        
        min_time = min(times) if times else 5
        if min_time < 1:
            return f"{int(min_time * 60)} seconds"
        else:
            return f"{int(min_time)} minutes"

    async def check_learned_solution(self, problem_description: str, service_name: str) -> Optional[Dict[str, Any]]:
        """Check if we have learned solution for this problem"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT problem_pattern, solution_pattern, success_count, failure_count, 
                           avg_execution_time, confidence_score
                    FROM learning_data 
                    WHERE problem_pattern LIKE ? AND confidence_score > 0.7
                    ORDER BY confidence_score DESC, success_count DESC
                    LIMIT 1
                """, (f"%{problem_description[:100]}%",))
                
                result = cursor.fetchone()
                if result:
                    return {
                        'problem_pattern': result[0],
                        'solution_pattern': result[1],
                        'success_count': result[2],
                        'failure_count': result[3],
                        'avg_execution_time': result[4],
                        'confidence_score': result[5]
                    }
                return None
                
        except Exception as e:
            print(f"⚠️ Error checking learned solutions: {e}")
            return None

    def format_cached_solution(self, cached_solution: Dict[str, Any], request: DiagnoseRequest) -> Dict[str, Any]:
        """Format cached solution into standard response format"""
        return {
            "diagnosis": f"Based on previous successful resolutions, this appears to be a recurring issue with {request.service_name}.",
            "root_cause": f"Historical analysis suggests: {cached_solution['problem_pattern']}",
            "solutions": [
                {
                    "priority": 1,
                    "description": f"Learned solution: {cached_solution['solution_pattern']}",
                    "commands": [f"curl -X POST {self.orchestration_url}/api/orchestration/services/{request.service_name}/restart"],
                    "risk_level": "low",
                    "estimated_time": f"{int(cached_solution['avg_execution_time'])} seconds",
                    "success_probability": f"{int(cached_solution['confidence_score'] * 100)}%",
                    "rollback_plan": [],
                    "requires_downtime": True
                }
            ],
            "prevention": "Continue monitoring to improve learned solution accuracy",
            "monitoring": "Track solution effectiveness for continuous learning"
        }

    def store_diagnosis_record(self, diagnosis_id: str, request: DiagnoseRequest, 
                             client_ip: str = None, user_agent: str = None, status: str = "pending"):
        """Store diagnosis record in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO diagnoses (
                        id, service_name, problem_description, problem_level, 
                        mdc_content, service_details, health_status, auto_fix_attempted,
                        diagnosis_result, status, client_ip, user_agent
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    diagnosis_id, request.service_name, request.problem_description, request.priority,
                    request.mdc_content, json.dumps(request.service_details), json.dumps(request.health_status),
                    request.auto_fix_attempted, json.dumps({}), status, client_ip, user_agent
                ))
                conn.commit()
        except Exception as e:
            print(f"⚠️ Error storing diagnosis record: {e}")

    def update_diagnosis_result(self, diagnosis_id: str, result: Dict[str, Any], 
                              processing_time: float, status: str):
        """Update diagnosis with results"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE diagnoses 
                    SET diagnosis_result = ?, processing_time_seconds = ?, status = ?, 
                        ai_model_version = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    json.dumps(result), processing_time, status, "gpt-4", diagnosis_id
                ))
                conn.commit()
        except Exception as e:
            print(f"⚠️ Error updating diagnosis result: {e}")

    def store_solution_record(self, solution_id: str, diagnosis_id: str, solution: Dict[str, Any]):
        """Store solution record in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO solutions (
                        id, diagnosis_id, solution_data, priority, risk_level,
                        commands, rollback_plan, success_rate
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    solution_id, diagnosis_id, json.dumps(solution), solution.get('priority', 1),
                    solution.get('risk_level', 'low'), json.dumps(solution.get('commands', [])),
                    json.dumps(solution.get('rollback_plan', [])), solution.get('estimated_success_rate', 0.75)
                ))
                conn.commit()
        except Exception as e:
            print(f"⚠️ Error storing solution record: {e}")

    async def execute_solution(self, diagnosis_id: str, solution_id: str, confirmation: bool) -> Dict[str, Any]:
        """Execute a solution with safety checks"""
        if not confirmation:
            raise HTTPException(status_code=400, detail="User confirmation required for solution execution")
        
        if not self.enable_auto_execution:
            return {
                "status": "disabled",
                "message": "Automatic execution is disabled. Manual execution required.",
                "instructions": "Execute the commands manually or enable auto-execution in configuration."
            }
        
        try:
            # Get solution details
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT solution_data, commands, rollback_plan, risk_level
                    FROM solutions WHERE id = ? AND diagnosis_id = ?
                """, (solution_id, diagnosis_id))
                
                result = cursor.fetchone()
                if not result:
                    raise HTTPException(status_code=404, detail="Solution not found")
                
                solution_data, commands_json, rollback_json, risk_level = result
                commands = json.loads(commands_json) if commands_json else []
                rollback_plan = json.loads(rollback_json) if rollback_json else []
            
            # Additional safety check for high-risk operations
            if risk_level in ['high', 'critical'] and not confirmation:
                return {
                    "status": "requires_confirmation",
                    "message": f"High-risk operation ({risk_level}) requires explicit confirmation",
                    "commands": commands,
                    "rollback_plan": rollback_plan
                }
            
            # Execute commands
            execution_results = []
            success = True
            
            for i, command in enumerate(commands):
                try:
                    print(f"🔧 Executing command {i+1}/{len(commands)}: {command}")
                    
                    if command.startswith('curl'):
                        # Execute HTTP commands using aiohttp
                        result = await self.execute_http_command(command)
                    else:
                        # Execute shell commands
                        result = await self.execute_shell_command(command)
                    
                    execution_results.append({
                        "command": command,
                        "success": result["success"],
                        "output": result["output"],
                        "error": result.get("error")
                    })
                    
                    if not result["success"]:
                        success = False
                        print(f"❌ Command failed: {command}")
                        break
                    else:
                        print(f"✅ Command succeeded: {command}")
                        
                except Exception as e:
                    execution_results.append({
                        "command": command,
                        "success": False,
                        "output": "",
                        "error": str(e)
                    })
                    success = False
                    print(f"❌ Command exception: {command} - {str(e)}")
                    break
            
            # Update solution execution status
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE solutions 
                    SET execution_status = ?, executed_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, ("success" if success else "failed", solution_id))
                conn.commit()
            
            return {
                "status": "success" if success else "failed",
                "solution_id": solution_id,
                "execution_results": execution_results,
                "rollback_available": len(rollback_plan) > 0,
                "message": "Solution executed successfully" if success else "Solution execution failed"
            }
            
        except Exception as e:
            print(f"❌ Solution execution error: {str(e)}")
            return {
                "status": "error",
                "message": f"Execution error: {str(e)}",
                "solution_id": solution_id
            }

    async def execute_http_command(self, command: str) -> Dict[str, Any]:
        """Execute HTTP command using aiohttp"""
        try:
            # Parse curl command (basic parsing)
            if 'POST' in command and '/restart' in command:
                # Extract URL from curl command
                parts = command.split()
                url = None
                for part in parts:
                    if part.startswith('http'):
                        url = part
                        break
                
                if url:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                            text = await response.text()
                            return {
                                "success": response.status == 200,
                                "output": text,
                                "status_code": response.status
                            }
            
            return {"success": False, "error": "Unsupported HTTP command", "output": ""}
            
        except Exception as e:
            return {"success": False, "error": str(e), "output": ""}

    async def execute_shell_command(self, command: str) -> Dict[str, Any]:
        """Execute shell command safely"""
        try:
            # Execute command with timeout
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            
            return {
                "success": process.returncode == 0,
                "output": stdout.decode(),
                "error": stderr.decode() if stderr else None,
                "return_code": process.returncode
            }
            
        except asyncio.TimeoutError:
            return {"success": False, "error": "Command timeout", "output": ""}
        except Exception as e:
            return {"success": False, "error": str(e), "output": ""}

    def get_diagnosis_history(self, service_name: str = None, limit: int = 50, status: str = None, page: int = 1) -> Dict[str, Any]:
        """Get diagnosis history with pagination"""
        try:
            offset = (page - 1) * limit
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build query with filters
                where_conditions = []
                params = []
                
                if service_name:
                    where_conditions.append("service_name = ?")
                    params.append(service_name)
                
                if status:
                    where_conditions.append("status = ?")
                    params.append(status)
                
                where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
                
                # Get total count
                count_query = f"SELECT COUNT(*) FROM diagnoses {where_clause}"
                cursor.execute(count_query, params)
                total_count = cursor.fetchone()[0]
                
                # Get paginated results
                query = f"""
                    SELECT id, service_name, problem_description, problem_level, 
                           diagnosis_result, status, created_at, processing_time_seconds
                    FROM diagnoses 
                    {where_clause}
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                """
                params.extend([limit, offset])
                cursor.execute(query, params)
                
                diagnoses = []
                for row in cursor.fetchall():
                    diagnosis_result = json.loads(row[4]) if row[4] else {}
                    diagnoses.append(DiagnosisResponse(
                        diagnosis_id=row[0],
                        service_name=row[1],
                        problem_description=row[2],
                        diagnosis=diagnosis_result.get('diagnosis', ''),
                        root_cause=diagnosis_result.get('root_cause', ''),
                        solutions=diagnosis_result.get('solutions', []),
                        prevention=diagnosis_result.get('prevention', ''),
                        monitoring=diagnosis_result.get('monitoring', ''),
                        status=row[5],
                        created_at=row[6],
                        estimated_resolution_time=diagnosis_result.get('estimated_resolution_time', 'Unknown')
                    ))
                
                return {
                    "diagnoses": diagnoses,
                    "total_count": total_count,
                    "page": page,
                    "page_size": limit,
                    "total_pages": (total_count + limit - 1) // limit
                }
                
        except Exception as e:
            print(f"⚠️ Error getting diagnosis history: {e}")
            return {"diagnoses": [], "total_count": 0, "page": page, "page_size": limit, "total_pages": 0}

    def store_feedback(self, feedback_request: FeedbackRequest) -> Dict[str, Any]:
        """Store feedback for learning improvement"""
        try:
            feedback_id = f"FEED-{datetime.now().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(3).upper()}"
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO feedback (
                        id, diagnosis_id, solution_id, success, feedback_text, 
                        execution_time_seconds
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    feedback_id, feedback_request.diagnosis_id, feedback_request.solution_id,
                    feedback_request.success, feedback_request.feedback, feedback_request.execution_time
                ))
                
                # Update learning data
                if feedback_request.success:
                    self.update_learning_data(feedback_request.diagnosis_id, True, feedback_request.execution_time)
                else:
                    self.update_learning_data(feedback_request.diagnosis_id, False, feedback_request.execution_time)
                
                conn.commit()
            
            return {"feedback_id": feedback_id, "status": "recorded", "message": "Feedback recorded for learning improvement"}
            
        except Exception as e:
            print(f"⚠️ Error storing feedback: {e}")
            return {"status": "error", "message": f"Failed to store feedback: {str(e)}"}

    def update_learning_data(self, diagnosis_id: str, success: bool, execution_time: int):
        """Update learning data for AI improvement"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get problem and solution patterns
                cursor.execute("""
                    SELECT d.problem_description, d.service_name, s.solution_data
                    FROM diagnoses d
                    JOIN solutions s ON d.id = s.diagnosis_id
                    WHERE d.id = ?
                    LIMIT 1
                """, (diagnosis_id,))
                
                result = cursor.fetchone()
                if not result:
                    return
                
                problem_desc, service_name, solution_data_json = result
                solution_data = json.loads(solution_data_json)
                
                problem_pattern = f"{service_name}:{problem_desc[:100]}"
                solution_pattern = solution_data.get('description', '')[:100]
                
                # Update or insert learning data
                cursor.execute("""
                    SELECT id, success_count, failure_count, avg_execution_time
                    FROM learning_data 
                    WHERE problem_pattern = ? AND solution_pattern = ?
                """, (problem_pattern, solution_pattern))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing record
                    old_success = existing[1]
                    old_failure = existing[2]
                    old_avg_time = existing[3]
                    
                    new_success = old_success + (1 if success else 0)
                    new_failure = old_failure + (0 if success else 1)
                    total_attempts = new_success + new_failure
                    
                    # Calculate new average execution time
                    new_avg_time = ((old_avg_time * (total_attempts - 1)) + execution_time) / total_attempts
                    
                    # Calculate confidence score
                    confidence_score = min(new_success / total_attempts, 0.95) if total_attempts > 0 else 0.5
                    
                    cursor.execute("""
                        UPDATE learning_data 
                        SET success_count = ?, failure_count = ?, avg_execution_time = ?, 
                            confidence_score = ?, last_updated = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (new_success, new_failure, new_avg_time, confidence_score, existing[0]))
                else:
                    # Insert new record
                    learning_id = f"LEARN-{datetime.now().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(3).upper()}"
                    success_count = 1 if success else 0
                    failure_count = 0 if success else 1
                    confidence_score = 0.7 if success else 0.3
                    
                    cursor.execute("""
                        INSERT INTO learning_data (
                            id, problem_pattern, solution_pattern, success_count, 
                            failure_count, avg_execution_time, confidence_score
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (learning_id, problem_pattern, solution_pattern, success_count, 
                          failure_count, execution_time, confidence_score))
                
                conn.commit()
                
        except Exception as e:
            print(f"⚠️ Error updating learning data: {e}")

# FastAPI app initialization
app = FastAPI(
    title="ZmartBot Doctor Service",
    description="AI-Powered System Diagnostics & Recovery",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
doctor_service = None

async def get_openai_api_key() -> Optional[str]:
    """Fetch OpenAI API key from API keys manager database"""
    try:
        api_keys_db_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/api_keys.db"
        if not os.path.exists(api_keys_db_path):
            print("⚠️ API keys database not found")
            return None
            
        with sqlite3.connect(api_keys_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT encrypted_key FROM api_keys 
                WHERE service_name = 'openai' AND key_type = 'api_key' AND is_active = 1
            """)
            result = cursor.fetchone()
            
            if result:
                # For now, assuming the key is not encrypted (needs proper decryption)
                # TODO: Implement proper decryption using the encryption key
                encrypted_key = result[0]
                # Return the key as-is for now - this needs proper decryption implementation
                print("✅ OpenAI API key found in database")
                return encrypted_key
            else:
                print("⚠️ No active OpenAI API key found in database")
                return None
                
    except Exception as e:
        print(f"❌ Error fetching OpenAI API key: {e}")
        return None

@app.on_event("startup")
async def startup_event():
    """Initialize the doctor service on startup"""
    global doctor_service
    
    print("🩺 Initializing Doctor Service...")
    
    # Get OpenAI API key from database
    openai_api_key = await get_openai_api_key()
    
    # Initialize the doctor service
    db_path = os.getenv("DOCTOR_DB_PATH", "/Users/dansidanutz/Desktop/ZmartBot/services/doctor-service/doctor.db")
    
    try:
        doctor_service = DoctorService(
            db_path=db_path,
            openai_api_key=openai_api_key
        )
        
        print("✅ Doctor Service initialized successfully")
        print(f"🤖 AI Available: {doctor_service.openai_api_key is not None}")
        print(f"🗄️ Database: {doctor_service.db_path}")
        
    except Exception as e:
        print(f"❌ Failed to initialize Doctor Service: {e}")
        # Create a minimal service instance to prevent crashes
        doctor_service = DoctorService(db_path=db_path, openai_api_key=None)

def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    return request.client.host

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API token"""
    global doctor_service
    if not doctor_service or credentials.credentials != doctor_service.service_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return credentials

# Health endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    global doctor_service
    ai_available = False
    db_connected = False
    
    if doctor_service:
        ai_available = doctor_service.openai_api_key is not None
        db_connected = os.path.exists(doctor_service.db_path)
    
    return {
        "status": "healthy",
        "service": "doctor-service",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ai_available": ai_available,
        "database_connected": db_connected
    }

@app.get("/ready", tags=["Health"])
async def readiness_check():
    """Readiness check endpoint"""
    global doctor_service
    
    if doctor_service is None:
        raise HTTPException(status_code=503, detail="Doctor service not initialized")
        
    try:
        # Test database connection
        with sqlite3.connect(doctor_service.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
        
        return {
            "status": "ready",
            "service": "doctor-service",
            "database": "connected",
            "ai_service": "available" if doctor_service.openai_api_key else "unavailable"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")

# Main API endpoints
@app.post("/api/doctor/diagnose", tags=["Diagnosis"])
async def diagnose_problem(
    request: DiagnoseRequest,
    client_request: Request,
    background_tasks: BackgroundTasks
):
    """Analyze service problem and generate solution"""
    global doctor_service
    
    # Safety check - ensure doctor_service is initialized
    if doctor_service is None:
        raise HTTPException(
            status_code=503, 
            detail="Doctor service not initialized. Please check service startup logs."
        )
    
    client_ip = get_client_ip(client_request)
    user_agent = client_request.headers.get("User-Agent", "")
    
    try:
        print(f"🩺 Received diagnosis request for {request.service_name} from {client_ip}")
        diagnosis_result = await doctor_service.diagnose_problem(request, client_ip, user_agent)
        
        # Add background task to update statistics
        background_tasks.add_task(update_service_statistics, request.service_name, True)
        
        return diagnosis_result
        
    except Exception as e:
        print(f"❌ Diagnosis error: {str(e)}")
        background_tasks.add_task(update_service_statistics, request.service_name, False)
        raise HTTPException(status_code=500, detail=f"Diagnosis failed: {str(e)}")

@app.get("/api/doctor/diagnosis/{diagnosis_id}", tags=["Diagnosis"])
async def get_diagnosis_details(
    diagnosis_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(verify_token)
):
    """Get specific diagnosis details"""
    try:
        with sqlite3.connect(doctor_service.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, service_name, problem_description, problem_level,
                       diagnosis_result, status, created_at, processing_time_seconds
                FROM diagnoses WHERE id = ?
            """, (diagnosis_id,))
            
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Diagnosis not found")
            
            diagnosis_result = json.loads(result[4]) if result[4] else {}
            
            return DiagnosisResponse(
                diagnosis_id=result[0],
                service_name=result[1],
                problem_description=result[2],
                diagnosis=diagnosis_result.get('diagnosis', ''),
                root_cause=diagnosis_result.get('root_cause', ''),
                solutions=diagnosis_result.get('solutions', []),
                prevention=diagnosis_result.get('prevention', ''),
                monitoring=diagnosis_result.get('monitoring', ''),
                status=result[5],
                created_at=result[6],
                estimated_resolution_time=diagnosis_result.get('estimated_resolution_time', 'Unknown')
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get diagnosis: {str(e)}")

@app.post("/api/doctor/execute-solution", tags=["Execution"])
async def execute_solution(
    request: SolutionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(verify_token)
):
    """Execute recommended solution"""
    try:
        result = await doctor_service.execute_solution(
            request.diagnosis_id, 
            request.solution_id, 
            request.confirmation
        )
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Solution execution failed: {str(e)}")

@app.get("/api/doctor/history", tags=["History"])
async def get_diagnosis_history(
    service_name: str = None,
    limit: int = 50,
    status: str = None,
    page: int = 1,
    credentials: HTTPAuthorizationCredentials = Depends(verify_token)
):
    """Get diagnosis history with pagination"""
    try:
        result = doctor_service.get_diagnosis_history(service_name, limit, status, page)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@app.post("/api/doctor/feedback", tags=["Learning"])
async def submit_feedback(
    request: FeedbackRequest,
    credentials: HTTPAuthorizationCredentials = Depends(verify_token)
):
    """Provide feedback on solution effectiveness"""
    try:
        result = doctor_service.store_feedback(request)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store feedback: {str(e)}")

@app.get("/api/doctor/stats", tags=["Statistics"])
async def get_service_statistics(credentials: HTTPAuthorizationCredentials = Depends(verify_token)):
    """Get service statistics and metrics"""
    try:
        with sqlite3.connect(doctor_service.db_path) as conn:
            cursor = conn.cursor()
            
            # Total diagnoses
            cursor.execute("SELECT COUNT(*) FROM diagnoses")
            total_diagnoses = cursor.fetchone()[0]
            
            # Success rate
            cursor.execute("SELECT COUNT(*) FROM diagnoses WHERE status = 'completed'")
            completed_diagnoses = cursor.fetchone()[0]
            
            # Recent activity (last 24 hours)
            cursor.execute("""
                SELECT COUNT(*) FROM diagnoses 
                WHERE created_at > datetime('now', '-24 hours')
            """)
            recent_activity = cursor.fetchone()[0]
            
            # Top problem services
            cursor.execute("""
                SELECT service_name, COUNT(*) as problem_count
                FROM diagnoses 
                WHERE created_at > datetime('now', '-7 days')
                GROUP BY service_name 
                ORDER BY problem_count DESC 
                LIMIT 5
            """)
            top_problem_services = [{"service": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            # Average processing time
            cursor.execute("SELECT AVG(processing_time_seconds) FROM diagnoses WHERE processing_time_seconds IS NOT NULL")
            avg_processing_time = cursor.fetchone()[0] or 0
            
            success_rate = (completed_diagnoses / total_diagnoses * 100) if total_diagnoses > 0 else 0
            
            return {
                "total_diagnoses": total_diagnoses,
                "completed_diagnoses": completed_diagnoses,
                "success_rate": round(success_rate, 2),
                "recent_activity_24h": recent_activity,
                "average_processing_time": round(avg_processing_time, 2),
                "top_problem_services": top_problem_services,
                "ai_available": doctor_service.openai_api_key is not None
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

# Background task functions
async def update_service_statistics(service_name: str, success: bool):
    """Background task to update service statistics"""
    try:
        # This could be expanded to update more detailed statistics
        print(f"📊 Updating statistics for {service_name}: {'success' if success else 'failure'}")
    except Exception as e:
        print(f"⚠️ Failed to update statistics: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="ZmartBot Doctor Service")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8700, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--openai-key", help="OpenAI API key for AI analysis")
    parser.add_argument("--db-path", help="Database file path")
    
    args = parser.parse_args()
    
    # Initialize global doctor service
    global doctor_service
    doctor_service = DoctorService(
        db_path=args.db_path,
        openai_api_key=args.openai_key
    )
    
    print("🩺 Starting ZmartBot Doctor Service...")
    print(f"🌐 Server: http://{args.host}:{args.port}")
    print(f"📚 API Docs: http://{args.host}:{args.port}/docs")
    print(f"🔍 Health: http://{args.host}:{args.port}/health")
    print(f"🤖 AI Available: {doctor_service.openai_api_key is not None}")
    print(f"🗄️  Database: {doctor_service.db_path}")
    
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="warning"
    )

if __name__ == "__main__":
    main()