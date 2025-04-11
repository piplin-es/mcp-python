import os
import pytest
import sys
import tempfile
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from mcp_python.server import PythonREPLServer

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname

@pytest.fixture
def server(temp_dir):
    """Create a server instance with PROJECT_ROOT set to a temporary directory"""
    os.environ["PROJECT_ROOT"] = temp_dir
    return PythonREPLServer()

def test_initialize_project_and_create_file(server, temp_dir):
    # Test project initialization
    project_name = "test_project"
    result = server.initialize_project(project_name)
    
    # Check if the result is a list with one TextContent item
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].type == "text"
    
    # Get the project directory from the result message
    project_dir = result[0].text.split()[-1]  # Gets the last word which should be the path
    
    # Verify the project directory exists
    assert os.path.exists(project_dir)
    assert project_dir.startswith(temp_dir)  # Ensure we're creating in the temp directory
    
    # Test file creation using execute_python
    test_file = "test.txt"
    code = f'''
with open("{test_file}", "w") as f:
    f.write("")
'''
    
    result = server.execute_python(code)
    
    # Verify the file was created
    file_path = os.path.join(project_dir, test_file)
    assert os.path.exists(file_path)
    
    # Clean up - remove the test file
    os.remove(file_path) 