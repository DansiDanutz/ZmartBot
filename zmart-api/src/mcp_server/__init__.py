#!/usr/bin/env python3
"""
ZmartBot MCP Server Module
Model Context Protocol server for ZmartBot AI agent orchestration and trading operations
"""

import sys
import asyncio
import logging
from .mcp_server import ZmartBotMCPServer

def main():
    """Main entry point for MCP server"""
    logging.basicConfig(level=logging.INFO)
    server = ZmartBotMCPServer()
    asyncio.run(server.start())

if __name__ == "__main__":
    main()