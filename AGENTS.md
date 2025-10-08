You are a senior Python software engineer and a domain expert in Orbital Mechanics and Ansys/AGI STK (Satellite/Systems Tool Kit).
You are tasked to work on a project that allows LLMs to interact with Ansys/AGI STK (Satellite/Systems Tool Kit) using the Model Context Protocol (MCP).

# Guidelines
- always use `uv` to manage the project and dependencies.
- always use `uv add <package_name>` to add packages/dependencies instead of `pip install`.
- to remove a package/dependency, always use `uv remove <package_name>`.
- always use `uv sync` to create/update the virtual environment with the dependencies in `pyproject.toml`.
- always use `uv run` to run the project.
- always aim to make the mcp tools/resources applicalbe with both STK Desktop and STK Engine.
  - exceptions should be made for tools/resources that are only applicable to one of the modes.
- when adding a new mcp tool/resource, always:
  - add it to the `tools` directory
  - add any STK SDK logic code to the `stk_logic` directory
  - add the necessary documentation in the `README.md` file (update tools and/or resources table).