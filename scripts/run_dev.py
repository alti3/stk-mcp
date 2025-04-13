import subprocess
import sys
import os

def run():
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    # Go up one level to the project root
    project_root = os.path.dirname(script_dir)
    # Construct the path to the server file relative to the project root
    server_file_path = os.path.join('src', 'stk_mcp', 'server.py')
    # Construct the full path for clarity, though relative might work
    full_server_path = os.path.join(project_root, server_file_path)

    # Ensure the server file exists
    if not os.path.exists(full_server_path):
        print(f"Error: Server file not found at {full_server_path}")
        sys.exit(1)

    # Command to run
    # Use sys.executable to ensure the correct python environment is used for mcp
    command = [sys.executable, "-m", "mcp", "dev", server_file_path]

    print(f"Running MCP development server: {' '.join(command)}")
    print(f"Working Directory: {project_root}")

    try:
        # Run the command from the project root directory
        subprocess.run(command, check=True, cwd=project_root)
    except subprocess.CalledProcessError as e:
        print(f"MCP server exited with error: {e}")
    except KeyboardInterrupt:
        print("\nMCP server stopped.")
    except FileNotFoundError:
         print(f"Error: '{sys.executable} -m mcp' command not found.")
         print("Ensure mcp is installed in your environment (uv sync)")


if __name__ == "__main__":
    run() 