import secrets
from collections import defaultdict
from dataclasses import dataclass
from pprint import pprint
from typing import Callable

from fastapi import WebSocket
from pydantic import BaseModel

MIN_NUM_PLAYERS = 4


@dataclass
class _Player:
    ws: WebSocket
    name: str | None = None
    ready: bool = False


class _Lobby(BaseModel):
    _rooms: defaultdict[str, dict[str, _Player]] = defaultdict(dict)

    def get_players(self, room_id: str):
        return [p.name for p in self._rooms[room_id].values()]

    def get_ready_players(self, room_id: str):
        return [p.name for p in self._rooms[room_id].values() if p.ready]

    def get_player_name(self, room_id: str, player_id: str):
        return self._rooms[room_id].get(player_id, None)

    def can_start_game(self, room_id: str, player_id: str):
        players = self._rooms[room_id]
        if not players[player_id].ready:
            return False

        return sum(p.ready for p in players.values()) >= MIN_NUM_PLAYERS

    async def broadcast_message(
        self, room_id: str, message: str | Callable[[_Player], str]
    ):
        for p in self._rooms[room_id].values():
            print(f"sending update to {p}")
            if isinstance(message, str):
                await p.ws.send_text(message)
            else:
                await p.ws.send_text(message(p))

    def add_player(self, room_id: str, ws: WebSocket):
        players = self._rooms[room_id]

        for player_id, p in players.items():
            if ws is p.ws:
                return player_id

        player_id = secrets.token_urlsafe(32)
        players[player_id] = _Player(ws=ws)
        pprint(self._rooms)
        return player_id

    def remove_player(self, room_id: str, ws: WebSocket):
        room = self._rooms[room_id]
        for player_id, p in room.items():
            if p.ws is ws:
                room.pop(player_id)
                break

        if not room:
            del self._rooms[room_id]

    def _get_player_id_from_socket(self, room_id: str, ws):
        for player_id, p in self._rooms[room_id].items():
            if p.ws is ws:
                return player_id
        raise AssertionError("websocket not found")

    def update_player_ready(self, room_id: str, ws: WebSocket, ready: bool):
        player_id = self._get_player_id_from_socket(room_id, ws)
        self._rooms[room_id][player_id].ready = ready

    def _is_valid_name(self, name: str):
        if 0 < len(name.strip()) < 32:
            return True

        return False

    def update_player_name(self, room_id: str, ws: WebSocket, name: str | None):
        player_id = self._get_player_id_from_socket(room_id, ws)
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
            player_id: player
            for player_id, player in self._rooms[room_id].items()
            if player.ready
        }

        started = _games.new_game(
            room_id,
            {
                player_id: player.name or "(no name)"
                for player_id, player in ready_players.items()
            },
        )
        if started:
            return list(ready_players.values())
        return []


class _Games(BaseModel):
    _rooms: dict[str, dict[str, str]] = defaultdict(dict)

    def new_game(self, room_id: str, room: dict[str, str]):
        if room_id in self._rooms:
            return False
        self._rooms[room_id] = room
        return True

    def get_room_info(self, room_id: str, player_id: str | None):
        room = self._rooms.get(room_id, None)
        if room is None:
            return {"error": "room not found"}

        if player_id is None:
            return {"error": "player token not found"}

        if player_id not in room:
            return {"error": "player not part of room"}

        return {"state": None, "players": room.values(), "player_name": room[player_id]}

    def get_player_info(self, room_id: str, player_id: str):
        return self._rooms[room_id].get(player_id, None)


_lobby = _Lobby()
_games = _Games()


def get_lobby_storage():
    return _lobby


def get_games_storage():
    return _games
