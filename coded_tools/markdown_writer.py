import os
from datetime import datetime
from typing import Any, Dict
from neuro_san.interfaces.coded_tool import CodedTool


class MarkdownWriter(CodedTool):
    """CodedTool for writing content to markdown files."""
    
    def __init__(self):
        self.output_dir = "generated_docs"
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
        """
        Write content to a markdown file.
        
        Args:
            args: Dictionary containing:
                - file_name: Name of the markdown file (without .md extension)
                - content: Markdown content to write
                - append: (Optional) If True, append to existing file; if False, overwrite
            sly_data: Dictionary for agent hierarchy data (not used in this tool)
            
        Returns:
            Success message with file path or error message
        """
        try:
            # Extract arguments
            file_name = args.get('file_name', '')
            content = args.get('content', '')
            append = args.get('append', False)
            
            if not file_name:
                return "Error: file_name parameter is required"
            if not content:
                return "Error: content parameter is required"
            
            # Ensure file has .md extension
            if not file_name.endswith('.md'):
                file_name += '.md'
            
            file_path = os.path.join(self.output_dir, file_name)
            
            # Add timestamp header if creating new file
            mode = 'a' if append else 'w'
            
            with open(file_path, mode, encoding='utf-8') as f:
                if not append or not os.path.exists(file_path):
                    # Add metadata header for new files
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"# {file_name.replace('.md', '').replace('_', ' ').title()}\n\n")
                    f.write(f"*Generated on: {timestamp}*\n\n")
                    f.write("---\n\n")
                
                f.write(content)
                f.write("\n\n")
            
            abs_path = os.path.abspath(file_path)
            return f"Successfully wrote content to {abs_path}"
            
        except Exception as e:
            return f"Error writing to file: {str(e)}"
