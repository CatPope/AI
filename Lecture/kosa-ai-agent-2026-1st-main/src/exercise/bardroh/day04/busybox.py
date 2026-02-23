import os
import subprocess
import shutil
from typing import List, Dict, Optional, Tuple
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("busybox")

WORKING_DIR = "/home/ubuntu/"

def validate_path(path: str) -> str:
    """Validate and normalize a path to ensure it's within working directory"""
    abs_path = os.path.abspath(os.path.join(WORKING_DIR, path))
    
    if not abs_path.startswith(WORKING_DIR):
        raise ValueError(f"Access denied: Path '{path}' is outside the working directory")
    
    return abs_path

@mcp.tool()
def set_working_directory(directory: str) -> str:
    """Set the working directory for all operations"""
    global WORKING_DIR
    
    abs_path = os.path.abspath(directory)
    
    if not os.path.isdir(abs_path):
        return f"Error: Directory '{directory}' does not exist"
    
    WORKING_DIR = abs_path
    return f"Working directory set to: {WORKING_DIR}"

@mcp.tool()
def ls(path: str = ".", show_hidden: bool = False) -> str:
    """List files and directories at the specified path"""
    try:
        abs_path = validate_path(path)
        
        if not os.path.exists(abs_path):
            return f"Error: Path '{path}' does not exist"
        
        if os.path.isfile(abs_path):
            return f"File: {os.path.basename(abs_path)}"
        
        items = os.listdir(abs_path)
        
        if not show_hidden:
            items = [item for item in items if not item.startswith('.')]
        
        result = []
        for item in sorted(items):
            item_path = os.path.join(abs_path, item)
            item_type = "DIR" if os.path.isdir(item_path) else "FILE"
            item_size = os.path.getsize(item_path)
            result.append(f"{item_type:<4} {item_size:<8} {item}")
        
        header = f"Contents of {abs_path}:\n"
        if not result:
            return header + "Directory is empty"
        
        return header + "\n".join(result)
    
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Error listing directory: {str(e)}"

