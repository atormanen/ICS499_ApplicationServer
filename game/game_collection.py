import multiprocessing
from threading import Thread
from typing import Dict, Optional

from database.db import DB
from game.game import Game


class GameCollection:

    def __init__(self, listener):
        self.listener = listener
        self.game_dict: Dict[str, Game] = dict()
        self.open_game_queue: list[Game] = []
        self.moveQueue = []  # I can't find the usage of this anywhere. If we can remove then FIXME
        self.lock = multiprocessing.Lock()
        self.db: Optional[DB] = None

    # self.socketChecker()

    def check_sockets(self):
        while True:  # should we have this eventually end? If so FIXME
            # print("checking sockets")
            for key, value in self.game_dict.items():
                print("Checking sockets")
                print("key: " + key + "     game_token: " + value.game_token)
                self.listener.process_request(value.player_one.socket, (value.player_one.ip, value.player_one.port))
                self.listener.process_request(value.player_two.socket, (value.player_two.ip, value.player_two.port))

    def start_socket_checker(self):
        thread = Thread(target=self.check_sockets)
        print("Starting socket checker")
        thread.start()

    def set_database(self, database):
        self.db = database

    def open_game_available(self):
        if (len(self.open_game_queue) > 0):
            print("Open game available")
            return True
        else:
            return False

    def check_if_already_in_game(self, username):
        print("Inside check games")
        for key, games in self.game_dict.items():
            print("Key: " + key + "     Value: " + games.game_token)

            if (username == games.player_one):
                if not (games.check_if_still_alive(username)):
                    self.remove_game(games)
                    return False
                else:
                    return True
            elif (username == games.player_two):
                if not (games.check_if_still_alive(username)):
                    self.remove_game(games)
                    return False
                else:
                    return True

        for games in self.open_game_queue:
            print("Value: " + games.player_one)
            if (username == games.player_one):
                if not (games.check_if_still_alive(username)):
                    print("socket not available")
                    self.open_game_queue.remove(games)
                    print(self.open_game_queue)
                    return False
                return True
            elif (username == games.player_two):
                if not (games.check_if_still_alive(username)):
                    print("socket not available")
                    self.open_game_queue.remove(games)
                    print(self.open_game_queue)
                    return False
                return True
        return False

    def add_open_game(self, game):
        self.open_game_queue.append(game)
        return True

    def add_second_player(self, player, signonToken, playerIp, playerPort, socket):
        game = self.open_game_queue.pop(0)
        # username, signonToken, pTwoIp, pOnePort, socket
        game.add_player_two(player, signonToken, playerIp, playerPort, socket)
        self.game_dict[game.game_token] = game
        return game

    def get_game_from_token(self, gameToken):
        try:
            print("GameCollection get_game: " + self.game_dict[gameToken].game_token)
            return self.game_dict[gameToken]
        except KeyError:
            print("KeyError")
            return False

    def get_game(self, username):
        for key, games in self.game_dict.items():
            # print("Key: " + key + "     Value: " + games.game_token)
            if (username == games.player_one):
                return games
            elif (username == games.player_two):
                return games

        for games in self.open_game_queue:
            print("Value: " + games.player_one.username)
            if username == games.player_one.username:
                return games
            elif username == games.player_two.username:
                return games
        return False
        try:  # FIXME unreachable code
            print("GameCollection get_game: " + self.game_dict[gameToken].game_token)
            return self.game_dict[gameToken]
        except KeyError:
            print("KeyError")
            return False

    def remove_game(self, game):
        print("removing game: " + game.game_token)
        removed_result = self.game_dict.pop(game.game_token)
        print("game: " + game.game_token + " has been removed")
        return removed_result

# TODO remove this if we don't need it
    # def make_move(self, parsed_data, req_item):
    #     ## TODO: Check json_obj for end of game
    #     game = self.get_game_from_token(parsed_data["game_token"])
    #     requester = parsed_data["username"]
    #     print(parsed_data)
    #
    #     json_obj = parsed_data["move"]
    #     print(json_obj)
    #
    #     # If this is end of game signal, save game stats in db and send end
    #     # game to both players
    #     try:
    #         if not (json_obj["match_result"] == None):
    #             if (json_obj["match_result"]["type"]["name"] == 'RESIGNATION'):
    #                 print("Resignation*************************")
    #                 if (json_obj["match_result"]["winning_color"]["name"] == 'WHITE'):
    #                     # Send victory to WHITE and defeat to BLACK
    #                     self.db.add_game_won(game.player_two)
    #                     if (json_obj["match_result"]["type"]["name"] == 'RESIGNATION'):
    #                         self.db.add_game_resigned(game.player_one)
    #                     else:
    #                         self.db.add_game_lost(game.player_one)
    #                     type = json_obj["match_result"]["type"]["name"]
    #                 elif (json_obj["match_result"]["winning_color"]["name"] == 'BLACK'):
    #                     # Send victory to BLACK and defeat to WHITE
    #                     self.db.add_game_won(game.player_one)
    #                     if (json_obj["match_result"]["type"]["name"] == 'RESIGNATION'):
    #                         self.db.add_game_resigned(game.player_two)
    #                     else:
    #                         self.db.add_game_lost(game.player_two)
    #                     type = json_obj["match_result"]["type"]["name"]
    #
    #
    #             elif (json_obj["match_result"]["type"]["name"] == 'AGREED_UPON_DRAW'):
    #                 # Draw
    #                 print("DRAW*************************")
    #                 self.db.add_game_played(game.player_one)
    #                 self.db.add_game_played(game.player_two)
    #
    #             game.lastMove = True
    #             game.make_move(requester, json_obj, game.playerOneSocket)
    #             game.make_move(requester, json_obj, game.playerTwoSocket)
    #             if (game.lastMove == True):
    #                 self.remove_game(game)
    #                 game.playerTwoSocket.close()
    #                 game.playerOneSocket.close()
    #                 print("closed player one socket")
    #                 print("closed player one socket")
    #
    #             game.gameClosedFlag = True
    #             return False
    #     except TypeError:
    #         print("Type error")
    #
    #     # Weird way to tell which socket is associated with which player
    #     # Only runs on initial startup of game
    #     if (json_obj == "white"):
    #         print("add_player_two_socket")
    #         game.addPlayerTwoSocket(req_item.connection_socket)
    #         return
    #     elif (json_obj == "black"):
    #         print("add_player_one_socket")
    #         game.addPlayerOneSocket(req_item.connection_socket)
    #         return
    #
    #     game.makeMove(requester, json_obj, req_item.connection_socket)
