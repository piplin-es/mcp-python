# Python REPL MCP Server

This MCP server provides a Python REPL (Read-Eval-Print Loop) as a tool. It allows execution of Python code through the MCP protocol with a persistent session.

## Setup

No setup needed! The project uses `uv` for dependency management.

## Running the Server

Simply run:
```bash
uv run src/python_repl/server.py
```

## Usage with Claude Desktop

Add this configuration to your Claude Desktop config file:

```json
{
    "mcpServers": {
        "python-repl": {
            "command": "uv",
            "args": ["--directory", "/absolute/path/to/python-repl-server", "run", "python-repl"]
        }
    }
}
```

The server provides two tools:

1. `execute_python`: Execute Python code with persistent variables
   - `code`: The Python code to execute
   - `reset`: Optional boolean to reset the session

2. `list_variables`: Show all variables in the current session

## Examples

Set a variable:
```python
a = 42
```

Use the variable:
```python
print(f"The value is {a}")
```

List all variables:
```python
# Use the list_variables tool
```

Reset the session:
```python
# Use execute_python with reset=true
```
