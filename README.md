# Python REPL MCP Server

> This is a fork of [hdresearch/mcp-python](https://github.com/hdresearch/mcp-python), a Python REPL server for MCP protocol. But seems almost nothing is left from the original code.

This MCP server provides a Python REPL (Read-Eval-Print Loop) as a tool. It allows execution of Python code through the MCP protocol with a persistent session.

## Setup

No setup needed! The project uses `uv` for dependency management. All dependencies are automatically managed through the `pyproject.toml` file.

## Environment Variables

The server supports `.env` file for environment variables management. Create a `.env` file in the root directory to store your environment variables. These variables will be automatically loaded and accessible in your Python REPL session using:

```python
import os

# Access environment variables
my_var = os.environ.get('MY_VARIABLE')
# or
my_var = os.getenv('MY_VARIABLE')
```

## Running the Server

Simply run:

```bash
uv run mcp_python
```

## Usage with Claude Desktop

Add this configuration to your Claude Desktop config file:

```json
{
  "mcpServers": {
    "python-repl": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/python-repl-server",
        "run",
        "mcp_python"
      ]
    }
  }
}
```

## Available Tools

The server provides the following tools:

1. `execute_python`: Execute Python code with persistent variables
   - `code`: The Python code to execute
   - `reset`: Optional boolean to reset the session

2. `list_variables`: Show all variables in the current session

3. `install_package`: Install a package from PyPI using `uv`
   - `package`: Name of the package to install

4. `initialize_project`: Create a new project directory with timestamp prefix
   - `project_name`: Name for the project directory

5. `create_file`: Create a new file with specified content
   - `filename`: Path to the file (supports nested directories)
   - `content`: Content to write to the file

6. `load_file`: Load and execute a Python script in the current session
   - `filename`: Path to the Python script to load

## Features

- Persistent Python REPL session
- Automatic environment variable loading from `.env` files
- Package management using `uv`
- Project initialization with timestamped directories
- File creation and management
- Script loading and execution
- Comprehensive logging system
- Support for nested project structures

## Examples

Initialize a new project:

```python
# Create a new project directory
initialize_project("my_project")
```

Create and execute a script:

```python
# Create a new Python file
create_file("script.py", """
def greet(name):
    return f"Hello, {name}!"
""")

# Load and execute the script
load_file("script.py")

# Use the loaded function
print(greet("World"))
```

Install and use a package:

```python
# Install pandas
install_package("pandas")

# Use the installed package
import pandas as pd
df = pd.DataFrame({'A': [1, 2, 3]})
print(df)
```

List all variables:

```python
# Show all variables in the current session
list_variables()
```

Reset the session:

```python
# Use execute_python with reset=true to clear all variables
execute_python("", reset=True)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Here are some ways you can contribute:

- Report bugs
- Suggest new features
- Improve documentation
- Add test cases
- Submit code improvements

Before submitting a PR, please ensure:

1. Your code follows the existing style
2. You've updated documentation as needed
3. All tests pass
4. You've added tests for new features

For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
