# Agents

This file documents the commands and agents used in the development process.

## Commands

### Development
- `uv run run.py` - Start development server with auto-reload
- `uv sync` - Install/update dependencies

### Linting & Formatting
- `uv run ruff check .` - Lint code
- `uv run ruff check . --fix` - Auto-fix linting issues
- `uv run ruff format .` - Format code

### Testing
- `pytest` - Run all tests
- `pytest tests/test_file.py::TestClass::test_method` - Run single test
- `pytest -v` - Run tests with verbose output

## Code Style Guidelines

### Imports
- Group imports: standard library, third-party, local
- Use absolute imports within the app package
- Example: `from fastapi import FastAPI, Request`

### Naming Conventions
- Functions: snake_case (e.g., `read_item`)
- Variables: snake_case (e.g., `item_id`)
- Classes: PascalCase (not yet used)
- Constants: UPPER_CASE (not yet used)

### Types
- Use type hints for function parameters and return values
- Example: `async def read_item(_: Request, id: str) -> dict:`

### Error Handling
- Use try/except blocks for expected errors
- Raise appropriate HTTP exceptions from FastAPI
- Log errors appropriately

### Async/Await
- Use async functions for FastAPI route handlers
- Await async operations
