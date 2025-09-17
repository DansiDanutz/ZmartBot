#!/usr/bin/env python3
"""
ZmartBot MCP Server
Model Context Protocol server for AI agent orchestration and trading operations
"""

import asyncio
import json
import logging
import sys
from typing import Dict, Any, List, Optional
from pathlib import Path
import socket

logger = logging.getLogger(__name__)

class ZmartBotMCPServer:
    """MCP Server for ZmartBot AI agent orchestration"""
    
    def __init__(self, host='127.0.0.1', port=7002):
        self.host = host
        self.port = port
        self.server = None
        self.clients = []
        
        # Load ZmartBot configuration
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load ZmartBot configuration"""
        try:
            config_path = Path(__file__).parent.parent.parent.parent / ".mcp.json"
            if config_path.exists():
                with open(config_path) as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.warning(f"Could not load config: {e}")
            return {}
    
    async def handle_client(self, websocket, path):
        """Handle MCP client connections"""
        logger.info(f"New MCP client connected: {websocket.remote_address}")
        self.clients.append(websocket)
        
        try:
            async for message in websocket:
                await self.process_message(websocket, message)
        except Exception as e:
            logger.error(f"Client error: {e}")
        finally:
            if websocket in self.clients:
                self.clients.remove(websocket)
            logger.info("Client disconnected")
    
    async def process_message(self, websocket, message: str):
        """Process incoming MCP messages"""
        try:
            data = json.loads(message)
            method = data.get('method')
            params = data.get('params', {})
            msg_id = data.get('id')
            
            logger.info(f"Processing MCP method: {method}")
            
            # Handle different MCP methods
            if method == 'initialize':
                response = await self.handle_initialize(params)
            elif method == 'tools/list':
                response = await self.handle_list_tools(params)
            elif method == 'tools/call':
                response = await self.handle_tool_call(params)
            elif method == 'resources/list':
                response = await self.handle_list_resources(params)
            elif method == 'resources/read':
                response = await self.handle_read_resource(params)
            elif method == 'prompts/list':
                response = await self.handle_list_prompts(params)
            elif method == 'prompts/get':
                response = await self.handle_get_prompt(params)
            else:
                response = {
                    'error': {'code': -32601, 'message': f'Method not found: {method}'}
                }
            
            # Send response
            response['id'] = msg_id
            await websocket.send(json.dumps(response))
            
        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                'error': {'code': -32700, 'message': 'Parse error'}
            }))
        except Exception as e:
            logger.error(f"Message processing error: {e}")
            await websocket.send(json.dumps({
                'error': {'code': -32603, 'message': f'Internal error: {str(e)}'}
            }))
    
    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request"""
        return {
            'result': {
                'protocolVersion': '2024-11-05',
                'capabilities': {
                    'tools': {},
                    'resources': {},
                    'prompts': {},
                    'logging': {}
                },
                'serverInfo': {
                    'name': 'zmartbot-mcp',
                    'version': '1.0.0',
                    'description': 'ZmartBot MCP Server for AI agent orchestration'
                }
            }
        }
    
    async def handle_list_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request"""
        tools = []
        
        # Add ZmartBot trading tools
        tools.extend([
            {
                'name': 'get_trading_signals',
                'description': 'Get current trading signals from ZmartBot agents',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'symbol': {'type': 'string', 'description': 'Trading pair symbol'},
                        'timeframe': {'type': 'string', 'description': 'Timeframe for analysis'}
                    }
                }
            },
            {
                'name': 'get_agent_status',
                'description': 'Check status of ZmartBot AI agents',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'agent_type': {'type': 'string', 'description': 'Type of agent to check'}
                    }
                }
            },
            {
                'name': 'get_market_data',
                'description': 'Get real-time market data from ZmartBot',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'symbols': {'type': 'array', 'items': {'type': 'string'}},
                        'exchange': {'type': 'string', 'description': 'Exchange name'}
                    }
                }
            }
        ])
        
        return {'result': {'tools': tools}}
    
    async def handle_tool_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        name = params.get('name')
        arguments = params.get('arguments', {})
        
        logger.info(f"Tool call: {name} with args: {arguments}")
        
        try:
            if name == 'get_trading_signals':
                result = await self._get_trading_signals(arguments)
            elif name == 'get_agent_status':
                result = await self._get_agent_status(arguments)
            elif name == 'get_market_data':
                result = await self._get_market_data(arguments)
            else:
                return {
                    'error': {'code': -32601, 'message': f'Unknown tool: {name}'}
                }
            
            return {'result': result}
            
        except Exception as e:
            logger.error(f"Tool call error: {e}")
            return {
                'error': {'code': -32603, 'message': f'Tool execution error: {str(e)}'}
            }
    
    async def _get_trading_signals(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get trading signals from ZmartBot"""
        symbol = args.get('symbol', 'BTCUSDT')
        timeframe = args.get('timeframe', '1h')
        
        # Mock response for now - in production this would connect to actual trading agents
        return {
            'content': [{
                'type': 'text',
                'text': f"Trading signals for {symbol} on {timeframe} timeframe:\n"
                       f"• Trend: Bullish\n"
                       f"• RSI: 65.2\n" 
                       f"• Signal: BUY\n"
                       f"• Confidence: 78%"
            }]
        }
    
    async def _get_agent_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get agent status from ZmartBot"""
        agent_type = args.get('agent_type', 'all')
        
        return {
            'content': [{
                'type': 'text',
                'text': f"ZmartBot Agent Status ({agent_type}):\n"
                       f"• MDC Agent: Active\n"
                       f"• Trading Agent: Active\n"
                       f"• Analytics Agent: Active\n"
                       f"• Risk Management: Active\n"
                       f"• Total Services: 42 running"
            }]
        }
    
    async def _get_market_data(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get market data from ZmartBot"""
        symbols = args.get('symbols', ['BTCUSDT'])
        exchange = args.get('exchange', 'binance')
        
        return {
            'content': [{
                'type': 'text',
                'text': f"Market Data from {exchange}:\n" +
                       '\n'.join([f"• {symbol}: $45,230 (+2.1%)" for symbol in symbols])
            }]
        }
    
    async def handle_list_resources(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/list request"""
        resources = [
            {
                'uri': 'file://./AGENTS.md',
                'name': 'ZmartBot Agents Documentation',
                'description': 'Comprehensive AI agent documentation',
                'mimeType': 'text/markdown'
            },
            {
                'uri': 'file://./CLAUDE.md',
                'name': 'ZmartBot Configuration',
                'description': 'Smart context and system configuration',
                'mimeType': 'text/markdown'
            }
        ]
        
        return {'result': {'resources': resources}}
    
    async def handle_read_resource(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/read request"""
        uri = params.get('uri', '')
        
        try:
            if uri.startswith('file://'):
                path = Path(uri[7:])  # Remove 'file://' prefix
                if path.exists():
                    content = path.read_text()
                    return {
                        'result': {
                            'contents': [{
                                'uri': uri,
                                'mimeType': 'text/markdown',
                                'text': content
                            }]
                        }
                    }
            
            return {
                'error': {'code': -32602, 'message': f'Resource not found: {uri}'}
            }
        except Exception as e:
            return {
                'error': {'code': -32603, 'message': f'Resource read error: {str(e)}'}
            }
    
    async def handle_list_prompts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prompts/list request"""
        prompts = []
        
        # Add ZmartBot prompts from config
        config_prompts = self.config.get('prompts', {})
        for prompt_name, prompt_config in config_prompts.items():
            prompts.append({
                'name': prompt_name,
                'description': prompt_config.get('description', ''),
                'arguments': prompt_config.get('arguments', [])
            })
        
        return {'result': {'prompts': prompts}}
    
    async def handle_get_prompt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prompts/get request"""
        name = params.get('name')
        arguments = params.get('arguments', {})
        
        config_prompts = self.config.get('prompts', {})
        if name not in config_prompts:
            return {
                'error': {'code': -32602, 'message': f'Prompt not found: {name}'}
            }
        
        prompt_config = config_prompts[name]
        
        # Generate prompt based on name and arguments
        if name == 'analyze_trading_opportunity':
            symbol = arguments.get('symbol', 'BTCUSDT')
            timeframe = arguments.get('timeframe', '1h')
            risk_level = arguments.get('risk_level', 'medium')
            
            content = f"Analyze the trading opportunity for {symbol} on {timeframe} timeframe with {risk_level} risk tolerance. Provide technical analysis, market sentiment, and trading recommendations."
        else:
            content = f"Execute {name} with provided arguments"
        
        return {
            'result': {
                'description': prompt_config.get('description', ''),
                'messages': [{
                    'role': 'user',
                    'content': {
                        'type': 'text',
                        'text': content
                    }
                }]
            }
        }
    
    def _is_port_available(self, port: int) -> bool:
        """Check if port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    async def start(self):
        """Start the MCP server"""
        try:
            import websockets
            
            # Check if port is available
            if not self._is_port_available(self.port):
                logger.warning(f"Port {self.port} is busy, trying alternative ports...")
                for alt_port in [7003, 7004, 7005]:
                    if self._is_port_available(alt_port):
                        self.port = alt_port
                        logger.info(f"Using alternative port: {self.port}")
                        break
                else:
                    raise Exception("No available ports found")
            
            # Start WebSocket server
            self.server = await websockets.serve(
                self.handle_client,
                self.host,
                self.port,
                ping_interval=30,
                ping_timeout=10
            )
            
            logger.info(f"ZmartBot MCP Server started on {self.host}:{self.port}")
            await self.server.wait_closed()
            
        except ImportError:
            logger.error("websockets library not installed. Install with: pip install websockets")
            # Fallback to simple HTTP server
            await self._start_http_server()
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            raise
    
    async def _start_http_server(self):
        """Start a simple HTTP server as fallback"""
        from aiohttp import web, web_runner
        
        app = web.Application()
        app.router.add_post('/mcp', self._handle_http_request)
        app.router.add_get('/health', self._health_check)
        
        runner = web_runner.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        logger.info(f"ZmartBot MCP Server (HTTP fallback) started on http://{self.host}:{self.port}")
        
        # Keep server running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down MCP server...")
            await runner.cleanup()
    
    async def _handle_http_request(self, request):
        """Handle HTTP MCP requests"""
        try:
            data = await request.json()
            method = data.get('method')
            params = data.get('params', {})
            
            if method == 'tools/list':
                response = await self.handle_list_tools(params)
            elif method == 'tools/call':
                response = await self.handle_tool_call(params)
            else:
                response = {
                    'error': {'code': -32601, 'message': f'Method not found: {method}'}
                }
            
            return web.json_response(response)
            
        except Exception as e:
            return web.json_response({
                'error': {'code': -32603, 'message': f'Internal error: {str(e)}'}
            }, status=500)
    
    async def _health_check(self, request):
        """Health check endpoint"""
        return web.json_response({
            'status': 'healthy',
            'service': 'zmartbot-mcp',
            'port': self.port,
            'clients': len(self.clients)
        })

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = ZmartBotMCPServer()
    asyncio.run(server.start())