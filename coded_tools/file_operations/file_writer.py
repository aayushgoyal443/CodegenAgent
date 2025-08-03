"""
File Writer tool for the CodeGen agent system.

This tool allows agents to write content to files on the local filesystem.
"""

import logging
import os
from typing import Any, Dict, Union

from neuro_san.interfaces.coded_tool import CodedTool


class FileWriter(CodedTool):
    """
    A tool that writes content to files on the local filesystem.
    
    This tool provides safe file writing capabilities with proper error handling
    and security measures to prevent directory traversal attacks.
    """
    
    def __init__(self):
        """Initialize the file writer tool with a logger."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        Write content to a file on the local filesystem.
        
        Args:
            args: Dictionary containing:
                - file_path: (str) Path where the file should be written
                - content: (str) Content to write to the file
                - mode: (str, optional) File mode ('w' for write, 'a' for append). Defaults to 'w'.
                - encoding: (str, optional) File encoding. Defaults to 'utf-8'.
                - create_dirs: (bool, optional) Create parent directories if they don't exist. Defaults to True.
            sly_data: Dictionary for maintaining state between tool invocations.
            
        Returns:
            Dict containing:
                - status: (str) 'success' or 'error'
                - file_path: (str) Path where the file was written
                - bytes_written: (int) Number of bytes written
                - message: (str) Additional information or error message
        """
        print("\n=== File Writer Invoked ===")
        try:
            # Get and validate required parameters
            file_path = args.get("file_path")
            if not file_path:
                return "Error: Missing required parameter 'file_path'"
                
            content = args.get("content")
            if content is None:
                return "Error: Missing required parameter 'content'"
            
            # Get optional parameters with defaults
            mode = args.get("mode", "w")
            encoding = args.get("encoding", "utf-8")
            create_dirs = args.get("create_dirs", True)
            
            # Convert content to string if it's not already
            if not isinstance(content, str):
                content = str(content)
            
            # Resolve relative paths relative to the project root
            if not os.path.isabs(file_path):
                project_root = os.getenv("PROJECT_ROOT", os.getcwd())
                file_path = os.path.abspath(os.path.join(project_root, file_path))
            
            # Security check: prevent directory traversal
            if not self._is_safe_path(file_path):
                return f"Error: Access to '{file_path}' is not allowed"
            
            # Create parent directories if needed
            if create_dirs:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write the file
            with open(file_path, mode, encoding=encoding) as file:
                bytes_written = file.write(content)
            
            # Verify the file was written
            if not os.path.exists(file_path):
                return f"Error: Failed to write to file: {file_path}"
            
            self.logger.info("Successfully wrote %d bytes to %s", bytes_written, file_path)
            
            return {
                "status": "success",
                "file_path": file_path,
                "bytes_written": bytes_written,
                "message": "File written successfully"
            }
            
        except PermissionError:
            return f"Error: Permission denied when writing to: {file_path}"
        except OSError as e:
            if hasattr(e, 'strerror'):
                return f"Error: {e.strerror}: {file_path}"
            return f"Error: {str(e)}: {file_path}"
        except Exception as e:
            self.logger.exception("Error in FileWriter")
            return f"Error: {str(e)}"
    
    def _is_safe_path(self, file_path: str) -> bool:
        """
        Check if the file path is safe to write to.
        Prevents directory traversal attacks.
        
        Args:
            file_path: The absolute path to check
            
        Returns:
            bool: True if the path is safe, False otherwise
        """
        # Get the project root directory
        project_root = os.path.abspath(os.getenv("PROJECT_ROOT", os.getcwd()))
        
        # Resolve the absolute path and check if it's within the project root
        abs_path = os.path.abspath(file_path)
        
        # Ensure the path is within the project directory
        return os.path.commonpath([project_root]) == os.path.commonpath([project_root, abs_path])
