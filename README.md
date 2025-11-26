# Decrypto Clone

An online multiplayer clone of the board game Decrypto, built for playing with friends.

## Description

Decrypto is a word-based deduction game where teams compete to guess secret words based on clues while preventing the opposing team from intercepting them.

This web application allows players to play Decrypto online with a mobile-first design.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTMX (HTML, CSS, JavaScript)
- **Design**: Mobile-first responsive

## Features

- Online multiplayer gameplay
- Simple interface with two tabs: My Team and Other Team
- Mobile-optimized

## Project Structure

- `app/`: Main application code
  - `data/`: Game data (e.g., wordlist.txt)
  - `templates/`: HTMX templates
  - `main.py`: FastAPI application
- `run.py`: Entry point script
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
