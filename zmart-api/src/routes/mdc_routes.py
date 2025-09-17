"""
MDC (Markdown Documentation Components) Routes
Handles scanning and serving MDC files from .cursor/rules directory
"""

import os
import json
import glob
import logging
from pathlib import Path
from flask import Blueprint, jsonify, request
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mdc_bp = Blueprint('mdc', __name__, url_prefix='/api')

# ZmartBot working directory from rules.mdc
WORKING_DIRECTORY = "/Users/dansidanutz/Desktop/ZmartBot"
MDC_DIRECTORY = os.path.join(WORKING_DIRECTORY, ".cursor", "rules")

def scan_mdc_directory() -> List[str]:
    """
    Scan the .cursor/rules directory for MDC files
    Returns list of MDC filenames
    """
    try:
        if not os.path.exists(MDC_DIRECTORY):
            logger.warning(f"MDC directory not found: {MDC_DIRECTORY}")
            return []
        
        # Get all .mdc files
        mdc_pattern = os.path.join(MDC_DIRECTORY, "*.mdc")
        mdc_files = glob.glob(mdc_pattern)
        
        # Extract just the filenames
        filenames = [os.path.basename(f) for f in mdc_files]
        
        logger.info(f"Found {len(filenames)} MDC files in {MDC_DIRECTORY}")
        return sorted(filenames)
        
    except Exception as e:
        logger.error(f"Error scanning MDC directory: {e}")
        return []

def read_mdc_file(filename: str) -> str:
    """
    Read content of a specific MDC file
    """
    try:
        file_path = os.path.join(MDC_DIRECTORY, filename)
        
        if not os.path.exists(file_path):
            logger.warning(f"MDC file not found: {file_path}")
            return ""
        
        # Security check - ensure file is within MDC directory
        if not os.path.commonpath([file_path, MDC_DIRECTORY]) == MDC_DIRECTORY:
            logger.error(f"Security violation: File outside MDC directory: {filename}")
            return ""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"Read MDC file: {filename} ({len(content)} chars)")
        return content
        
    except Exception as e:
        logger.error(f"Error reading MDC file {filename}: {e}")
        return ""

def get_mdc_file_info(filename: str) -> Dict[str, Any]:
    """
    Get metadata about an MDC file
    """
    try:
        file_path = os.path.join(MDC_DIRECTORY, filename)
        
        if not os.path.exists(file_path):
            return {}
        
        stat = os.stat(file_path)
        
        return {
            "filename": filename,
            "path": file_path,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "created": stat.st_ctime
        }
        
    except Exception as e:
        logger.error(f"Error getting file info for {filename}: {e}")
        return {}

@mdc_bp.route('/scan-mdc-files', methods=['GET'])
def api_scan_mdc_files():
    """
    API endpoint to scan MDC files
    Returns: {"files": [...], "count": N, "directory": "path"}
    """
    try:
        files = scan_mdc_directory()
        
        response = {
            "success": True,
            "files": files,
            "count": len(files),
            "directory": MDC_DIRECTORY,
            "working_directory": WORKING_DIRECTORY
        }
        
        logger.info(f"API scan complete: {len(files)} files found")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"API scan error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "files": [],
            "count": 0
        }), 500

@mdc_bp.route('/mdc-file-content/<filename>', methods=['GET'])
def api_get_mdc_file_content(filename: str):
    """
    API endpoint to get content of specific MDC file
    Returns: {"content": "...", "info": {...}}
    """
    try:
        # Validate filename
        if not filename.endswith('.mdc'):
            return jsonify({
                "success": False,
                "error": "Invalid file extension. Only .mdc files allowed"
            }), 400
        
        # Security check for path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify({
                "success": False,
                "error": "Invalid filename"
            }), 400
        
        content = read_mdc_file(filename)
        file_info = get_mdc_file_info(filename)
        
        if not content and not file_info:
            return jsonify({
                "success": False,
                "error": "File not found"
            }), 404
        
        response = {
            "success": True,
            "content": content,
            "info": file_info,
            "filename": filename
        }
        
        logger.info(f"API content request: {filename} ({len(content)} chars)")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"API content error for {filename}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@mdc_bp.route('/mdc-directory-info', methods=['GET'])
def api_get_mdc_directory_info():
    """
    API endpoint to get MDC directory information
    Returns directory status and statistics
    """
    try:
        files = scan_mdc_directory()
        
        # Get directory stats
        total_size = 0
        file_stats = []
        
        for filename in files:
            info = get_mdc_file_info(filename)
            if info:
                total_size += info.get('size', 0)
                file_stats.append(info)
        
        response = {
            "success": True,
            "directory": MDC_DIRECTORY,
            "working_directory": WORKING_DIRECTORY,
            "exists": os.path.exists(MDC_DIRECTORY),
            "total_files": len(files),
            "total_size": total_size,
            "files": file_stats
        }
        
        logger.info(f"API directory info: {len(files)} files, {total_size} bytes")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"API directory info error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@mdc_bp.route('/mdc-search', methods=['GET'])
