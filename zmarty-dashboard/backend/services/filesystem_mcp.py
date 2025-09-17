"""
Filesystem MCP Adapter for Zmarty Dashboard
Provides secure file system access through MCP
"""
import os
import json
import logging
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import hashlib
import tempfile
import shutil

logger = logging.getLogger(__name__)


class FilesystemMCPAdapter:
    """
    MCP-compatible filesystem adapter for secure file operations
    Provides controlled access to project files and data directories
    """
    
    def __init__(self, base_path: str = "/tmp/zmarty_files", allowed_extensions: Optional[List[str]] = None):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Security: Define allowed file extensions
        self.allowed_extensions = allowed_extensions or [
            '.txt', '.json', '.csv', '.md', '.yml', '.yaml', '.log',
            '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css',
            '.png', '.jpg', '.jpeg', '.gif', '.svg', '.pdf'
        ]
        
        # Security: Define restricted paths
        self.restricted_paths = {
            '/', '/etc', '/usr', '/bin', '/sbin', '/root', '/home',
            '/var', '/tmp', '/proc', '/sys', '/dev'
        }
        
        # Create secure directories
        self._init_directories()
        
    def _init_directories(self):
        """Initialize secure directory structure"""
        directories = [
            'uploads', 'exports', 'logs', 'cache', 'temp',
            'user_data', 'analytics', 'backups'
        ]
        
        for directory in directories:
            dir_path = self.base_path / directory
            dir_path.mkdir(exist_ok=True)
            
            # Create .gitkeep file
            gitkeep = dir_path / '.gitkeep'
            if not gitkeep.exists():
                gitkeep.write_text('')
        
        logger.info(f"Filesystem MCP initialized at {self.base_path}")
    
    def _is_safe_path(self, file_path: Union[str, Path]) -> bool:
        """Check if path is safe for operations"""
        try:
            resolved_path = Path(file_path).resolve()
            base_resolved = self.base_path.resolve()
            
            # Must be within base path
            if not str(resolved_path).startswith(str(base_resolved)):
                return False
            
            # Check for restricted patterns
            path_str = str(resolved_path)
            restricted_patterns = ['..', '~', '$', '|', ';', '&', '`']
            
            for pattern in restricted_patterns:
                if pattern in path_str:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _is_allowed_extension(self, file_path: Union[str, Path]) -> bool:
        """Check if file extension is allowed"""
        extension = Path(file_path).suffix.lower()
        return extension in self.allowed_extensions
    
    def _get_file_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Get comprehensive file metadata"""
        try:
            stat = file_path.stat()
            
            # Calculate file hash for integrity
            file_hash = ""
            if file_path.is_file() and stat.st_size < 10 * 1024 * 1024:  # Only hash files < 10MB
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            return {
                "name": file_path.name,
                "path": str(file_path.relative_to(self.base_path)),
                "absolute_path": str(file_path),
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "is_file": file_path.is_file(),
                "is_directory": file_path.is_dir(),
                "extension": file_path.suffix.lower(),
                "mime_type": mime_type,
                "hash": file_hash,
                "permissions": oct(stat.st_mode)[-3:],
                "readable": os.access(file_path, os.R_OK),
                "writable": os.access(file_path, os.W_OK)
            }
            
        except Exception as e:
            logger.error(f"Failed to get metadata for {file_path}: {e}")
            return {"error": str(e)}
    
    def list_directory(self, directory: str = "", include_hidden: bool = False) -> Dict[str, Any]:
        """List directory contents with metadata"""
        try:
            target_path = self.base_path / directory if directory else self.base_path
            
            if not self._is_safe_path(target_path):
                raise ValueError("Unsafe path access denied")
            
            if not target_path.exists():
                raise FileNotFoundError(f"Directory not found: {directory}")
            
            if not target_path.is_dir():
                raise ValueError(f"Path is not a directory: {directory}")
            
            files = []
            directories = []
            
            for item in target_path.iterdir():
                # Skip hidden files unless requested
                if not include_hidden and item.name.startswith('.'):
                    continue
                
                metadata = self._get_file_metadata(item)
                
                if item.is_dir():
                    directories.append(metadata)
                else:
                    files.append(metadata)
            
            # Sort by name
            files.sort(key=lambda x: x['name'])
            directories.sort(key=lambda x: x['name'])
            
            return {
                "directory": str(target_path.relative_to(self.base_path)),
                "files": files,
                "directories": directories,
                "total_files": len(files),
                "total_directories": len(directories),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to list directory {directory}: {e}")
            return {"error": str(e)}
    
    def read_file(self, file_path: str, encoding: str = 'utf-8', max_size: int = 1024*1024) -> Dict[str, Any]:
        """Read file content with safety checks"""
        try:
            target_path = self.base_path / file_path
            
            if not self._is_safe_path(target_path):
                raise ValueError("Unsafe path access denied")
            
            if not target_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if not target_path.is_file():
                raise ValueError(f"Path is not a file: {file_path}")
            
            if not self._is_allowed_extension(target_path):
                raise ValueError(f"File extension not allowed: {target_path.suffix}")
            
            # Check file size
            file_size = target_path.stat().st_size
            if file_size > max_size:
                raise ValueError(f"File too large: {file_size} bytes (max: {max_size})")
            
            # Read file content
            try:
                content = target_path.read_text(encoding=encoding)
                is_binary = False
            except UnicodeDecodeError:
                # Try reading as binary
                content = target_path.read_bytes()
                content = content.hex()  # Convert to hex string
                is_binary = True
            
            metadata = self._get_file_metadata(target_path)
            
            return {
                "path": file_path,
                "content": content,
                "size": file_size,
                "encoding": encoding,
                "is_binary": is_binary,
                "metadata": metadata,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return {"error": str(e)}
    
    def write_file(
        self, 
        file_path: str, 
        content: Union[str, bytes], 
        encoding: str = 'utf-8',
        create_dirs: bool = True
    ) -> Dict[str, Any]:
        """Write file content with safety checks"""
        try:
            target_path = self.base_path / file_path
            
            if not self._is_safe_path(target_path):
                raise ValueError("Unsafe path access denied")
            
            if not self._is_allowed_extension(target_path):
                raise ValueError(f"File extension not allowed: {target_path.suffix}")
            
            # Create parent directories if needed
            if create_dirs:
                target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            if isinstance(content, bytes):
                target_path.write_bytes(content)
            else:
                target_path.write_text(content, encoding=encoding)
            
            metadata = self._get_file_metadata(target_path)
            
            logger.info(f"File written successfully: {file_path}")
            
            return {
                "path": file_path,
                "size": metadata["size"],
                "created": metadata["created"],
                "metadata": metadata,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            return {"error": str(e)}
    
    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """Delete file with safety checks"""
        try:
            target_path = self.base_path / file_path
            
            if not self._is_safe_path(target_path):
                raise ValueError("Unsafe path access denied")
            
            if not target_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Get metadata before deletion
            metadata = self._get_file_metadata(target_path)
            
            # Delete file or directory
            if target_path.is_file():
                target_path.unlink()
            elif target_path.is_dir():
                shutil.rmtree(target_path)
            
            logger.info(f"Deleted successfully: {file_path}")
            
            return {
                "path": file_path,
                "deleted": True,
                "metadata": metadata,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return {"error": str(e)}
    
    def copy_file(self, source_path: str, destination_path: str) -> Dict[str, Any]:
        """Copy file with safety checks"""
        try:
            src_path = self.base_path / source_path
            dst_path = self.base_path / destination_path
            
            if not self._is_safe_path(src_path) or not self._is_safe_path(dst_path):
                raise ValueError("Unsafe path access denied")
            
            if not src_path.exists():
                raise FileNotFoundError(f"Source file not found: {source_path}")
            
            if not self._is_allowed_extension(dst_path):
                raise ValueError(f"Destination file extension not allowed: {dst_path.suffix}")
            
            # Create destination directory if needed
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            if src_path.is_file():
                shutil.copy2(src_path, dst_path)
            elif src_path.is_dir():
                shutil.copytree(src_path, dst_path)
            
            dst_metadata = self._get_file_metadata(dst_path)
            
            logger.info(f"Copied {source_path} to {destination_path}")
            
            return {
                "source_path": source_path,
                "destination_path": destination_path,
                "copied": True,
                "metadata": dst_metadata,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to copy {source_path} to {destination_path}: {e}")
            return {"error": str(e)}
    
    def move_file(self, source_path: str, destination_path: str) -> Dict[str, Any]:
        """Move file with safety checks"""
        try:
            src_path = self.base_path / source_path
            dst_path = self.base_path / destination_path
            
            if not self._is_safe_path(src_path) or not self._is_safe_path(dst_path):
                raise ValueError("Unsafe path access denied")
            
            if not src_path.exists():
                raise FileNotFoundError(f"Source file not found: {source_path}")
            
            if not self._is_allowed_extension(dst_path):
                raise ValueError(f"Destination file extension not allowed: {dst_path.suffix}")
            
            # Create destination directory if needed
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move file
            shutil.move(str(src_path), str(dst_path))
            
            dst_metadata = self._get_file_metadata(dst_path)
            
            logger.info(f"Moved {source_path} to {destination_path}")
            
            return {
                "source_path": source_path,
                "destination_path": destination_path,
                "moved": True,
                "metadata": dst_metadata,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to move {source_path} to {destination_path}: {e}")
            return {"error": str(e)}
    
    def search_files(
        self, 
        pattern: str, 
        directory: str = "",
        case_sensitive: bool = False,
        file_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search for files matching pattern"""
        try:
            search_path = self.base_path / directory if directory else self.base_path
            
            if not self._is_safe_path(search_path):
                raise ValueError("Unsafe path access denied")
            
            matches = []
            
            # Convert pattern for case-insensitive search
            if not case_sensitive:
                pattern = pattern.lower()
            
            for item in search_path.rglob("*"):
                if not self._is_safe_path(item):
                    continue
                
                # Skip directories if looking for specific file type
                if file_type == "file" and not item.is_file():
                    continue
                if file_type == "directory" and not item.is_dir():
                    continue
                
                # Check pattern match
                item_name = item.name if case_sensitive else item.name.lower()
                
                if pattern in item_name:
                    metadata = self._get_file_metadata(item)
                    matches.append(metadata)
            
            # Sort by relevance (exact matches first, then by name)
            matches.sort(key=lambda x: (not x['name'].startswith(pattern), x['name']))
            
            return {
                "pattern": pattern,
                "directory": directory,
                "matches": matches,
                "count": len(matches),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to search files with pattern {pattern}: {e}")
            return {"error": str(e)}
    
    def get_disk_usage(self, directory: str = "") -> Dict[str, Any]:
        """Get disk usage statistics"""
        try:
            target_path = self.base_path / directory if directory else self.base_path
            
            if not self._is_safe_path(target_path):
                raise ValueError("Unsafe path access denied")
            
            total_size = 0
            file_count = 0
            dir_count = 0
            
            for item in target_path.rglob("*"):
                if item.is_file():
                    try:
                        total_size += item.stat().st_size
                        file_count += 1
                    except (OSError, IOError):
                        pass  # Skip files that can't be accessed
                elif item.is_dir():
                    dir_count += 1
            
            return {
                "directory": directory,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "file_count": file_count,
                "directory_count": dir_count,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get disk usage for {directory}: {e}")
            return {"error": str(e)}


# Global instance
filesystem_mcp = FilesystemMCPAdapter()


# MCP-compatible interface functions
async def mcp_list_directory(directory: str = "", include_hidden: bool = False) -> Dict[str, Any]:
    """MCP-compatible directory listing"""
    return filesystem_mcp.list_directory(directory, include_hidden)


async def mcp_read_file(file_path: str, encoding: str = 'utf-8', max_size: int = 1024*1024) -> Dict[str, Any]:
    """MCP-compatible file reading"""
    return filesystem_mcp.read_file(file_path, encoding, max_size)


async def mcp_write_file(
    file_path: str, 
    content: Union[str, bytes], 
    encoding: str = 'utf-8',
    create_dirs: bool = True
) -> Dict[str, Any]:
    """MCP-compatible file writing"""
    return filesystem_mcp.write_file(file_path, content, encoding, create_dirs)


async def mcp_search_files(
    pattern: str, 
    directory: str = "",
    case_sensitive: bool = False,
    file_type: Optional[str] = None
) -> Dict[str, Any]:
    """MCP-compatible file search"""
    return filesystem_mcp.search_files(pattern, directory, case_sensitive, file_type)


async def mcp_get_disk_usage(directory: str = "") -> Dict[str, Any]:
    """MCP-compatible disk usage"""
    return filesystem_mcp.get_disk_usage(directory)