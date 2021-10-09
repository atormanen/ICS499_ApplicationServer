import json
from socket import socket

# TODO: Create subclasses for each message type.
# Too much happening here
from game.game import Game

# Message item is a wrapper class to hold the data of each reqeust.
# It holds the json object that was sent to the server as well as
# the socket

FAILURE = "failure"
SUCCESS = "success"


class MessageItem:

    log_function_name = lambda x: logger.debug(f"func {inspect.stack()[1][3]}")

    def __init__(self, connection_socket: socket, address, parsed_data: dict[str, str]) -> None:
        self.connection_socket: socket = connection_socket
        self.ip_address: str = address[0]
        self.port: int = address[1]
        self.parsed_data: dict[str, str] = parsed_data
        self.response_obj: str = ''


    def invalidRequest(self):
        self.log_function_name()
        response = {
                    "status":"fail - invalid request. please double check request syntax"
        }
        self.responseObj = json.dumps(response)
        

    def create_match_communication_response(self, was_successful) -> None:
        self.log_function_name()
        """Create a response for a match communication request"""
        response = {
            "request_type": "MatchCommunication",
            "result": SUCCESS if was_successful else FAILURE

        }
        self.response_obj = json.dumps(response)

    def create_match_result_report_response(self, was_successful) -> None:
        self.log_function_name()
        """Create a response for a match result report request"""
        response = {
            "request_type": "MatchResultReport",
            "result": SUCCESS if was_successful else FAILURE
        }
        self.response_obj = json.dumps(response)

    def create_error_report_response(self, was_successful: bool) -> None:
        self.log_function_name()
        """Create a response for an error result report request"""
        response = {
            "request_type": "ErrorReport",
            "result": SUCCESS if was_successful else FAILURE
        }
        self.response_obj = json.dumps(response)

    def create_game_resp_not_accepted(self, player_one_username: str, game_token: str) -> None:
        self.log_function_name()
        """Creates a response for a request to create a game, but an opponent hasn't accepted yet"""  # FIXME if needed
        response = {
            "request_type": "CreateGame",
            "player_one_username": player_one_username,
            "game_token": game_token
        }
        self.response_obj = json.dumps(response)

    def accept_game(self, player_one_username: str, player_two_username: str, game_token: str) -> None:
        self.log_function_name()
        """Creates a response for when a game is accepted by the second player"""
        response = {
            "request_type": "CreateGame",
            "player_one_username": player_one_username,
            "player_two": player_two_username,
            "game_token": game_token
        }
        self.response_obj = json.dumps(response)

    def check_for_game_response(self, player_one_username: str, game_token: str) -> None:  # TODO add docString
        self.log_function_name()
        response = {
            "request_type": "CreateGame",
            "username": player_one_username,
            "game_token": game_token
        }
        self.response_obj = json.dumps(response)

    def create_random_game_resp(self, game: Game) -> None:  # TODO add docString
        self.log_function_name()
        response = {
            "request_type": "RequestGame",
            "status": SUCCESS,
            "game_token": game.game_token,
            "player_one_username": game.player_one.username,
            "player_two_username": game.player_two.username,
            "player_one_color": game.player_one.color,
            "player_two_color": game.player_two.color,
            "player_one_ip": game.player_one.ip,
            "player_one_port": game.player_one.port,
            "player_two_ip": game.player_two.ip
        }
        self.response_obj = json.dumps(response)

    def create_random_game_resp_failure(self, username: str, was_successful: str,
                                        reason: str) -> None:  # TODO add docString
        self.log_function_name()
        response = {
            "request_type": "RequestGame",
            "player_one_username": username,
            "status": SUCCESS if was_successful else FAILURE,
            "reason": reason
        }

        self.response_obj = json.dumps(response)

    def cancel_random_game_resp(self, username: str,
                                was_successful: bool) -> None:  # TODO add docString and type of status
        self.log_function_name()
        response = {
            "request_type": "RequestGame",
            "player_one_username": username,
            "status": SUCCESS if was_successful else FAILURE
        }

        self.response_obj = json.dumps(response)

    # FIXME I commented this out because we don't use it.
    #   If we are not going to use it, we should remove it.
    #   If we will use it, it needs to be fixed because there are Errors.
    #
    # def get_game_list_response(self, game_list: list[str], request: str = "getGameList") -> None:
    #     game_dict = {
    #         "game0": "games"
    #     }
    #
    #     i = 0
    #     for item in game_list:
    #         game = {
    #             "game": ""
    #         }
    #         game["game"] = item[1]
    #
    #         game_str = "game" + str(i)
    #         game_dict[game_str] = user
    #         i = i + 1
    #     response = {
    #         "request_type": "getGameList",
    #         "count": "",
    #         "games": ""
    #     }
    #     response["request_type"] = request
    #     response["count"] = len(friendsList)
    #     response["friends"] = str(friendDict)
    #     self.response_obj = json.dumps(response)
