"""
Zmart Trading Bot Platform - Agents Routes
Trading agent management and operations
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.routes.auth import get_current_active_user, require_role
from src.utils.metrics import record_agent_task, update_agent_status
from src.utils.event_bus import emit_agent_event, EventType

router = APIRouter()

# Pydantic models
class Agent(BaseModel):
    agent_id: str
    name: str
    agent_type: str
    status: str  # "idle", "active", "busy", "error", "maintenance"
    capabilities: List[str]
    config: Dict[str, Any]
    created_at: datetime
    last_heartbeat: datetime
    total_tasks_completed: int
    total_tasks_failed: int
    average_execution_time: float

class AgentConfig(BaseModel):
    name: str
    agent_type: str
    capabilities: List[str]
    config: Dict[str, Any]

class Task(BaseModel):
    task_id: str
    agent_id: str
    task_type: str
    priority: int
    payload: Dict[str, Any]
    status: str  # "pending", "running", "completed", "failed"
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Mock data (replace with database)
MOCK_AGENTS = {
    "orchestration": {
        "agent_id": "orchestration_1",
        "name": "Orchestration Agent",
        "agent_type": "orchestration",
        "status": "active",
        "capabilities": ["task_scheduling", "agent_coordination", "conflict_resolution"],
        "config": {"max_concurrent_tasks": 10},
        "created_at": datetime.utcnow(),
        "last_heartbeat": datetime.utcnow(),
        "total_tasks_completed": 150,
        "total_tasks_failed": 2,
        "average_execution_time": 0.5
    },
    "scoring": {
        "agent_id": "scoring_1",
        "name": "Scoring Agent",
        "agent_type": "scoring",
        "status": "active",
        "capabilities": ["signal_scoring", "confidence_calculation", "risk_assessment"],
        "config": {"confidence_threshold": 0.7},
        "created_at": datetime.utcnow(),
        "last_heartbeat": datetime.utcnow(),
        "total_tasks_completed": 300,
        "total_tasks_failed": 5,
        "average_execution_time": 0.3
    },
    "risk_guard": {
        "agent_id": "risk_guard_1",
        "name": "Risk Guard Agent",
        "agent_type": "risk_guard",
        "status": "active",
        "capabilities": ["risk_monitoring", "circuit_breaker", "position_limits"],
        "config": {"max_drawdown": 0.1, "position_limit": 1000},
        "created_at": datetime.utcnow(),
        "last_heartbeat": datetime.utcnow(),
        "total_tasks_completed": 200,
        "total_tasks_failed": 1,
        "average_execution_time": 0.2
    }
}

MOCK_TASKS = []

@router.get("/agents", response_model=List[Agent])
async def get_agents(
    agent_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get all agents with optional filtering"""
    agents = list(MOCK_AGENTS.values())
    
    # Apply filters
    if agent_type:
        agents = [agent for agent in agents if agent["agent_type"] == agent_type]
    
    if status:
        agents = [agent for agent in agents if agent["status"] == status]
    
    return [Agent(**agent) for agent in agents]

