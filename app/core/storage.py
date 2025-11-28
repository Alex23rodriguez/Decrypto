import secrets
from collections import defaultdict
from typing import Callable, TypedDict
from fastapi import WebSocket
from pydantic import BaseModel

MIN_NUM_PLAYERS = 4


class _Player(BaseModel):
    ws: WebSocket
    name: str | None = None
    ready: bool = False


class _Lobby(BaseModel):
    _rooms: defaultdict[str, dict[str, _Player]] = defaultdict(dict)

    def get_players(self, room_id: str):
        return [p.model_copy() for p in self._rooms[room_id].values()]

    def get_ready_players(self, room_id: str):
        return [p.model_copy() for p in self._rooms[room_id].values() if p.ready]

    def can_start_game(self, room_id: str, player_id: str):
        players = self._rooms[room_id]
        if not players[player_id].ready:
            return False

        return sum(p.ready for p in players.values()) >= MIN_NUM_PLAYERS

    async def broadcast_message(
        self, room_id: str, message: str | Callable[[_Player], str]
    ):
        for p in self._rooms[room_id].values():
            if isinstance(message, str):
                await p.ws.send_text(message)
            else:
                await p.ws.send_text(message(p))

    def add_player(self, room_id: str, ws: WebSocket):
        players = self._rooms[room_id]

        for pid, p in players.items():
            if ws == p.ws:
                return pid

        player_id = secrets.token_urlsafe(32)
        players[player_id] = _Player(ws=ws)
        return player_id

    def remove_player(self, room_id: str, player_id: str):
        room = self._rooms[room_id]
        room.pop(player_id)
        if not room:
            del self._rooms[room_id]

    def update_player_ready(self, room_id: str, player_id: str, ready: bool):
        self._rooms[room_id][player_id].ready = ready

    def _is_valid_name(self, name: str):
        if 0 < len(name.strip()) < 32:
            return True

        return False

    def update_player_name(self, room_id: str, player_id: str, name: str | None):
        room = self._rooms[room_id]
        if name is None:
            room[player_id].name = None
            return True

        if not self._is_valid_name(name):
            return False

        taken = any(
            player_id != other_id and name == other.name
            for other_id, other in room.items()
        )
        if taken:
            return False

        room[player_id].name = name
        return True

    def start_game(self, room_id) -> list[_Player]:
        ready_players = {
            player_id: player.model_copy()
            for player_id, player in self._rooms[room_id].items()
            if player.ready
        }
        started = _games.new_game(
            room_id,
            ready_players,
        )
        if started:
            return list(ready_players.values())
        return []


class _Games(BaseModel):
    _rooms: defaultdict[str, dict[str, _Player]] = defaultdict(dict)

    def new_game(self, room_id: str, room: dict[str, _Player]):
        if room_id in self._rooms:
            return False
        self._rooms[room_id] = room
        return True


_lobby = _Lobby()
_games = _Games()


def get_lobby_storage():
    return _lobby


def get_games_storage():
    return _games