def api_search_mdc_files():
    """
    API endpoint to search MDC files by content or name
    Query params: q (search term), type (name|content|both)
    """
    try:
        query = request.args.get('q', '').strip()
        search_type = request.args.get('type', 'both').lower()
        
        if not query:
            return jsonify({
                "success": False,
                "error": "Search query required"
            }), 400
        
        files = scan_mdc_directory()
        results = []
        
        for filename in files:
            match_score = 0
            match_type = []
            
            # Search filename
            if search_type in ['name', 'both']:
                if query.lower() in filename.lower():
                    match_score += 10
                    match_type.append('filename')
            
            # Search content
            if search_type in ['content', 'both']:
                content = read_mdc_file(filename)
                if query.lower() in content.lower():
                    match_score += 5
                    match_type.append('content')
                    
                    # Count occurrences for ranking
                    occurrences = content.lower().count(query.lower())
                    match_score += occurrences
            
            if match_score > 0:
                results.append({
                    "filename": filename,
                    "match_score": match_score,
                    "match_type": match_type,
                    "info": get_mdc_file_info(filename)
                })
        
        # Sort by match score
        results.sort(key=lambda x: x['match_score'], reverse=True)
        
        response = {
            "success": True,
            "query": query,
            "search_type": search_type,
            "results": results,
            "count": len(results)
        }
        
        logger.info(f"API search: '{query}' found {len(results)} matches")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"API search error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# MDC Connection Agent endpoints
@mdc_bp.route('/mdc-auto-connect/<filename>', methods=['POST'])
def api_auto_connect_service(filename: str):
    """
    API endpoint to auto-connect a specific MDC file
    Discovers all possible connections and injects them into the file
    """
    try:
        # Security validation
        if not filename.endswith('.mdc'):
            return jsonify({
                "success": False,
                "error": "Invalid file extension. Only .mdc files allowed"
            }), 400
        
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify({
                "success": False,
                "error": "Invalid filename"
            }), 400
        
        # Import and get agent
        from ..services.mdc_connection_agent import get_mdc_agent
        agent = get_mdc_agent()
        
        # Run async auto-connect
        import asyncio
        result = asyncio.run(agent.auto_connect_service(filename))
        
        if result["success"]:
            logger.info(f"Auto-connected {filename}: {result['connections_found']} connections")
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Auto-connect error for {filename}: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "filename": filename
        }), 500

@mdc_bp.route('/mdc-discover-all', methods=['POST'])
def api_discover_all_connections():
    """
    API endpoint to discover connections for all MDC files
    """
    try:
        from ..services.mdc_connection_agent import get_mdc_agent
        agent = get_mdc_agent()
        
        import asyncio
        connections = asyncio.run(agent.discover_all_connections())
        
        # Count total connections
        total_connections = sum(len(conns) for conns in connections.values())
        
        return jsonify({
            "success": True,
            "message": f"Discovered connections for {len(connections)} services",
            "total_connections": total_connections,
            "services": list(connections.keys()),
            "stats": agent.get_connection_stats()
        })
        
    except Exception as e:
        logger.error(f"Discover all connections error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@mdc_bp.route('/mdc-connection-stats', methods=['GET'])
def api_get_connection_stats():
    """
    API endpoint to get connection statistics
    """
    try:
        from ..services.mdc_connection_agent import get_mdc_agent
        agent = get_mdc_agent()
        
        stats = agent.get_connection_stats()
        
        return jsonify({
            "success": True,
            "stats": stats,
            "agent_status": "running" if agent.is_running else "stopped"
        })
        
    except Exception as e:
        logger.error(f"Connection stats error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@mdc_bp.route('/mdc-service-connections/<service_name>', methods=['GET'])
def api_get_service_connections(service_name: str):
    """
    API endpoint to get connections for a specific service
    """
    try:
        from ..services.mdc_connection_agent import get_mdc_agent
        agent = get_mdc_agent()
        
        connections = agent.connections.get(service_name, [])
        
        # Convert connections to dict format
        connections_data = []
        for conn in connections:
            from dataclasses import asdict
            connections_data.append(asdict(conn))
        
        return jsonify({
            "success": True,
            "service_name": service_name,
            "connections": connections_data,
            "connection_count": len(connections)
        })
        
    except Exception as e:
        logger.error(f"Service connections error for {service_name}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Health check endpoint
@mdc_bp.route('/mdc-health', methods=['GET'])
def api_mdc_health():
    """
    Health check for MDC service
    """
    try:
        directory_exists = os.path.exists(MDC_DIRECTORY)
        files_count = len(scan_mdc_directory()) if directory_exists else 0
        
        # Check agent status
        agent_status = "not_initialized"
        try:
            from ..services.mdc_connection_agent import get_mdc_agent
            agent = get_mdc_agent()
            agent_status = "running" if agent.is_running else "stopped"
        except Exception:
            agent_status = "error"
        
        return jsonify({
            "success": True,
            "service": "MDC Browser & Connection Agent",
            "status": "healthy" if directory_exists else "warning",
            "directory": MDC_DIRECTORY,
            "directory_exists": directory_exists,
            "files_count": files_count,
            "agent_status": agent_status,
            "timestamp": __import__('time').time()
        })
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            "success": False,
            "status": "error",
            "error": str(e)
        }), 500