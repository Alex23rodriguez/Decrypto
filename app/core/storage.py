import secrets
from typing import TypedDict
from fastapi import WebSocket
from pydantic import BaseModel

MIN_NUM_PLAYERS = 4


class _Player(BaseModel):
    ws: WebSocket
    name: str = ""
    ready: bool = False


PlayerDict = TypedDict("PlayerDict", {"ws": WebSocket, "name": str, "ready": bool})


class _Room(BaseModel):
    _room_id: str
    _players: dict[str, _Player] = {}

    def get_players(self) -> list[PlayerDict]:
        return [p.model_dump() for p in self._players.values()]  # type:ignore

    def get_ready_players(self) -> list[PlayerDict]:
        return [p.model_dump() for p in self._players.values() if p.ready]  # type:ignore

    def can_start_game(self, player_id: str):
        return (
            self._players[player_id].ready
            and len(self.get_ready_players()) >= MIN_NUM_PLAYERS
        )

    async def broadcast_message(self, message: str):
        for p in self._players.values():
            await p.ws.send_text(message)

    def add_player(self, ws: WebSocket):
        for pid, p in self._players.items():
            if ws == p.ws:
                return pid

        player_id = secrets.token_urlsafe(32)
        self._players[player_id] = _Player(ws=ws)
        return player_id

    def remove_player(self, player_id: str):
        if player_id in self._players:
            del self._players[player_id]

    def update_player_name(self, player_id: str, name: str):
        p = self._players[player_id]
        p.name = name
        p.ready = bool(name)


class _Lobby(BaseModel):
    _rooms: dict[str, _Room] = {}

    def clean(self):
        for room_id, r in self._rooms.items():
            if not r._players:
                del self._rooms[room_id]

    def __getitem__(self, room_id: str, /) -> _Room:
        if room_id not in self._rooms:
            self._rooms[room_id] = _Room(_room_id=room_id)
        return self._rooms[room_id]


_lobby = _Lobby()


def get_lobby_storage():
    return _lobby