@router.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(
    agent_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get a specific agent by ID"""
    agent = MOCK_AGENTS.get(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return Agent(**agent)

@router.post("/agents", response_model=Agent)
async def create_agent(
    agent_config: AgentConfig,
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """Create a new agent"""
    agent_id = f"{agent_config.agent_type}_{len(MOCK_AGENTS) + 1}"
    
    agent = {
        "agent_id": agent_id,
        "name": agent_config.name,
        "agent_type": agent_config.agent_type,
        "status": "idle",
        "capabilities": agent_config.capabilities,
        "config": agent_config.config,
        "created_at": datetime.utcnow(),
        "last_heartbeat": datetime.utcnow(),
        "total_tasks_completed": 0,
        "total_tasks_failed": 0,
        "average_execution_time": 0.0
    }
    
    MOCK_AGENTS[agent_id] = agent
    
    # Emit agent event
    await emit_agent_event(
        agent_type=agent_config.agent_type,
        event_type=EventType.AGENT_STARTED,
        data={"agent_id": agent_id, "name": agent_config.name}
    )
    
    return Agent(**agent)

@router.put("/agents/{agent_id}/status")
async def update_agent_status_route(
    agent_id: str,
    status: str,
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """Update agent status"""
    agent = MOCK_AGENTS.get(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if status not in ["idle", "active", "busy", "error", "maintenance"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    agent["status"] = status
    
    # Update metrics
    update_agent_status(agent["agent_type"], status == "active")
    
    return {"message": f"Agent {agent_id} status updated to {status}"}

@router.delete("/agents/{agent_id}")
async def delete_agent(
    agent_id: str,
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """Delete an agent"""
    agent = MOCK_AGENTS.get(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    del MOCK_AGENTS[agent_id]
    
    # Emit agent event
    await emit_agent_event(
        agent_type=agent["agent_type"],
        event_type=EventType.AGENT_STOPPED,
        data={"agent_id": agent_id}
    )
    
    return {"message": f"Agent {agent_id} deleted"}

@router.post("/agents/{agent_id}/tasks", response_model=Task)
async def submit_task(
    agent_id: str,
    task_type: str,
    payload: Dict[str, Any],
    priority: int = 2,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Submit a task to an agent"""
    agent = MOCK_AGENTS.get(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if agent["status"] not in ["active", "idle"]:
        raise HTTPException(status_code=400, detail="Agent is not available")
    
    # Create task
    task_id = f"task_{len(MOCK_TASKS) + 1}_{datetime.utcnow().timestamp()}"
    task = {
        "task_id": task_id,
        "agent_id": agent_id,
        "task_type": task_type,
        "priority": priority,
        "payload": payload,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "started_at": None,
        "completed_at": None,
        "result": None,
        "error": None
    }
    
    MOCK_TASKS.append(task)
    
    # Update agent status
    agent["status"] = "busy"
    agent["last_heartbeat"] = datetime.utcnow()
    
    # Record metrics
    record_agent_task(agent["agent_type"], "submitted", 0.0)
    
    return Task(**task)

@router.get("/tasks", response_model=List[Task])
async def get_tasks(
    agent_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get tasks with optional filtering"""
    tasks = MOCK_TASKS.copy()
    
    # Apply filters
    if agent_id:
        tasks = [task for task in tasks if task["agent_id"] == agent_id]
    
    if status:
        tasks = [task for task in tasks if task["status"] == status]
    
    # Sort by created_at (newest first) and limit
    tasks.sort(key=lambda x: x["created_at"], reverse=True)
    tasks = tasks[:limit]
    
    return [Task(**task) for task in tasks]

@router.get("/tasks/{task_id}", response_model=Task)
async def get_task(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get a specific task by ID"""
    task = next((t for t in MOCK_TASKS if t["task_id"] == task_id), None)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return Task(**task)

@router.put("/tasks/{task_id}/status")
async def update_task_status(
    task_id: str,
    status: str,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Update task status"""
    task = next((t for t in MOCK_TASKS if t["task_id"] == task_id), None)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if status not in ["pending", "running", "completed", "failed"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    task["status"] = status
    
    if status == "running" and not task["started_at"]:
        task["started_at"] = datetime.utcnow()
    elif status in ["completed", "failed"] and not task["completed_at"]:
        task["completed_at"] = datetime.utcnow()
    
    if result:
        task["result"] = result
    
    if error:
        task["error"] = error
    
    # Update agent metrics
    agent = MOCK_AGENTS.get(task["agent_id"])
    if agent:
        if status == "completed":
            agent["total_tasks_completed"] += 1
            agent["status"] = "idle"
        elif status == "failed":
            agent["total_tasks_failed"] += 1
            agent["status"] = "idle"
        
        # Calculate execution time
        if task["started_at"] and task["completed_at"]:
            execution_time = (task["completed_at"] - task["started_at"]).total_seconds()
            agent["average_execution_time"] = (
                (agent["average_execution_time"] * (agent["total_tasks_completed"] - 1) + execution_time) /
                agent["total_tasks_completed"]
            )
    
    # Record metrics
    execution_time = 0.0
    if task["started_at"] and task["completed_at"]:
        execution_time = (task["completed_at"] - task["started_at"]).total_seconds()
    
    record_agent_task(agent["agent_type"] if agent else "unknown", status, execution_time)
    
    return {"message": f"Task {task_id} status updated to {status}"}

@router.get("/agents/{agent_id}/heartbeat")
async def agent_heartbeat(
    agent_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Update agent heartbeat"""
    agent = MOCK_AGENTS.get(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent["last_heartbeat"] = datetime.utcnow()
    
    # Emit heartbeat event
    await emit_agent_event(
        agent_type=agent["agent_type"],
        event_type=EventType.AGENT_HEARTBEAT,
        data={"agent_id": agent_id, "timestamp": datetime.utcnow().isoformat()}
    )
    
    return {"message": "Heartbeat updated", "timestamp": agent["last_heartbeat"]}

@router.get("/agents/statistics")
async def get_agent_statistics(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get agent statistics"""
    total_agents = len(MOCK_AGENTS)
    active_agents = len([a for a in MOCK_AGENTS.values() if a["status"] == "active"])
    idle_agents = len([a for a in MOCK_AGENTS.values() if a["status"] == "idle"])
    busy_agents = len([a for a in MOCK_AGENTS.values() if a["status"] == "busy"])
    
    total_tasks = len(MOCK_TASKS)
    completed_tasks = len([t for t in MOCK_TASKS if t["status"] == "completed"])
    failed_tasks = len([t for t in MOCK_TASKS if t["status"] == "failed"])
    
    return {
        "total_agents": total_agents,
        "active_agents": active_agents,
        "idle_agents": idle_agents,
        "busy_agents": busy_agents,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "failed_tasks": failed_tasks,
        "success_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    }

@router.get("/agents/types")
async def get_agent_types(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get available agent types"""
    agent_types = list(set(agent["agent_type"] for agent in MOCK_AGENTS.values()))
    
    return {
        "agent_types": agent_types,
        "total_types": len(agent_types)
    }

@router.post("/agents/{agent_id}/restart")
async def restart_agent(
    agent_id: str,
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """Restart an agent"""
    agent = MOCK_AGENTS.get(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Reset agent status
    agent["status"] = "idle"
    agent["last_heartbeat"] = datetime.utcnow()
    
    # Emit restart event
    await emit_agent_event(
        agent_type=agent["agent_type"],
        event_type=EventType.AGENT_STARTED,
        data={"agent_id": agent_id, "restarted": True}
    )
    
    return {"message": f"Agent {agent_id} restarted"}

@router.get("/agents/{agent_id}/capabilities")
async def get_agent_capabilities(
    agent_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get agent capabilities"""
    agent = MOCK_AGENTS.get(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {
        "agent_id": agent_id,
        "capabilities": agent["capabilities"],
        "total_capabilities": len(agent["capabilities"])
    }

@router.put("/agents/{agent_id}/config")
async def update_agent_config(
    agent_id: str,
    config: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """Update agent configuration"""
    agent = MOCK_AGENTS.get(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent["config"].update(config)
    
    return {"message": f"Agent {agent_id} configuration updated"}

@router.get("/agents/{agent_id}/performance")
async def get_agent_performance(
    agent_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get agent performance metrics"""
    agent = MOCK_AGENTS.get(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {
        "agent_id": agent_id,
        "total_tasks_completed": agent["total_tasks_completed"],
        "total_tasks_failed": agent["total_tasks_failed"],
        "average_execution_time": agent["average_execution_time"],
        "success_rate": (
            agent["total_tasks_completed"] / 
            (agent["total_tasks_completed"] + agent["total_tasks_failed"]) * 100
        ) if (agent["total_tasks_completed"] + agent["total_tasks_failed"]) > 0 else 0
    } 