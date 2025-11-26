# Agents

## Commands
- **Dev**: `uv run run.py` (auto-reload), `uv run run.py --port 3000` (custom port)
- **Deps**: `uv sync`
- **Lint**: `uv run ruff check .` (`--fix` to auto-fix), `uv run ruff format .`
- **Test**: `pytest` (all), `pytest tests/test_file.py::TestClass::test_method` (single), `pytest -v` (verbose)

## Code Style
- **Architecture**: Router-based FastAPI (`app/routers/`), component templates, WebSockets + HTMX
- **Styling**: Tailwind CSS via Play CDN, mobile-first responsive design
- **Imports**: Group by stdlib/third-party/local, absolute imports in app package
- **Naming**: snake_case functions/variables, PascalCase classes, UPPER_CASE constants, lowercase_underscores templates
- **Types**: Use type hints on parameters/returns (e.g., `async def func(id: str) -> dict:`)
- **Error Handling**: try/except for expected errors, FastAPI HTTP exceptions, appropriate logging
- **Async**: Use async route handlers, await operations
- **HTMX**: `hx-post`/`hx-get` for requests, `hx-target`/`hx-swap` for DOM updates, prefer SSR over client JS
