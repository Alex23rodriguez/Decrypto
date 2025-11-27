# Decrypto Clone

An online multiplayer clone of the board game Decrypto, built for playing with friends.

## Description

Decrypto is a word-based deduction game where teams compete to guess secret words based on clues while preventing the opposing team from intercepting them.

This web application allows players to play Decrypto online with a mobile-first design.

## Tech Stack

- **Backend**: FastAPI (Python) with modular router architecture
- **Frontend**: HTMX (HTML, CSS, JavaScript) with WebSocket extensions
- **Real-time Communication**: WebSockets for live updates and synchronized actions
- **Styling**: Tailwind CSS for mobile-first responsive design
- **Templating**: Jinja2 for server-side rendering

## Features

- **Landing Page**: Attractive entry point explaining the game and allowing room joining
- **Real-time Multiplayer Lobby**: Live player list updates via WebSockets
- **Duplicate Name Prevention**: Server-side validation prevents name conflicts
- **Synchronized Game Start**: All players redirected simultaneously when game starts
- **Responsive Design**: Mobile-first interface using Tailwind CSS
- **Component-based Architecture**: Modular HTMX templates for maintainability

## Project Structure

- `app/`: Main application code
  - `routers/`: Router modules
    - `lobby.py`: Game lobby logic with WebSocket support
    - `game.py`: Game page router
  - `templates/`: Jinja2 templates
    - `index.html`: Landing page
    - `lobby/`: Lobby-related templates
      - `index.html`: Main lobby page
      - `form.html`: Player name input form
      - `joined.html`: Player joined state
      - `player_list.html`: Live player list component
    - `game/`: Game-related templates
      - `index.html`: Game page
  - `data/`: Game data (e.g., wordlist.txt)
  - `main.py`: FastAPI application entry point
- `run.py`: Development server with configurable port
- `pyproject.toml`: Project configuration
- `uv.lock`: Dependency lock file

## Getting Started

### Prerequisites

- Python 3.13
- uv

### Installation

1. Clone the repository
2. Install dependencies: `uv sync`
3. Run the development server: `uv run run.py` (auto-reloads on changes)

### Usage

1. Run the server: `uv run run.py` (or `uv run run.py --port 3000` for custom port)
2. Open the app in your browser (defaults to http://localhost:8000)
3. Enter a room ID on the landing page or share one with friends
4. Join the lobby with a unique name
5. Wait for 4+ players, then click "Start Game" to begin
6. All players will be redirected to the game page simultaneously
