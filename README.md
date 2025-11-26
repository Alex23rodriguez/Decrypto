# Decrypto Clone

An online multiplayer clone of the board game Decrypto, built for playing with friends.

## Description

Decrypto is a word-based deduction game where teams compete to guess secret words based on clues while preventing the opposing team from intercepting them.

This web application allows players to play Decrypto online with a mobile-first design.

## Tech Stack

- **Backend**: FastAPI (Python) with router-based architecture
- **Frontend**: HTMX (HTML, CSS, JavaScript) with WebSocket extensions
- **Real-time Communication**: WebSockets for live player updates
- **Design**: Mobile-first responsive

## Features

- **Real-time Multiplayer Lobby**: Live player list updates via WebSockets
- **Duplicate Name Prevention**: Client-side validation prevents name conflicts
- **Game State Management**: Automatic game start detection when 4+ players join
- **Responsive Design**: Mobile-optimized interface
- **Component-based Architecture**: Modular HTMX templates for maintainability

## Project Structure

- `app/`: Main application code
  - `routers/game/`: Router modules for game functionality
    - `lobby.py`: Game lobby logic with WebSocket support
  - `templates/lobby/`: HTMX template components
    - `index.html`: Main lobby page
    - `form.html`: Player name input form
    - `joined.html`: Player joined state
    - `player_list.html`: Live player list component
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
3. Run the server: `uv run run.py`

### Usage

Open the app in your browser and start a game.
