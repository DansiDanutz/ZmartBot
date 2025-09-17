#!/usr/bin/env python3
"""
Blockchain API Routes
Provides endpoints for blockchain data access
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from src.services.blockchain_agent import BlockchainAgent

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize blockchain agent
blockchain_agent = BlockchainAgent()

@router.get("/status")
async def get_blockchain_status():
    """Get blockchain agent status"""
    try:
        status = {
            "initialized": blockchain_agent.is_ready(),
            "networks": {
                "ethereum": {
                    "name": "Ethereum",
                    "api_key_configured": bool(blockchain_agent.etherscan_api_key),
                    "base_url": blockchain_agent.networks["ethereum"].base_url
                },
                "tron": {
                    "name": "TRON",
                    "api_key_configured": bool(blockchain_agent.tronscan_api_key),
                    "base_url": blockchain_agent.networks["tron"].base_url
                },
                "solana": {
                    "name": "Solana",
                    "api_key_configured": bool(blockchain_agent.solscan_api_key),
                    "base_url": blockchain_agent.networks["solana"].base_url
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "status": "success",
            "data": status
        }
        
    except Exception as e:
        logger.error(f"Error getting blockchain status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get blockchain status: {str(e)}")

@router.post("/initialize")
async def initialize_blockchain_agent():
    """Initialize blockchain agent"""
    try:
        success = await blockchain_agent.initialize()
        
        return {
            "status": "success" if success else "failed",
            "initialized": success,
            "message": "Blockchain agent initialized successfully" if success else "Failed to initialize blockchain agent",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error initializing blockchain agent: {e}")
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")

@router.get("/ethereum")
async def get_ethereum_data(
    address: Optional[str] = Query(None, description="Ethereum address to query")
):
    """Get Ethereum blockchain data"""
    try:
        data = await blockchain_agent.get_ethereum_data(address)
        
        return {
            "status": "success",
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting Ethereum data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get Ethereum data: {str(e)}")

@router.get("/tron")
async def get_tron_data(
    address: Optional[str] = Query(None, description="TRON address to query")
):
    """Get TRON blockchain data"""
    try:
        data = await blockchain_agent.get_tron_data(address)
        
        return {
            "status": "success",
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting TRON data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get TRON data: {str(e)}")

@router.get("/solana")
async def get_solana_data(
    address: Optional[str] = Query(None, description="Solana address to query")
):
    """Get Solana blockchain data"""
    try:
        data = await blockchain_agent.get_solana_data(address)
        
        return {
            "status": "success",
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting Solana data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get Solana data: {str(e)}")

@router.get("/multi-chain")
async def get_multi_chain_data(
    ethereum_address: Optional[str] = Query(None, description="Ethereum address"),
    tron_address: Optional[str] = Query(None, description="TRON address"),
    solana_address: Optional[str] = Query(None, description="Solana address")
):
    """Get data from all supported blockchains"""
    try:
        addresses = {}
        if ethereum_address:
            addresses["ethereum"] = ethereum_address
        if tron_address:
            addresses["tron"] = tron_address
        if solana_address:
            addresses["solana"] = solana_address
        
        data = await blockchain_agent.get_multi_chain_data(addresses if addresses else None)
        
        return {
            "status": "success",
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting multi-chain data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get multi-chain data: {str(e)}")

@router.get("/ethereum/address/{address}")
async def get_ethereum_address_info(address: str):
    """Get specific Ethereum address information"""
    try:
        data = await blockchain_agent.get_ethereum_data(address)
        
        return {
            "status": "success",
            "address": address,
            "network": "ethereum",
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting Ethereum address info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get Ethereum address info: {str(e)}")

@router.get("/tron/address/{address}")
async def get_tron_address_info(address: str):
    """Get specific TRON address information"""
    try:
        data = await blockchain_agent.get_tron_data(address)
        
        return {
            "status": "success",
            "address": address,
            "network": "tron",
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting TRON address info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get TRON address info: {str(e)}")

@router.get("/solana/address/{address}")
async def get_solana_address_info(address: str):
    """Get specific Solana address information"""
    try:
        data = await blockchain_agent.get_solana_data(address)
        
        return {
            "status": "success",
            "address": address,
            "network": "solana",
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting Solana address info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get Solana address info: {str(e)}")

@router.get("/ethereum/transactions/{address}")
async def get_ethereum_transactions(
    address: str,
    limit: int = Query(10, description="Number of transactions to return", ge=1, le=100)
):
    """Get Ethereum transactions for an address"""
    try:
        data = await blockchain_agent.get_ethereum_data(address)
        transactions = data.get("transactions", [])[:limit]
        
        return {
            "status": "success",
            "address": address,
            "network": "ethereum",
            "transactions": transactions,
            "count": len(transactions),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting Ethereum transactions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get Ethereum transactions: {str(e)}")

@router.get("/tron/transactions/{address}")
async def get_tron_transactions(
    address: str,
    limit: int = Query(10, description="Number of transactions to return", ge=1, le=100)
):
    """Get TRON transactions for an address"""
    try:
        data = await blockchain_agent.get_tron_data(address)
        transactions = data.get("transactions", [])[:limit]
        
        return {
            "status": "success",
            "address": address,
            "network": "tron",
            "transactions": transactions,
            "count": len(transactions),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting TRON transactions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get TRON transactions: {str(e)}")

@router.get("/solana/transactions/{address}")
async def get_solana_transactions(
    address: str,
    limit: int = Query(10, description="Number of transactions to return", ge=1, le=100)
):
    """Get Solana transactions for an address"""
    try:
        data = await blockchain_agent.get_solana_data(address)
        transactions = data.get("transactions", [])[:limit]
        
        return {
            "status": "success",
            "address": address,
            "network": "solana",
            "transactions": transactions,
            "count": len(transactions),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting Solana transactions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get Solana transactions: {str(e)}")

@router.get("/ethereum/tokens/{address}")
async def get_ethereum_tokens(address: str):
    """Get Ethereum tokens for an address"""
    try:
        data = await blockchain_agent.get_ethereum_data(address)
        tokens = data.get("tokens", [])
        
        return {
            "status": "success",
            "address": address,
            "network": "ethereum",
            "tokens": tokens,
            "count": len(tokens),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting Ethereum tokens: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get Ethereum tokens: {str(e)}")

@router.get("/tron/tokens/{address}")
async def get_tron_tokens(address: str):
    """Get TRON tokens for an address"""
    try:
        data = await blockchain_agent.get_tron_data(address)
        tokens = data.get("tokens", [])
        
        return {
            "status": "success",
            "address": address,
            "network": "tron",
            "tokens": tokens,
            "count": len(tokens),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting TRON tokens: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get TRON tokens: {str(e)}")

@router.get("/solana/tokens/{address}")
async def get_solana_tokens(address: str):
    """Get Solana tokens for an address"""
    try:
        data = await blockchain_agent.get_solana_data(address)
        tokens = data.get("tokens", [])
        
        return {
            "status": "success",
            "address": address,
            "network": "solana",
            "tokens": tokens,
            "count": len(tokens),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting Solana tokens: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get Solana tokens: {str(e)}")

@router.get("/networks/metrics")
async def get_network_metrics():
    """Get metrics for all supported networks"""
    try:
        # Get metrics for each network
        ethereum_metrics = await blockchain_agent._get_ethereum_metrics()
        tron_metrics = await blockchain_agent._get_tron_metrics()
        solana_metrics = await blockchain_agent._get_solana_metrics()
        
        metrics = {
            "ethereum": ethereum_metrics,
            "tron": tron_metrics,
            "solana": solana_metrics,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "status": "success",
            "metrics": metrics
        }
        
    except Exception as e:
        logger.error(f"Error getting network metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get network metrics: {str(e)}")

@router.get("/test-connections")
async def test_blockchain_connections():
    """Test connections to all blockchain APIs"""
    try:
        # Test each API connection
        ethereum_status = await blockchain_agent._test_etherscan_api()
        tron_status = await blockchain_agent._test_tronscan_api()
        solana_status = await blockchain_agent._test_solscan_api()
        
        connections = {
            "ethereum": {
                "status": "available" if ethereum_status else "unavailable",
                "api": "Etherscan",
                "base_url": blockchain_agent.networks["ethereum"].base_url
            },
            "tron": {
                "status": "available" if tron_status else "unavailable",
                "api": "Tronscan",
                "base_url": blockchain_agent.networks["tron"].base_url
            },
            "solana": {
                "status": "available" if solana_status else "unavailable",
                "api": "Solscan",
                "base_url": blockchain_agent.networks["solana"].base_url
            }
        }
        
        return {
            "status": "success",
            "connections": connections,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error testing blockchain connections: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test connections: {str(e)}") 