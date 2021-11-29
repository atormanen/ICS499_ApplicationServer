"""The game module contains only a Game class"""
import json
from socket import error as socket_error
from socket import socket as socket_cls
from threading import Thread

from game.chess_color import ChessColor
from game.player import Player
from global_logger import *


class Game:
    """A Game object provides ways to access attributes of a given game, add a second player,
        evaluate match results, and handle match communication.
    """

    def __init__(self, game_token, parsed_data, p_one_ip, p_one_port, socket, listener, db):
        self.db = db
        self.listener = listener
        self.game_token = game_token
        self.player_one_socket_initial: socket_cls = socket
        self.player_two_socket_initial: Optional[socket_cls] = None
        self.player_one_socket_initial_flag = 0
        self.player_two_socket_initial_flag = 0
        self.response_obj = ''
        self.last_move = False
        self.game_closed_flag = False
        self.chess_color = ChessColor()
        self.player_one: Player = Player(game_token=self.game_token,
                                         username=parsed_data["username"],
                                         signon_token=parsed_data["signon_token"],
                                         ip=p_one_ip,
                                         port=p_one_port,
                                         socket=socket,
                                         color=ChessColor.get_random_color(),
                                         avatar=self.db.get_avatar(parsed_data["username"]))
        self.player_two: Optional[Player] = None

    def listen(self, socket):
        while not self.last_move:
            # msg = socket.recv(1024) test
            self.listener.process_request(socket, (self.player_one.ip, self.player_one.port))

    @logged_method
    def check_if_still_alive(self, username) -> bool:

        if username == self.player_one.username:
            try:
                self.player_one.socket.send("socket test".encode("utf-8"))
            except socket_error:
                log('socket is dead', level=VERBOSE)
                return False
        elif self.player_two is not None and username == self.player_two.username:
            try:
                self.player_two.socket.send("socket test".encode("utf-8"))
            except socket_error:
                log('socket is dead', level=VERBOSE)
                return False
        else:  # the username is not associated with a player in this game
            return False

        # socket test passed
        return True

    @logged_method
    def add_player_two(self, username, signon_token, p_two_ip, p_two_port, socket):

        self.player_two = Player(game_token=self.game_token,
                                 username=username,
                                 signon_token=signon_token,
                                 ip=p_two_ip,
                                 port=p_two_port,
                                 socket=socket,
                                 color=ChessColor.get_other_color(self.player_one.color),
                                 avatar=self.db.get_avatar(username))
        self.player_two_socket_initial = socket

        # now that we have two players, we set the opponent properties on the Player objects
        self.player_two.opponent = self.player_one
        self.player_one.opponent = self.player_two

    @logged_method
    def add_player_one_socket(self, socket):

        self.player_one.socket = socket
        self.player_one.socket.setblocking(False)
        self.player_one_socket_initial_flag = 1
        # TODO: find a different way to handle multpiple sockets
        thread = Thread(target=self.listen, args=(self.player_one.socket,))
        thread.start()

    @logged_method
    def add_player_two_socket(self, socket):

        self.player_two.socket = socket
        self.player_two.socket.setblocking(False)
        self.player_two_socket_initial_flag = 1
        # TODO: find a different way to handle multpiple sockets
        thread = Thread(target=self.listen, args=(self.player_two.socket,))
        thread.start()

    @logged_method
    def forward_match_communication(self, sender_username, communication_obj) -> bool:
        """Forwards the communication to the other player

        Args:
            sender_username: the username of the sender
            communication_obj: the communication object to be sent

        Returns:
            bool: True if successful, else False
        """

        if (sender_username == self.player_one.username):
            try:
                self.player_two.socket.send(str(communication_obj).encode("utf-8"))
                return True
            except socket_error:
                return False
        # self.player_one_username.socket.send(str(succsess_response()).encode("utf-8"))
        elif (sender_username == self.player_two.username):
            try:
                self.player_one.socket.send(str(communication_obj).encode("utf-8"))
                return True
            except socket_error:
                return False

        # self.player_two.socket.send(str(succsess_response()).encode("utf-8"))
        else:  # no player matched the requester's username
            log(f"{sender_username} was not found in this game", level=VERBOSE)
            return False

    @logged_method
    def create_random_game_response(self):

        response = {"request_type": "request_game", "status": "success",
                    "game_token": self.game_token,
                    "player_one_username": self.player_one.username,
                    "player_two": self.player_two.username,
                    "player_one_color": self.player_one.color,
                    "player_two_color": self.player_two.color,
                    "player_one_ip": self.player_one.ip,
                    "player_one_port": self.player_one.port,
                    "player_two_ip": self.player_two.ip,
                    "player_two_port": self.player_two.port,
                    "player_one_avatar": self.player_one.avatar,
                    "player_two_avatar": self.player_two.avatar}
        self.response_obj = json.dumps(response)

    @logged_method
    def send_game_response(self):

        self.create_random_game_response()
        self.player_one_socket_initial.send(self.response_obj.encode("utf-8"))
        self.player_two_socket_initial.send(self.response_obj.encode("utf-8"))
        self.player_one_socket_initial.close()
        self.player_two_socket_initial.close()
