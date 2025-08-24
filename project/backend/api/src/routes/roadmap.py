"""
Roadmap API Routes
Provides orchestration for development progress tracking and deployment automation
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import json
import os
import subprocess
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/roadmap", tags=["Roadmap"])

# Development phases and milestones
DEVELOPMENT_PHASES = {
    "phase_1": {
        "name": "Enhanced Alerts System",
        "status": "completed",
        "completion_date": "2025-08-19",
        "description": "Real-time cross-signals and pattern detection",
        "features": [
            "21 Technical Indicators",
            "Cross-Signal Detection", 
            "Real-time Updates",
            "Cooldown Management",
            "Market Sentiment Analysis"
        ],
        "progress": 100
    },
    "phase_2": {
        "name": "Advanced Analytics & AI",
        "status": "in_progress",
        "start_date": "2025-08-20",
        "description": "Machine learning and predictive modeling",
        "features": [
            "AI Pattern Recognition",
            "Predictive Scoring",
            "Risk Assessment",
            "Performance Analytics",
            "Self-Learning Models"
        ],
        "progress": 35
    },
    "phase_3": {
        "name": "AI Trading & Automation",
        "status": "planned",
        "planned_start": "2025-09-01",
        "description": "Automated trading with AI agents",
        "features": [
            "Automated Trading Bots",
            "Portfolio Management",
            "Risk Management",
            "Multi-Exchange Support",
            "Real-time Execution"
        ],
        "progress": 0
    }
}

# Deployment trains (major releases)
DEPLOYMENT_TRAINS = {
    "train_alpha": {
        "name": "Alpha Train",
        "version": "1.0.0-alpha",
        "status": "deployed",
        "deployment_date": "2025-08-15",
        "features": ["Enhanced Alerts", "Basic Analytics"],
        "wagon_count": 3
    },
    "train_beta": {
        "name": "Beta Train", 
        "version": "1.0.0-beta",
        "status": "building",
        "planned_deployment": "2025-08-25",
        "features": ["AI Integration", "Advanced Analytics"],
        "wagon_count": 5
    },
    "train_production": {
        "name": "Production Train",
        "version": "1.0.0",
        "status": "planned",
        "planned_deployment": "2025-09-15",
        "features": ["Full AI Trading", "Complete Automation"],
        "wagon_count": 8
    }
}

# Development wagons (feature modules)
DEVELOPMENT_WAGONS = {
    "wagon_enhanced_alerts": {
        "name": "Enhanced Alerts Wagon",
        "train": "train_alpha",
        "status": "deployed",
        "deployment_date": "2025-08-15",
        "features": ["21 Indicators", "Cross-Signals", "Real-time Updates"],
        "git_commits": 45,
        "test_coverage": 92
    },
    "wagon_market_sentiment": {
        "name": "Market Sentiment Wagon",
        "train": "train_alpha", 
        "status": "deployed",
        "deployment_date": "2025-08-17",
        "features": ["Sentiment Analysis", "Percentage Breakdowns"],
        "git_commits": 23,
        "test_coverage": 88
    },
    "wagon_ai_patterns": {
        "name": "AI Pattern Recognition Wagon",
        "train": "train_beta",
        "status": "building",
        "estimated_completion": "2025-08-22",
        "features": ["ML Models", "Pattern Detection"],
        "git_commits": 67,
        "test_coverage": 75
    },
    "wagon_predictive_scoring": {
        "name": "Predictive Scoring Wagon",
        "train": "train_beta",
        "status": "building", 
        "estimated_completion": "2025-08-24",
        "features": ["Win Rate Prediction", "Risk Assessment"],
        "git_commits": 34,
        "test_coverage": 82
    }
}

@router.get("/phases")
async def get_development_phases():
    """Get all development phases and their progress"""
    return {
        "ok": True,
        "data": {
            "phases": DEVELOPMENT_PHASES,
            "total_phases": len(DEVELOPMENT_PHASES),
            "completed_phases": len([p for p in DEVELOPMENT_PHASES.values() if p["status"] == "completed"]),
            "in_progress_phases": len([p for p in DEVELOPMENT_PHASES.values() if p["status"] == "in_progress"]),
            "overall_progress": sum(p["progress"] for p in DEVELOPMENT_PHASES.values()) // len(DEVELOPMENT_PHASES)
        }
    }

@router.get("/trains")
async def get_deployment_trains():
    """Get all deployment trains and their status"""
    return {
        "ok": True,
        "data": {
            "trains": DEPLOYMENT_TRAINS,
            "total_trains": len(DEPLOYMENT_TRAINS),
            "deployed_trains": len([t for t in DEPLOYMENT_TRAINS.values() if t["status"] == "deployed"]),
            "building_trains": len([t for t in DEPLOYMENT_TRAINS.values() if t["status"] == "building"]),
            "total_wagons": sum(t["wagon_count"] for t in DEPLOYMENT_TRAINS.values())
        }
    }

@router.get("/wagons")
async def get_development_wagons():
    """Get all development wagons and their status"""
    return {
        "ok": True,
        "data": {
            "wagons": DEVELOPMENT_WAGONS,
            "total_wagons": len(DEVELOPMENT_WAGONS),
            "deployed_wagons": len([w for w in DEVELOPMENT_WAGONS.values() if w["status"] == "deployed"]),
            "building_wagons": len([w for w in DEVELOPMENT_WAGONS.values() if w["status"] == "building"]),
            "total_commits": sum(w["git_commits"] for w in DEVELOPMENT_WAGONS.values()),
            "avg_test_coverage": sum(w["test_coverage"] for w in DEVELOPMENT_WAGONS.values()) // len(DEVELOPMENT_WAGONS)
        }
    }

@router.get("/overview")
async def get_roadmap_overview():
    """Get comprehensive roadmap overview"""
    return {
        "ok": True,
        "data": {
            "project_name": "ZmartBot Trading Platform",
            "current_version": "1.0.0-alpha",
            "last_updated": datetime.now().isoformat(),
            "development_phases": {
                "total": len(DEVELOPMENT_PHASES),
                "completed": len([p for p in DEVELOPMENT_PHASES.values() if p["status"] == "completed"]),
                "in_progress": len([p for p in DEVELOPMENT_PHASES.values() if p["status"] == "in_progress"]),
                "planned": len([p for p in DEVELOPMENT_PHASES.values() if p["status"] == "planned"])
            },
            "deployment_trains": {
                "total": len(DEPLOYMENT_TRAINS),
                "deployed": len([t for t in DEPLOYMENT_TRAINS.values() if t["status"] == "deployed"]),
                "building": len([t for t in DEPLOYMENT_TRAINS.values() if t["status"] == "building"]),
                "planned": len([t for t in DEPLOYMENT_TRAINS.values() if t["status"] == "planned"])
            },
            "development_wagons": {
                "total": len(DEVELOPMENT_WAGONS),
                "deployed": len([w for w in DEVELOPMENT_WAGONS.values() if w["status"] == "deployed"]),
                "building": len([w for w in DEVELOPMENT_WAGONS.values() if w["status"] == "building"]),
                "total_commits": sum(w["git_commits"] for w in DEVELOPMENT_WAGONS.values()),
                "avg_test_coverage": sum(w["test_coverage"] for w in DEVELOPMENT_WAGONS.values()) // len(DEVELOPMENT_WAGONS)
            },
            "next_milestones": [
                {
                    "name": "AI Pattern Recognition Completion",
                    "date": "2025-08-22",
                    "type": "wagon_deployment"
                },
                {
                    "name": "Beta Train Deployment",
                    "date": "2025-08-25", 
                    "type": "train_deployment"
                },
                {
                    "name": "Phase 2 Completion",
                    "date": "2025-08-30",
                    "type": "phase_completion"
                }
            ]
        }
    }

@router.post("/create-wagon")
async def create_development_wagon(wagon_data: Dict[str, Any]):
    """Create a new development wagon"""
    wagon_id = f"wagon_{wagon_data.get('name', 'new').lower().replace(' ', '_')}"
    
    new_wagon = {
        "name": wagon_data.get("name", "New Wagon"),
        "train": wagon_data.get("train", "train_beta"),
        "status": "building",
        "estimated_completion": wagon_data.get("estimated_completion", "2025-08-30"),
        "features": wagon_data.get("features", []),
        "git_commits": 0,
        "test_coverage": 0,
        "created_at": datetime.now().isoformat()
    }
    
    DEVELOPMENT_WAGONS[wagon_id] = new_wagon
    
    logger.info(f"Created new development wagon: {wagon_id}")
    
    return {
        "ok": True,
        "data": {
            "wagon_id": wagon_id,
            "wagon": new_wagon,
            "message": f"Development wagon '{new_wagon['name']}' created successfully"
        }
    }

@router.post("/deploy-wagon/{wagon_id}")
async def deploy_wagon(wagon_id: str, background_tasks: BackgroundTasks):
    """Deploy a development wagon"""
    if wagon_id not in DEVELOPMENT_WAGONS:
        raise HTTPException(status_code=404, detail=f"Wagon {wagon_id} not found")
    
    wagon = DEVELOPMENT_WAGONS[wagon_id]
    if wagon["status"] == "deployed":
        raise HTTPException(status_code=400, detail=f"Wagon {wagon_id} is already deployed")
    
    # Update wagon status
    wagon["status"] = "deployed"
    wagon["deployment_date"] = datetime.now().isoformat()
    
    # Background task to simulate deployment process
    background_tasks.add_task(simulate_wagon_deployment, wagon_id, wagon)
    
    logger.info(f"Deploying wagon: {wagon_id}")
    
    return {
        "ok": True,
        "data": {
            "wagon_id": wagon_id,
            "status": "deploying",
            "message": f"Wagon '{wagon['name']}' deployment started"
        }
    }

@router.post("/deploy-train/{train_id}")
async def deploy_train(train_id: str, background_tasks: BackgroundTasks):
    """Deploy a complete train with all its wagons"""
    if train_id not in DEPLOYMENT_TRAINS:
        raise HTTPException(status_code=404, detail=f"Train {train_id} not found")
    
    train = DEPLOYMENT_TRAINS[train_id]
    if train["status"] == "deployed":
        raise HTTPException(status_code=400, detail=f"Train {train_id} is already deployed")
    
    # Get all wagons for this train
    train_wagons = [w for w in DEVELOPMENT_WAGONS.values() if w["train"] == train_id]
    
    # Check if all wagons are ready
    undeployed_wagons = [w for w in train_wagons if w["status"] != "deployed"]
    if undeployed_wagons:
        raise HTTPException(
            status_code=400, 
            detail=f"Train cannot be deployed. Undeployed wagons: {[w['name'] for w in undeployed_wagons]}"
        )
    
    # Update train status
    train["status"] = "deployed"
    train["deployment_date"] = datetime.now().isoformat()
    
    # Background task to simulate train deployment
    background_tasks.add_task(simulate_train_deployment, train_id, train, train_wagons)
    
    logger.info(f"Deploying train: {train_id} with {len(train_wagons)} wagons")
    
    return {
        "ok": True,
        "data": {
            "train_id": train_id,
            "status": "deploying",
            "wagon_count": len(train_wagons),
            "message": f"Train '{train['name']}' deployment started with {len(train_wagons)} wagons"
        }
    }

@router.get("/git-status")
async def get_git_status():
    """Get current git status and commit information"""
    try:
        # Get current git status
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent.parent
        )
        
        # Get recent commits
        commits_result = subprocess.run(
            ["git", "log", "--oneline", "-10"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent.parent
        )
        
        # Get current branch
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent.parent
        )
        
        return {
            "ok": True,
            "data": {
                "current_branch": branch_result.stdout.strip(),
                "modified_files": len([line for line in result.stdout.split('\n') if line.strip()]),
                "recent_commits": commits_result.stdout.strip().split('\n')[:5],
                "last_updated": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error getting git status: {e}")
        return {
            "ok": False,
            "error": "Could not retrieve git status"
        }

async def simulate_wagon_deployment(wagon_id: str, wagon: Dict[str, Any]):
    """Simulate wagon deployment process"""
    await asyncio.sleep(2)  # Simulate deployment time
    logger.info(f"Wagon {wagon_id} deployment completed")

async def simulate_train_deployment(train_id: str, train: Dict[str, Any], wagons: List[Dict[str, Any]]):
    """Simulate train deployment process"""
    await asyncio.sleep(5)  # Simulate deployment time
    logger.info(f"Train {train_id} deployment completed with {len(wagons)} wagons")
