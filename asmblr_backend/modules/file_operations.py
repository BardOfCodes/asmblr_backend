"""
File operations module.
Example module demonstrating how to organize file-related API endpoints.
"""

import os
import shutil
from typing import Dict, Any, List
from pathlib import Path


class FileOperationsModule:
    """
    Module for file operations and management.
    This is an example of how to structure modules for different API functionalities.
    """
    
    def __init__(self, base_path: str = "/tmp"):
        """
        Initialize the file operations module.
        
        Args:
            base_path: Base path for file operations (for security)
        """
        self.base_path = Path(base_path)
        self.allowed_extensions = {'.txt', '.json', '.csv', '.log', '.md'}
    
    def list_files(self, directory: str = "") -> Dict[str, Any]:
        """
        List files in a directory.
        
        Args:
            directory: Subdirectory to list (relative to base_path)
            
        Returns:
            Dictionary with file listing information
        """
        try:
            target_path = self.base_path / directory if directory else self.base_path
            
            if not target_path.exists():
                return {'error': 'Directory does not exist', 'files': []}
            
            if not target_path.is_dir():
                return {'error': 'Path is not a directory', 'files': []}
            
            files = []
            for item in target_path.iterdir():
                try:
                    stat = item.stat()
                    files.append({
                        'name': item.name,
                        'type': 'directory' if item.is_dir() else 'file',
                        'size': stat.st_size if item.is_file() else None,
                        'modified': stat.st_mtime,
                        'permissions': oct(stat.st_mode)[-3:]
                    })
                except (OSError, PermissionError):
                    continue
            
            return {
                'directory': str(target_path),
                'files': sorted(files, key=lambda x: (x['type'], x['name'])),
                'count': len(files)
            }
            
        except Exception as e:
            return {'error': f'Failed to list files: {str(e)}', 'files': []}
    
    def read_file(self, file_path: str, max_size: int = 1024 * 1024) -> Dict[str, Any]:
        """
        Read content from a file.
        
        Args:
            file_path: Path to the file (relative to base_path)
            max_size: Maximum file size to read (in bytes)
            
        Returns:
            Dictionary with file content or error information
        """
        try:
            target_path = self.base_path / file_path
            
            if not target_path.exists():
                return {'error': 'File does not exist', 'content': None}
            
            if not target_path.is_file():
                return {'error': 'Path is not a file', 'content': None}
            
            if target_path.stat().st_size > max_size:
                return {'error': f'File too large (max {max_size} bytes)', 'content': None}
            
            # Check file extension for security
            if target_path.suffix.lower() not in self.allowed_extensions:
                return {'error': 'File type not allowed', 'content': None}
            
            with open(target_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'file_path': str(target_path),
                'content': content,
                'size': len(content),
                'encoding': 'utf-8'
            }
            
        except UnicodeDecodeError:
            return {'error': 'File is not valid UTF-8 text', 'content': None}
        except Exception as e:
            return {'error': f'Failed to read file: {str(e)}', 'content': None}
    
    def write_file(self, file_path: str, content: str, overwrite: bool = False) -> Dict[str, Any]:
        """
        Write content to a file.
        
        Args:
            file_path: Path to the file (relative to base_path)
            content: Content to write
            overwrite: Whether to overwrite existing files
            
        Returns:
            Dictionary with operation result
        """
        try:
            target_path = self.base_path / file_path
            
            # Check file extension for security
            if target_path.suffix.lower() not in self.allowed_extensions:
                return {'error': 'File type not allowed', 'success': False}
            
            if target_path.exists() and not overwrite:
                return {'error': 'File exists and overwrite is False', 'success': False}
            
            # Create parent directories if needed
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                'file_path': str(target_path),
                'size': len(content),
                'success': True
            }
            
        except Exception as e:
            return {'error': f'Failed to write file: {str(e)}', 'success': False}
    
    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """
        Delete a file.
        
        Args:
            file_path: Path to the file (relative to base_path)
            
        Returns:
            Dictionary with operation result
        """
        try:
            target_path = self.base_path / file_path
            
            if not target_path.exists():
                return {'error': 'File does not exist', 'success': False}
            
            if target_path.is_dir():
                return {'error': 'Path is a directory, not a file', 'success': False}
            
            target_path.unlink()
            
            return {
                'file_path': str(target_path),
                'success': True
            }
            
        except Exception as e:
            return {'error': f'Failed to delete file: {str(e)}', 'success': False}
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get information about a file.
        
        Args:
            file_path: Path to the file (relative to base_path)
            
        Returns:
            Dictionary with file information
        """
        try:
            target_path = self.base_path / file_path
            
            if not target_path.exists():
                return {'error': 'File does not exist', 'info': None}
            
            stat = target_path.stat()
            
            return {
                'file_path': str(target_path),
                'info': {
                    'name': target_path.name,
                    'type': 'directory' if target_path.is_dir() else 'file',
                    'size': stat.st_size,
                    'created': stat.st_ctime,
                    'modified': stat.st_mtime,
                    'accessed': stat.st_atime,
                    'permissions': oct(stat.st_mode)[-3:],
                    'extension': target_path.suffix.lower()
                }
            }
            
        except Exception as e:
            return {'error': f'Failed to get file info: {str(e)}', 'info': None}
