from __future__ import annotations

from socket import socket as socket

from global_logger import *


class Player:
    """Represents a player within a Game"""

    def __init__(self, game_token: str, username: str, signon_token: str, ip: str, port, socket: socket, color: str,
                 avatar):
        self._game_token: str = game_token
        self._username: str = username
        self._signon_token: str = signon_token
        self._color: str = color
        self._avatar = avatar
        self._ip: str = ip
        self._port = port
        self._socket: Optional[socket] = socket
        self._opponent: Optional[Player] = None

    @property
    def game_token(self):
        """The token representing the game in which the player is participating"""
        return self._game_token

    @property
    def signon_token(self):
        """The token representing the player's sign-in to their account"""
        return self._signon_token

    @property
    def color(self) -> str:
        """

        Returns:
            str: 'white' if the player is playing white, else 'black'
        """
        return self._color

    @property
    def avatar(self):
        """The player's avatar, an image representing the player."""
        return self._avatar

    @property
    def ip(self):
        """The IP address of the player."""
        return self._ip

    @property
    def port(self):
        """The port on which the player is listening."""
        return self._port

    @property
    def socket(self) -> socket:
        """The socket on which the player is connected."""
        return self._socket

    @socket.setter
    def socket(self, value: socket):
        self._socket = value

    @property
    def opponent(self) -> Player:
        """The opponent which this player is playing."""
        return self._opponent

    @opponent.setter
    def opponent(self, value: Player):
        self._opponent = value

    @property
    def username(self) -> str:
        """The username associated with the player"""
        return self._username
