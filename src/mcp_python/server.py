import asyncio
import io
import subprocess
import re
from contextlib import redirect_stdout, redirect_stderr
import traceback
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
import time
from mcp.server.fastmcp import FastMCP

# Set up logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Load environment variables from .env file into os.environ
load_dotenv(override=True)

log_file = os.path.join(log_dir, f"python_repl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create the FastMCP server instance
mcp = FastMCP("PythonREPL")

@mcp.tool()
async def execute_python(code: str, reset: bool = False) -> str:
    """Execute Python code and return the output. Variables persist between executions.
    Environment variables can be accessed using os.environ.get() or os.getenv().
    
    Args:
        code: Python code to execute
        reset: Reset the Python session (clear all variables)
        
    Returns:
        The execution output or error message
    """
    # Access the global namespace from the server instance
    global_namespace = getattr(mcp, 'global_namespace', {
        "__builtins__": __builtins__,
        "os": os,
    })
    
    if reset:
        global_namespace.clear()
        global_namespace.update({
            "__builtins__": __builtins__,
            "os": os,
        })
        return "Python session reset. All variables cleared."

    # Capture stdout and stderr
    stdout = io.StringIO()
    stderr = io.StringIO()
    
    try:
        # Execute code with output redirection
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exec(code, global_namespace)
        
        # Combine output
        output = stdout.getvalue()
        errors = stderr.getvalue()
        
        # Format response
        result = ""
        if output:
            result += f"Output:\n{output}"
        if errors:
            result += f"\nErrors:\n{errors}"
        if not output and not errors:
            # Try to get the value of the last expression
            try:
                last_line = code.strip().split('\n')[-1]
                last_value = eval(last_line, global_namespace)
                result = f"Result: {repr(last_value)}"
            except (SyntaxError, ValueError, NameError):
                result = "Code executed successfully (no output)"
        
        # Store the updated namespace
        setattr(mcp, 'global_namespace', global_namespace)
        
        return result
                
    except Exception as e:
        # Capture and format any exceptions
        error_msg = f"Error executing code:\n{traceback.format_exc()}"
        # Log the error
        logging.error(f"Execution failed:\n{error_msg}")
        return error_msg

@mcp.tool()
async def initialize_project(project_name: str) -> str:
    """Initialize a new project with timestamp prefix.
    
    Args:
        project_name: Current project name. Will be used as the directory name.
        
    Returns:
        Confirmation message with project directory path
    """
    project_name = time.strftime("%Y%m%d_%H%M%S") + "_" + project_name
    
    # Get project root or use current directory as fallback
    project_root = os.getenv("PROJECTS_ROOT", os.getcwd())
    project_dir = os.path.join(project_root, project_name)
    
    try:
        os.makedirs(project_dir, exist_ok=True)
        os.chdir(project_dir)
        
        logging.info(f"Project initialized in {project_dir}")
        
        return f"Project successfully initialized in {project_dir}"
    except Exception as e:
        error_msg = f"Failed to initialize project: {str(e)}"
        logging.error(error_msg)
        return error_msg

@mcp.tool()
async def install_package(package: str) -> str:
    """Install a Python package using uv.
    
    Args:
        package: Package name to install (e.g., 'pandas')
        
    Returns:
        Installation result message
    """
    # Basic package name validation
    if not re.match("^[A-Za-z0-9][A-Za-z0-9._-]*$", package):
        return f"Invalid package name: {package}"
    
    try:
        # Install package using uv
        process = subprocess.run(
            ["uv", "pip", "install", package],
            capture_output=True,
            text=True,
            check=True
        )

        if process.returncode != 0:
            return f"Failed to install package: {process.stderr}"
        
        # Import the package to make it available in the REPL
        try:
            # Get the base package name without extras
            base_package = package.split('[')[0]
            # Execute the import in the global namespace
            exec(f"import {base_package}", getattr(mcp, 'global_namespace', globals()))
            return f"Successfully installed and imported {package}"
        except ImportError as e:
            return f"Package installed but import failed: {str(e)}"
            
    except subprocess.CalledProcessError as e:
        return f"Failed to install package:\n{e.stderr}"

@mcp.tool()
async def list_variables() -> str:
    """List all variables in the current session.
    
    Returns:
        Formatted string of current variables and their values
    """
    # Get the global namespace
    global_namespace = getattr(mcp, 'global_namespace', {})
    
    # Filter out builtins and private variables
    vars_dict = {
        k: repr(v) for k, v in global_namespace.items() 
        if not k.startswith('_') and k != '__builtins__'
    }
    
    if not vars_dict:
        return "No variables in current session."
    
    # Format variables list
    var_list = "\n".join(f"{k} = {v}" for k, v in vars_dict.items())
    return f"Current session variables:\n\n{var_list}"

@mcp.tool()
async def create_file(filename: str, content: str) -> str:
    """Create a new file with the specified content. Supports nested directories.
    
    Args:
        filename: Path to the file to create (can include directories)
        content: Content to write to the file
        
    Returns:
        Success or error message
    """
    try:
        # Create directories if they don't exist
        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)
            
        # Write the content to the file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
            
        abs_path = os.path.abspath(filename)
        logging.info(f"File created successfully: {abs_path}")
        return f"File created successfully at {abs_path}"
        
    except Exception as e:
        error_msg = f"Failed to create file {filename}: {str(e)}"
        logging.error(error_msg)
        return error_msg

@mcp.tool()
async def load_file(filename: str) -> str:
    """Load and execute a Python script file in the current REPL session.
    The script's variables and functions will be available in the global namespace.
    
    Args:
        filename: Path to the Python script to load and execute
        
    Returns:
        Execution result or error message
    """
    try:
        # Check if file exists
        if not os.path.exists(filename):
            return f"Error: File {filename} not found"
            
        # Read the file content
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
            
        # Execute the code using our execute_python tool to maintain the same environment
        result = await execute_python(code)
        
        logging.info(f"Successfully loaded and executed {filename}")
        return f"File {filename} loaded and executed:\n{result}"
        
    except Exception as e:
        error_msg = f"Failed to load file {filename}: {str(e)}"
        logging.error(error_msg)
        return error_msg

# Initialize the global namespace
setattr(mcp, 'global_namespace', {
    "__builtins__": __builtins__,
    "os": os,
})

async def main():
    await mcp.run_stdio_async()

if __name__ == "__main__":
    import anyio
    anyio.run(main)
