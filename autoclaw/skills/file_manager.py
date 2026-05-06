"""
AutoClaw - Autonomous AI Agent Platform
File Manager Skill

Handles file operations: read, write, organize, monitor, and search.
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

SKILL_METADATA = {
    "name": "file_manager",
    "version": "1.0.0",
    "description": "File management: read, write, organize, and monitor files",
    "author": "AutoClaw Team",
    "capabilities": [
        "read_file",
        "write_file",
        "delete_file",
        "create_directory",
        "list_directory",
        "search_files",
        "copy_file",
        "move_file",
        "compress"
    ]
}


class FileManager:
    """
    File management operations.
    
    Features:
    - Read/write text and binary files
    - Create/delete directories
    - Search files by content or name
    - Monitor file changes
    - Archive/compress files
    """
    
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir) if base_dir else Path.home()
        self.file_watchers = {}
    
    async def read_file(self, path: str, encoding: str = "utf-8") -> Dict:
        """
        Read a file's contents.
        
        Args:
            path: File path (absolute or relative to base_dir)
            encoding: File encoding
            
        Returns:
            File contents
        """
        try:
            file_path = self._resolve_path(path)
            
            if not file_path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }
            
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return {
                "success": True,
                "path": str(file_path),
                "content": content,
                "size": file_path.stat().st_size,
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def write_file(self, path: str, content: str, encoding: str = "utf-8", 
                         append: bool = False) -> Dict:
        """
        Write content to a file.
        
        Args:
            path: File path
            content: Content to write
            encoding: File encoding
            append: Whether to append instead of overwrite
            
        Returns:
            Write result
        """
        try:
            file_path = self._resolve_path(path)
            
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            mode = 'a' if append else 'w'
            with open(file_path, mode, encoding=encoding) as f:
                f.write(content)
            
            return {
                "success": True,
                "path": str(file_path),
                "bytes_written": len(content.encode(encoding)),
                "message": f"Successfully wrote to {file_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_file(self, path: str) -> Dict:
        """Delete a file."""
        try:
            file_path = self._resolve_path(path)
            
            if not file_path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }
            
            file_path.unlink()
            
            return {
                "success": True,
                "path": str(file_path),
                "message": "File deleted successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_directory(self, path: str, parents: bool = True) -> Dict:
        """Create a directory."""
        try:
            dir_path = self._resolve_path(path)
            dir_path.mkdir(parents=parents, exist_ok=True)
            
            return {
                "success": True,
                "path": str(dir_path),
                "message": "Directory created successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def list_directory(self, path: str, pattern: str = "*") -> Dict:
        """List contents of a directory."""
        try:
            dir_path = self._resolve_path(path)
            
            if not dir_path.exists():
                return {
                    "success": False,
                    "error": f"Directory not found: {dir_path}"
                }
            
            items = []
            for item in dir_path.glob(pattern):
                stat = item.stat()
                items.append({
                    "name": item.name,
                    "path": str(item),
                    "is_directory": item.is_dir(),
                    "size": stat.st_size if item.is_file() else 0,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            
            return {
                "success": True,
                "path": str(dir_path),
                "items": items,
                "total": len(items)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def search_files(self, directory: str, pattern: str = "*", 
                          content_search: Optional[str] = None) -> Dict:
        """
        Search for files by name pattern and/or content.
        
        Args:
            directory: Directory to search in
            pattern: Glob pattern for filename matching
            content_search: Optional text to search for in file contents
            
        Returns:
            Matching files
        """
        try:
            dir_path = self._resolve_path(directory)
            matches = []
            
            for file_path in dir_path.rglob(pattern):
                if file_path.is_file():
                    match_info = {
                        "path": str(file_path),
                        "name": file_path.name,
                        "size": file_path.stat().st_size
                    }
                    
                    # Search in content if specified
                    if content_search:
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if content_search.lower() in content.lower():
                                    match_info["content_match"] = True
                                    matches.append(match_info)
                        except:
                            pass
                    else:
                        matches.append(match_info)
            
            return {
                "success": True,
                "directory": str(dir_path),
                "matches": matches,
                "count": len(matches)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def copy_file(self, source: str, destination: str) -> Dict:
        """Copy a file."""
        try:
            source_path = self._resolve_path(source)
            dest_path = self._resolve_path(destination)
            
            if not source_path.exists():
                return {
                    "success": False,
                    "error": f"Source file not found: {source_path}"
                }
            
            # Create parent directories
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(source_path, dest_path)
            
            return {
                "success": True,
                "source": str(source_path),
                "destination": str(dest_path),
                "message": "File copied successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def move_file(self, source: str, destination: str) -> Dict:
        """Move a file."""
        try:
            source_path = self._resolve_path(source)
            dest_path = self._resolve_path(destination)
            
            if not source_path.exists():
                return {
                    "success": False,
                    "error": f"Source file not found: {source_path}"
                }
            
            # Create parent directories
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(source_path), str(dest_path))
            
            return {
                "success": True,
                "source": str(source_path),
                "destination": str(dest_path),
                "message": "File moved successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def compress(self, files: List[str], output: str, format: str = "zip") -> Dict:
        """Compress files into an archive."""
        try:
            output_path = self._resolve_path(output)
            
            # Resolve all input files
            resolved_files = []
            for f in files:
                file_path = self._resolve_path(f)
                if file_path.exists():
                    resolved_files.append(str(file_path))
            
            if not resolved_files:
                return {
                    "success": False,
                    "error": "No valid files to compress"
                }
            
            # Create archive
            if format == "zip":
                archive_name = str(output_path.with_suffix(''))
                shutil.make_archive(archive_name, 'zip', 
                                   root_dir=str(output_path.parent),
                                   base_dir=str(output_path.stem))
            else:
                return {
                    "success": False,
                    "error": f"Unsupported format: {format}"
                }
            
            return {
                "success": True,
                "output": str(output_path) + ".zip",
                "files_compressed": len(resolved_files),
                "message": "Files compressed successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _resolve_path(self, path: str) -> Path:
        """Resolve a path relative to base_dir if not absolute."""
        p = Path(path)
        if p.is_absolute():
            return p
        return self.base_dir / p
    
    async def execute(self, action: str, **kwargs) -> Dict:
        """Generic execute method for tool manager compatibility."""
        if action == "read_file":
            return await self.read_file(kwargs.get("path", ""), kwargs.get("encoding", "utf-8"))
        elif action == "write_file":
            return await self.write_file(
                kwargs.get("path", ""),
                kwargs.get("content", ""),
                kwargs.get("encoding", "utf-8"),
                kwargs.get("append", False)
            )
        elif action == "delete_file":
            return await self.delete_file(kwargs.get("path", ""))
        elif action == "create_directory":
            return await self.create_directory(kwargs.get("path", ""))
        elif action == "list_directory":
            return await self.list_directory(kwargs.get("path", "."), kwargs.get("pattern", "*"))
        elif action == "search_files":
            return await self.search_files(
                kwargs.get("directory", "."),
                kwargs.get("pattern", "*"),
                kwargs.get("content_search")
            )
        elif action == "copy_file":
            return await self.copy_file(kwargs.get("source", ""), kwargs.get("destination", ""))
        elif action == "move_file":
            return await self.move_file(kwargs.get("source", ""), kwargs.get("destination", ""))
        elif action == "compress":
            return await self.compress(
                kwargs.get("files", []),
                kwargs.get("output", "archive.zip"),
                kwargs.get("format", "zip")
            )
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}"
            }
