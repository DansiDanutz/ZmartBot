#!/usr/bin/env python3
"""
Blockchain Agent Service
Multi-chain blockchain data fetching and analysis for ETH, TRON, and SOL
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import aiohttp
import requests
from web3 import Web3
from web3.exceptions import Web3Exception

logger = logging.getLogger(__name__)

@dataclass
class BlockchainConfig:
    """Configuration for blockchain networks"""
    name: str
    api_key: str
    base_url: str
    chain_id: int
    currency_symbol: str
    decimals: int

@dataclass
class TransactionData:
    """Blockchain transaction data"""
    tx_hash: str
    from_address: str
    to_address: str
    value: float
    gas_price: Optional[float]
    gas_used: Optional[int]
    block_number: int
    timestamp: datetime
    status: str
    fee: Optional[float]

@dataclass
class TokenData:
    """Token information"""
    contract_address: str
    name: str
    symbol: str
    decimals: int
    total_supply: float
    price_usd: Optional[float]
    market_cap: Optional[float]
    volume_24h: Optional[float]

@dataclass
class BlockchainMetrics:
    """Blockchain network metrics"""
    network: str
    total_transactions: int
    active_addresses: int
    average_gas_price: float
    network_hashrate: Optional[float]
    block_time: float
    total_value_locked: Optional[float]
    timestamp: datetime

class BlockchainAgent:
    """Multi-chain blockchain data agent"""
    
    def __init__(self):
        # API Keys
        self.etherscan_api_key = "6ISB4WXGSAVFGAVZW37F3JS334HRI9GDXH"
        self.solscan_api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MzkzOTUxMDIwMDgsImVtYWlsIjoic2VtZWJpdGNvaW5AZ21haWwuY29tIiwiYWN0aW9uIjoidG9rZW4tYXBpIiwiYXBpVmVyc2lvbiI6InYyIiwiaWF0IjoxNzM5Mzk1MTAyfQ.IgmEZ2khtzJLBVChkIO168gmSjXYFGzgJWr-e_78eWI"
        self.tronscan_api_key = "162c63fa-ae63-4cd2-89e4-d372917c915c"
        
        # Network configurations
        self.networks = {
            "ethereum": BlockchainConfig(
                name="Ethereum",
                api_key=self.etherscan_api_key,
                base_url="https://api.etherscan.io/api",
                chain_id=1,
                currency_symbol="ETH",
                decimals=18
            ),
            "tron": BlockchainConfig(
                name="TRON",
                api_key=self.tronscan_api_key,
                base_url="https://api.tronscan.org/api",
                chain_id=1,
                currency_symbol="TRX",
                decimals=6
            ),
            "solana": BlockchainConfig(
                name="Solana",
                api_key=self.solscan_api_key,
                base_url="https://public-api.solscan.io",
                chain_id=101,
                currency_symbol="SOL",
                decimals=9
            )
        }
        
        # Web3 connections
        self.web3_connections = {}
        self.initialized = False
        
    async def initialize(self) -> bool:
        """Initialize blockchain agent"""
        try:
            logger.info("Initializing Blockchain Agent...")
            
            # Initialize Web3 connections
            await self._initialize_web3_connections()
            
            # Test API connections
            await self._test_api_connections()
            
            self.initialized = True
            logger.info("✅ Blockchain Agent initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Blockchain Agent: {e}")
            return False
    
    async def _initialize_web3_connections(self):
        """Initialize Web3 connections for each network"""
        try:
            # Ethereum Web3 connection
            ethereum_provider = "https://mainnet.infura.io/v3/your-project-id"  # Replace with your Infura project ID
            self.web3_connections["ethereum"] = Web3(Web3.HTTPProvider(ethereum_provider))
            
            # TRON Web3 connection (using TronGrid)
            tron_provider = "https://api.trongrid.io"
            self.web3_connections["tron"] = Web3(Web3.HTTPProvider(tron_provider))
            
            # Solana connection (using public RPC)
            solana_provider = "https://api.mainnet-beta.solana.com"
            self.web3_connections["solana"] = Web3(Web3.HTTPProvider(solana_provider))
            
            logger.info("✅ Web3 connections initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Web3 connection initialization failed: {e}")
    
    async def _test_api_connections(self):
        """Test API connections for all networks"""
        try:
            # Test Etherscan API
            eth_status = await self._test_etherscan_api()
            logger.info(f"Etherscan API: {'✅ Available' if eth_status else '❌ Unavailable'}")
            
            # Test Solscan API
            sol_status = await self._test_solscan_api()
            logger.info(f"Solscan API: {'✅ Available' if sol_status else '❌ Unavailable'}")
            
            # Test Tronscan API
            tron_status = await self._test_tronscan_api()
            logger.info(f"Tronscan API: {'✅ Available' if tron_status else '❌ Unavailable'}")
            
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
    
    async def _test_etherscan_api(self) -> bool:
        """Test Etherscan API connection"""
        try:
            url = f"{self.networks['ethereum'].base_url}?module=proxy&action=eth_blockNumber&apikey={self.etherscan_api_key}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def _test_solscan_api(self) -> bool:
        """Test Solscan API connection"""
        try:
            url = f"{self.networks['solana'].base_url}/account/11111111111111111111111111111112"
            headers = {"Authorization": f"Bearer {self.solscan_api_key}"}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def _test_tronscan_api(self) -> bool:
        """Test Tronscan API connection"""
        try:
            url = f"{self.networks['tron'].base_url}/system/status"
            headers = {"TRON-PRO-API-KEY": self.tronscan_api_key}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def get_ethereum_data(self, address: Optional[str] = None) -> Dict[str, Any]:
        """Get Ethereum blockchain data"""
        try:
            data = {
                "network": "ethereum",
                "timestamp": datetime.now().isoformat(),
                "metrics": await self._get_ethereum_metrics(),
                "transactions": [],
                "tokens": []
            }
            
            if address:
                data["address_info"] = await self._get_ethereum_address_info(address)
                data["transactions"] = await self._get_ethereum_transactions(address)
                data["tokens"] = await self._get_ethereum_tokens(address)
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting Ethereum data: {e}")
            return {"error": str(e)}
    
    async def get_tron_data(self, address: Optional[str] = None) -> Dict[str, Any]:
        """Get TRON blockchain data"""
        try:
            data = {
                "network": "tron",
                "timestamp": datetime.now().isoformat(),
                "metrics": await self._get_tron_metrics(),
                "transactions": [],
                "tokens": []
            }
            
            if address:
                data["address_info"] = await self._get_tron_address_info(address)
                data["transactions"] = await self._get_tron_transactions(address)
                data["tokens"] = await self._get_tron_tokens(address)
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting TRON data: {e}")
            return {"error": str(e)}
    
    async def get_solana_data(self, address: Optional[str] = None) -> Dict[str, Any]:
        """Get Solana blockchain data"""
        try:
            data = {
                "network": "solana",
                "timestamp": datetime.now().isoformat(),
                "metrics": await self._get_solana_metrics(),
                "transactions": [],
                "tokens": []
            }
            
            if address:
                data["address_info"] = await self._get_solana_address_info(address)
                data["transactions"] = await self._get_solana_transactions(address)
                data["tokens"] = await self._get_solana_tokens(address)
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting Solana data: {e}")
            return {"error": str(e)}
    
    async def _get_ethereum_metrics(self) -> Dict[str, Any]:
        """Get Ethereum network metrics"""
        try:
            # Get latest block
            url = f"{self.networks['ethereum'].base_url}?module=proxy&action=eth_blockNumber&apikey={self.etherscan_api_key}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        latest_block = int(data.get("result", "0x0"), 16)
                        
                        # Get gas price
                        gas_url = f"{self.networks['ethereum'].base_url}?module=gastracker&action=gasoracle&apikey={self.etherscan_api_key}"
                        async with session.get(gas_url) as gas_response:
                            gas_data = await gas_response.json()
                            gas_price = gas_data.get("result", {}).get("SafeGasPrice", "0")
                        
                        return {
                            "latest_block": latest_block,
                            "gas_price_gwei": int(gas_price),
                            "network_status": "active"
                        }
            
            return {"error": "Failed to fetch Ethereum metrics"}
            
        except Exception as e:
            logger.error(f"Error getting Ethereum metrics: {e}")
            return {"error": str(e)}
    
    async def _get_tron_metrics(self) -> Dict[str, Any]:
        """Get TRON network metrics"""
        try:
            url = f"{self.networks['tron'].base_url}/system/status"
            headers = {"TRON-PRO-API-KEY": self.tronscan_api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "latest_block": data.get("block", 0),
                            "total_transactions": data.get("totalTransaction", 0),
                            "network_status": "active"
                        }
            
            return {"error": "Failed to fetch TRON metrics"}
            
        except Exception as e:
            logger.error(f"Error getting TRON metrics: {e}")
            return {"error": str(e)}
    
    async def _get_solana_metrics(self) -> Dict[str, Any]:
        """Get Solana network metrics"""
        try:
            url = f"{self.networks['solana'].base_url}/cluster-nodes"
            headers = {"Authorization": f"Bearer {self.solscan_api_key}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "active_nodes": len(data) if isinstance(data, list) else 0,
                            "network_status": "active"
                        }
            
            return {"error": "Failed to fetch Solana metrics"}
            
        except Exception as e:
            logger.error(f"Error getting Solana metrics: {e}")
            return {"error": str(e)}
    
    async def _get_ethereum_address_info(self, address: str) -> Dict[str, Any]:
        """Get Ethereum address information"""
        try:
            url = f"{self.networks['ethereum'].base_url}?module=account&action=balance&address={address}&tag=latest&apikey={self.etherscan_api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        balance_wei = int(data.get("result", "0"))
                        balance_eth = balance_wei / (10 ** 18)
                        
                        return {
                            "address": address,
                            "balance_wei": balance_wei,
                            "balance_eth": balance_eth,
                            "network": "ethereum"
                        }
            
            return {"error": "Failed to fetch address info"}
            
        except Exception as e:
            logger.error(f"Error getting Ethereum address info: {e}")
            return {"error": str(e)}
    
    async def _get_tron_address_info(self, address: str) -> Dict[str, Any]:
        """Get TRON address information"""
        try:
            url = f"{self.networks['tron'].base_url}/account/{address}"
            headers = {"TRON-PRO-API-KEY": self.tronscan_api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        balance = data.get("balance", 0) / (10 ** 6)  # TRX has 6 decimals
                        
                        return {
                            "address": address,
                            "balance_trx": balance,
                            "network": "tron"
                        }
            
            return {"error": "Failed to fetch address info"}
            
        except Exception as e:
            logger.error(f"Error getting TRON address info: {e}")
            return {"error": str(e)}
    
    async def _get_solana_address_info(self, address: str) -> Dict[str, Any]:
        """Get Solana address information"""
        try:
            url = f"{self.networks['solana'].base_url}/account/{address}"
            headers = {"Authorization": f"Bearer {self.solscan_api_key}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        balance = data.get("lamports", 0) / (10 ** 9)  # SOL has 9 decimals
                        
                        return {
                            "address": address,
                            "balance_sol": balance,
                            "network": "solana"
                        }
            
            return {"error": "Failed to fetch address info"}
            
        except Exception as e:
            logger.error(f"Error getting Solana address info: {e}")
            return {"error": str(e)}
    
    async def _get_ethereum_transactions(self, address: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get Ethereum transactions for an address"""
        try:
            url = f"{self.networks['ethereum'].base_url}?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&page=1&offset={limit}&sort=desc&apikey={self.etherscan_api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        transactions = data.get("result", [])
                        
                        return [
                            {
                                "tx_hash": tx.get("hash"),
                                "from": tx.get("from"),
                                "to": tx.get("to"),
                                "value": float(tx.get("value", 0)) / (10 ** 18),
                                "gas_price": float(tx.get("gasPrice", 0)),
                                "gas_used": int(tx.get("gasUsed", 0)),
                                "block_number": int(tx.get("blockNumber", 0)),
                                "timestamp": datetime.fromtimestamp(int(tx.get("timeStamp", 0))).isoformat(),
                                "status": "success" if tx.get("isError") == "0" else "failed"
                            }
                            for tx in transactions
                        ]
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting Ethereum transactions: {e}")
            return []
    
    async def _get_tron_transactions(self, address: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get TRON transactions for an address"""
        try:
            url = f"{self.networks['tron'].base_url}/transaction/trc20?address={address}&limit={limit}&start=0&sort=-timestamp"
            headers = {"TRON-PRO-API-KEY": self.tronscan_api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        transactions = data.get("data", [])
                        
                        return [
                            {
                                "tx_hash": tx.get("transaction_id"),
                                "from": tx.get("from"),
                                "to": tx.get("to"),
                                "value": float(tx.get("value", 0)) / (10 ** int(tx.get("tokenInfo", {}).get("tokenDecimal", 6))),
                                "token_symbol": tx.get("tokenInfo", {}).get("tokenAbbr"),
                                "block_number": int(tx.get("block", 0)),
                                "timestamp": datetime.fromtimestamp(int(tx.get("timestamp", 0)) / 1000).isoformat(),
                                "status": "success"
                            }
                            for tx in transactions
                        ]
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting TRON transactions: {e}")
            return []
    
    async def _get_solana_transactions(self, address: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get Solana transactions for an address"""
        try:
            url = f"{self.networks['solana'].base_url}/account/{address}/transactions?limit={limit}"
            headers = {"Authorization": f"Bearer {self.solscan_api_key}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        transactions = data.get("data", [])
                        
                        return [
                            {
                                "tx_hash": tx.get("txHash"),
                                "from": tx.get("from"),
                                "to": tx.get("to"),
                                "value": float(tx.get("lamport", 0)) / (10 ** 9),
                                "block_number": int(tx.get("slot", 0)),
                                "timestamp": datetime.fromtimestamp(int(tx.get("blockTime", 0))).isoformat(),
                                "status": "success" if tx.get("status") == "Success" else "failed"
                            }
                            for tx in transactions
                        ]
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting Solana transactions: {e}")
            return []
    
    async def _get_ethereum_tokens(self, address: str) -> List[Dict[str, Any]]:
        """Get Ethereum tokens for an address"""
        try:
            url = f"{self.networks['ethereum'].base_url}?module=account&action=tokentx&address={address}&startblock=0&endblock=99999999&sort=desc&apikey={self.etherscan_api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        tokens = data.get("result", [])
                        
                        # Group by token contract
                        token_balances = {}
                        for token in tokens:
                            contract = token.get("contractAddress")
                            if contract not in token_balances:
                                token_balances[contract] = {
                                    "contract_address": contract,
                                    "name": token.get("tokenName"),
                                    "symbol": token.get("tokenSymbol"),
                                    "decimals": int(token.get("tokenDecimal", 18)),
                                    "balance": 0
                                }
                            
                            # Calculate balance
                            value = float(token.get("value", 0))
                            decimals = token_balances[contract]["decimals"]
                            token_balances[contract]["balance"] += value / (10 ** decimals)
                        
                        return list(token_balances.values())
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting Ethereum tokens: {e}")
            return []
    
    async def _get_tron_tokens(self, address: str) -> List[Dict[str, Any]]:
        """Get TRON tokens for an address"""
        try:
            url = f"{self.networks['tron'].base_url}/account/{address}/trc20"
            headers = {"TRON-PRO-API-KEY": self.tronscan_api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        tokens = data.get("data", [])
                        
                        return [
                            {
                                "contract_address": token.get("contract_address"),
                                "name": token.get("name"),
                                "symbol": token.get("symbol"),
                                "decimals": int(token.get("decimals", 6)),
                                "balance": float(token.get("balance", 0)) / (10 ** int(token.get("decimals", 6)))
                            }
                            for token in tokens
                        ]
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting TRON tokens: {e}")
            return []
    
    async def _get_solana_tokens(self, address: str) -> List[Dict[str, Any]]:
        """Get Solana tokens for an address"""
        try:
            url = f"{self.networks['solana'].base_url}/account/{address}/tokens"
            headers = {"Authorization": f"Bearer {self.solscan_api_key}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        tokens = data.get("data", [])
                        
                        return [
                            {
                                "contract_address": token.get("mint"),
                                "name": token.get("name"),
                                "symbol": token.get("symbol"),
                                "decimals": int(token.get("decimals", 9)),
                                "balance": float(token.get("amount", 0)) / (10 ** int(token.get("decimals", 9)))
                            }
                            for token in tokens
                        ]
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting Solana tokens: {e}")
            return []
    
    async def get_multi_chain_data(self, addresses: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Get data from all supported blockchains"""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "networks": {}
            }
            
            # Get data for each network
            if addresses and "ethereum" in addresses:
                data["networks"]["ethereum"] = await self.get_ethereum_data(addresses["ethereum"])
            
            if addresses and "tron" in addresses:
                data["networks"]["tron"] = await self.get_tron_data(addresses["tron"])
            
            if addresses and "solana" in addresses:
                data["networks"]["solana"] = await self.get_solana_data(addresses["solana"])
            
            # Get network metrics
            data["networks"]["ethereum"] = await self.get_ethereum_data()
            data["networks"]["tron"] = await self.get_tron_data()
            data["networks"]["solana"] = await self.get_solana_data()
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting multi-chain data: {e}")
            return {"error": str(e)}
    
    def is_ready(self) -> bool:
        """Check if blockchain agent is ready"""
        return self.initialized 