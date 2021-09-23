import json
from socket import error as socket_error
from socket import socket as socket_cls
from threading import Thread
from typing import Optional

import chess_color
from game.player import Player


class Game:

    def __init__(self, game_token, parsed_data, p_one_ip, p_one_port, socket, listener, db):
        self.db = db
        self.listener = listener
        self.game_token = game_token
        # self.player_one_username = parsed_data["username"]
        # self.player_one_signon_token = parsed_data["signon_token"]
        # self.player_two = ''
        # self.player_two_signon_token = ''
        # self.player_one_color = ''
        # self.player_two_color = ''
        # self.player_one_avatar = ''
        # self.player_two_avatar = ''
        # self.player_one_ip = pOneIp
        # self.player_two_ip = ''
        # self.player_one_port = pOnePort
        # self.player_two_port = ''
        # self.playerOneSocket = ''
        # self.playerTwoSocket = ''
        self.player_one_socket_initial: socket_cls = socket
        Optional[self.player_two_socket_initial: socket_cls] = None
        self.player_one_socket_initial_flag = 0
        self.player_two_socket_initial_flag = 0
        self.responseObj = ''
        self.lastMove = False
        self.gameClosedFlag = False
        self.player_one: Player = Player(game_token=self.game_token,
                                         username=parsed_data["username"],
                                         signon_token=parsed_data["signon_token"],
                                         ip=p_one_ip,
                                         port=p_one_port,
                                         socket=socket,
                                         color=chess_color.get_random_color(),
                                         avatar=self.db.get_avatar(parsed_data["username"]))
        Optional[self.player_two:Player] = None

    def listen(self, socket):
        while (self.lastMove == False):
            # msg = socket.recv(1024) test
            self.listener.processRequest(socket, (self.player_one.ip, self.player_one.port))

    def checkIfStillAlive(self, username) -> bool:
        print("Checking if socket is still alive")
        if username == self.player_one.username:
            try:
                self.player_one.socket.send("socket test".encode("utf-8"))
            except socket_error:
                print("socket is dead")
                return False
        elif self.player_two is not None and username == self.player_two.username:
            try:
                self.player_two.socket.send("socket test".encode("utf-8"))
            except socket_error:
                print("socket is dead")
                return False
        else:  # the username is not associated with a player in this game
            return False

        # socket test passed
        return True

    def add_player_two(self, username, signonToken, pTwoIp, pTwoPort, socket):

        self.player_two = Player(game_token=self.game_token,
                                 username=username,
                                 signon_token=signonToken,
                                 ip=pTwoIp,
                                 port=pTwoPort,
                                 socket=socket,
                                 color=chess_color.get_other_color(self.player_one.color),
                                 avatar=self.db.get_avatar(username))
        self.player_two_socket_initial = socket

        # now that we have two players, we set the opponent properties on the Player objects
        self.player_two.opponent = self.player_one
        self.player_one.opponent = self.player_two

    def add_player_one_socket(self, socket):
        print("player one socket: " + str(socket))
        self.player_one.socket = socket
        self.player_one.socket.setblocking(False)
        self.player_one_socket_initial_flag = 1
        ## TODO: find a different way to handle multpiple sockets
        thread = Thread(target=self.listen, args=(self.playerOneSocket,))
        thread.start()

    def add_player_two_socket(self, socket):
        print("player two socket: " + str(socket))
        self.player_two.socket = socket
        self.player_two.socket.setblocking(False)
        self.player_two_socket_initial_flag = 1
        ## TODO: find a different way to handle multpiple sockets
        thread = Thread(target=self.listen, args=(self.player_two.socket,))
        thread.start()

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
            print(f"{sender_username} was not found in this game")
            return False

    def create_random_game_response(self):
        response = {
            "request_type": "RequestGame",
            "status": "success",
            "game_token": "",
            "player_one_username": "",
            "player_two": "",
            "player_one_color": "",
            "player_two_color": "",
            "player_one_ip": "",
            "player_one_port": "",
            "player_two_ip": ""
        }
        response["game_token"] = self.game_token
        response["player_one_username"] = self.player_one.username
        response["player_two"] = self.player_two.username
        response["player_one_color"] = self.player_one.color
        response["player_two_color"] = self.player_two.color
        response["player_one_ip"] = self.player_one.ip
        response["player_one_port"] = self.player_one.port
        response["player_two_ip"] = self.player_two.ip
        response["player_two_port"] = self.player_two.port
        response["player_one_avatar"] = self.player_one.avatar
        response["player_two_avatar"] = self.player_two.avatar
        self.responseObj = json.dumps(response)

    def send_game_response(self):
        self.create_random_game_response()
        self.player_one_socket_initial.send(self.responseObj.encode("utf-8"))
        self.player_two_socket_initial.send(self.responseObj.encode("utf-8"))
        print(self.player_one.username + "    " + str(self.playerOneSocket))
        print(self.player_two.username + "    " + str(self.playerTwoSocket))
        self.player_one_socket_initial.close()
        self.player_two_socket_initial.close()
