"""
File Reader tool for the CodeGen agent system.

This tool allows agents to read the contents of files from the local filesystem.
"""

import logging
import os
from typing import Any, Dict, Union

from neuro_san.interfaces.coded_tool import CodedTool


class FileReader(CodedTool):
    """
    A tool that reads the contents of a file from the local filesystem.
    
    This tool can be used by agents to read various types of files including
    code files, documentation, and configuration files.
    """
    
    def __init__(self):
        """Initialize the file reader tool with a logger."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        Read the contents of a file from the local filesystem.
        
        Args:
            args: Dictionary containing:
                - file_path: (str) Path to the file to read
                - start_line: (int, optional) Starting line number (1-based). Defaults to 1.
                - end_line: (int, optional) Ending line number (inclusive). If None, reads to end of file.
            sly_data: Dictionary for maintaining state between tool invocations.
            
        Returns:
            Dict containing:
                - content: (str) The file content
                - line_count: (int) Total number of lines in the file
                - truncated: (bool) Whether the content was truncated
            
            Or an error string starting with "Error: " if the operation fails.
        """
        try:
            print("Starting file reader tool")
            # Get and validate file path
            file_path = args.get("file_path")
            if not file_path:
                return "Error: Missing required parameter 'file_path'"
                
            # Get line range parameters with proper type conversion and validation
            try:
                start_line = int(args.get("start_line", 1))
                end_line = args.get("end_line")
                if end_line is not None:
                    end_line = int(end_line)
            except (ValueError, TypeError) as e:
                return f"Error: Invalid line number format: {str(e)}"
            
            if start_line < 1:
                return "Error: start_line must be 1 or greater"
                
            if end_line is not None and end_line < start_line:
                return "Error: end_line must be greater than or equal to start_line"
            
            # Resolve relative paths relative to the project root
            if not os.path.isabs(file_path):
                project_root = os.getenv("PROJECT_ROOT", os.getcwd())
                file_path = os.path.abspath(os.path.join(project_root, file_path))
            
            # Security check: prevent directory traversal
            if not self._is_safe_path(file_path):
                return f"Error: Access to '{file_path}' is not allowed"
            
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            total_lines = len(lines)
            
            # Convert to 0-based index for Python slicing
            start_idx = max(0, start_line - 1)
            end_idx = end_line if end_line is None else min(end_line, total_lines)
            
            # Get the requested lines
            if end_idx is not None:
                content_lines = lines[start_idx:end_idx]
                truncated = end_idx < total_lines
            else:
                content_lines = lines[start_idx:]
                truncated = False
            
            content = ''.join(content_lines)
            
            self.logger.info("Read %d/%d lines from %s", 
                           len(content_lines), total_lines, file_path)
            
            return {
                "content": content,
                "line_count": total_lines,
                "truncated": truncated
            }
            
        except FileNotFoundError:
            return f"Error: File not found: {file_path}"
        except PermissionError:
            return f"Error: Permission denied when reading: {file_path}"
        except UnicodeDecodeError:
            return f"Error: Could not decode file as UTF-8: {file_path}"
        except Exception as e:
            self.logger.exception("Error reading file")
            return f"Error: {str(e)}"
    
    def _is_safe_path(self, file_path: str) -> bool:
        """
        Check if the file path is safe to access.
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
        return os.path.commonpath([project_root]) == os.path.commonpath([project_root, abs_path])