@mcp.resource("file://{file_path}")
def read_file(file_path: str) -> str:
    """Read the content of a file"""
    try:
        abs_path = validate_path(file_path)
        
        if not os.path.exists(abs_path):
            return f"Error: File '{file_path}' does not exist"
        
        if os.path.isdir(abs_path):
            return f"Error: '{file_path}' is a directory, not a file"
        
        with open(abs_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
def cp(source: str, destination: str) -> str:
    """Copy a file or directory"""
    try:
        src_path = validate_path(source)
        dst_path = validate_path(destination)
        
        if not os.path.exists(src_path):
            return f"Error: Source '{source}' does not exist"
        
        if os.path.isdir(src_path):
            if os.path.exists(dst_path) and os.path.isdir(dst_path):
                final_dst = os.path.join(dst_path, os.path.basename(src_path))
            else:
                final_dst = dst_path
            
            shutil.copytree(src_path, final_dst)
            return f"Directory '{source}' copied to '{destination}'"
        else:
            if os.path.exists(dst_path) and os.path.isdir(dst_path):
                final_dst = os.path.join(dst_path, os.path.basename(src_path))
            else:
                final_dst = dst_path
            
            shutil.copy2(src_path, final_dst)
            return f"File '{source}' copied to '{destination}'"
    
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Error copying: {str(e)}"

@mcp.tool()
def mv(source: str, destination: str) -> str:
    """Move a file or directory"""
    try:
        src_path = validate_path(source)
        dst_path = validate_path(destination)
        
        if not os.path.exists(src_path):
            return f"Error: Source '{source}' does not exist"
        
        if os.path.exists(dst_path) and os.path.isdir(dst_path):
            final_dst = os.path.join(dst_path, os.path.basename(src_path))
        else:
            final_dst = dst_path
        
        shutil.move(src_path, final_dst)
        return f"'{source}' moved to '{destination}'"
    
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Error moving: {str(e)}"

@mcp.tool()
def rm(path: str, recursive: bool = False) -> str:
    """Remove a file or directory"""
    try:
        abs_path = validate_path(path)
        
        if not os.path.exists(abs_path):
            return f"Error: Path '{path}' does not exist"
        
        if os.path.isdir(abs_path):
            if not recursive:
                return f"Error: '{path}' is a directory. Use recursive=True to remove directories"
            
            shutil.rmtree(abs_path)
            return f"Directory '{path}' removed recursively"
        else:
            os.remove(abs_path)
            return f"File '{path}' removed"
    
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Error removing: {str(e)}"

@mcp.tool()
def mkdir(path: str) -> str:
    """Create a new directory"""
    try:
        abs_path = validate_path(path)
        
        if os.path.exists(abs_path):
            return f"Error: Path '{path}' already exists"
        
        os.makedirs(abs_path)
        return f"Directory '{path}' created"
    
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Error creating directory: {str(e)}"

@mcp.tool()
def write_file(file_path: str, content: str, append: bool = False) -> str:
    """Write content to a file"""
    try:
        abs_path = validate_path(file_path)
        
        if os.path.exists(abs_path) and os.path.isdir(abs_path):
            return f"Error: '{file_path}' is a directory, not a file"
        
        parent_dir = os.path.dirname(abs_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        
        mode = 'a' if append else 'w'
        with open(abs_path, mode, encoding='utf-8') as f:
            f.write(content)
        
        action = "appended to" if append else "written to"
        return f"Content {action} '{file_path}'"
    
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Error writing to file: {str(e)}"

@mcp.tool()
def pwd() -> str:
    """Get the current working directory"""
    return WORKING_DIR

@mcp.tool()
def execute_command(command: str, args: List[str] = None) -> str:
    """Execute an external command with arguments"""
    try:
        if args is None:
            args = []
        
        safe_commands = ["zip", "unzip", "tar", "gzip", "grep", "find", "sort", "wc", "cat", "head", "tail"]
        if command not in safe_commands:
            return f"Error: Command '{command}' is not allowed. Allowed commands: {', '.join(safe_commands)}"
        
        full_command = [command] + args
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            cwd=WORKING_DIR,
            timeout=60
        )
        
        output = result.stdout
        error = result.stderr
        
        if result.returncode != 0:
            return f"Command failed with exit code {result.returncode}:\n{error}"
        
        return f"Command executed successfully:\n{output}"
    
    except subprocess.TimeoutExpired:
        return "Error: Command execution timed out"
    except Exception as e:
        return f"Error executing command: {str(e)}"

@mcp.tool()
def file_info(path: str) -> Dict:
    """Get detailed information about a file or directory"""
    try:
        abs_path = validate_path(path)
        
        if not os.path.exists(abs_path):
            return {"error": f"Path '{path}' does not exist"}
        
        stat_info = os.stat(abs_path)
        
        info = {
            "path": abs_path,
            "relative_path": os.path.relpath(abs_path, WORKING_DIR),
            "exists": os.path.exists(abs_path),
            "is_file": os.path.isfile(abs_path),
            "is_dir": os.path.isdir(abs_path),
            "size_bytes": stat_info.st_size,
            "last_modified": stat_info.st_mtime,
            "permissions": oct(stat_info.st_mode)[-3:],
            "owner_id": stat_info.st_uid,
            "group_id": stat_info.st_gid
        }
        
        if os.path.isdir(abs_path):
            info["contents"] = os.listdir(abs_path)
        
        return info
    
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Error getting file info: {str(e)}"}

@mcp.tool()
def find_files(search_pattern: str, path: str = ".") -> List[str]:
    """Search for files matching a pattern"""
    try:
        abs_path = validate_path(path)
        
        if not os.path.exists(abs_path):
            return [f"Error: Path '{path}' does not exist"]
        
        if not os.path.isdir(abs_path):
            return [f"Error: '{path}' is not a directory"]
        
        results = []
        
        for root, dirs, files in os.walk(abs_path):
            if not root.startswith(WORKING_DIR):
                continue
                
            for name in files + dirs:
                if search_pattern in name:
                    result_path = os.path.join(root, name)
                    rel_path = os.path.relpath(result_path, WORKING_DIR)
                    results.append(rel_path)
        
        if not results:
            return [f"No files matching '{search_pattern}' found in '{path}'"]
        
        return results
    
    except ValueError as e:
        return [str(e)]
    except Exception as e:
        return [f"Error searching for files: {str(e)}"]

if __name__ == "__main__":
    mcp.run(transport="sse")