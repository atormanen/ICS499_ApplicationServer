import json
from socket import socket

# TODO: Create subclasses for each message type.
# Too much happening here
from typing import Dict, List

from game.game import Game

# Message item is a wrapper class to hold the data of each reqeust.
# It holds the json object that was sent to the server as well as
# the socket
from global_logger import logged_method

RESULT = "result"


class RequestType:
    """Constants representing request types."""

    CANCEL_GAME_REQUEST = "cancel_game_request"
    REQUEST_GAME = "request_game"
    CHECK_FOR_GAME = "check_for_game"
    ACCEPT_GAME = "accept_game"
    CREATE_GAME = "create_game"
    MATCH_COMMUNICATION = "match_communication"

    ERROR_REPORT = 'error_report'

    MATCH_RESULT_REPORT = "match_result_report"

    @classmethod
    def get_items(cls) -> List[str]:
        """Gets a list of all items."""
        return []


class Status:
    """Constants representing possible Status values."""
    FAIL = "failure"
    SUCCESS = "success"

    @classmethod
    def get_items(cls) -> List[str]:
        """Gets a list of all items."""
        return [Status.FAIL, Status.SUCCESS]

    @staticmethod
    def was_success(was_success: bool):
        """Gets the status given a boolean representing that the request was processed successfully.

        Args:
            was_success:
                A boolean representing that the request was processed successfully.

        Returns:
            Status.SUCCESS if was_success argument evaluates to True when converted to bool or
                Status.FAIL if was_success argument evaluates to False when converted to bool.

        """
        return Status.SUCCESS if bool(was_success) else Status.FAIL


class FailureReasons:
    """Constants representing failure reason messages."""
    UNSPECIFIED = 'unspecified'

    @classmethod
    def get_items(cls) -> List[str]:
        """Gets a list of all items."""
        return [FailureReasons.UNSPECIFIED]


class MessageItem:

    def __init__(self, connection_socket: socket, address, parsed_data: Dict[str, str]) -> None:
        self.connection_socket: socket = connection_socket
        self.ip_address: str = address[0]
        self.port: int = address[1]
        self.parsed_data: Dict[str, str] = parsed_data
        self.response_obj: str = ''

    def is_bad_request(self):
        return self.parsed_data['request_type'] not in RequestType.get_items()

    @logged_method
    def create_invalid_request_response(self):
        response = {
            "status": "fail - invalid request. please double check request syntax"
        }
        self.response_obj = json.dumps(response)

    @logged_method
    def create_match_communication_response(self, was_successful) -> None:
        """Create a response for a match communication request"""
        response = {
            "request_type": RequestType.MATCH_COMMUNICATION,
            RESULT: Status.was_success(was_successful)

        }
        self.response_obj = json.dumps(response)

    @logged_method
    def create_match_result_report_response(self, was_successful) -> None:
        """Create a response for a match result report request"""
        response = {
            "request_type": RequestType.MATCH_RESULT_REPORT,
            RESULT: Status.was_success(was_successful)
        }
        self.response_obj = json.dumps(response)

    @logged_method
    def create_error_report_response(self, was_successful: bool) -> None:
        """Create a response for an error result report request"""
        response = {
            "request_type": RequestType.ERROR_REPORT,
            RESULT: Status.was_success(was_successful)
        }
        self.response_obj = json.dumps(response)

    @logged_method
    def create_game_resp_not_accepted(self, player_one_username: str, game_token: str) -> None:
        """Creates a response for a request to create a game, but an opponent hasn't accepted yet"""  # FIXME if needed
        was_successful = bool(player_one_username) and bool(game_token)
        response = {
            "request_type": "create_game",
            "player_one_username": player_one_username,
            "game_token": game_token,
            RESULT: Status.was_success(was_successful)
        }
        self.response_obj = json.dumps(response)

    @logged_method
    def accept_game(self, player_one_username: str, player_two_username: str, game_token: str) -> None:
        """Creates a response for when a game is accepted by the second player"""
        was_successful = bool(player_one_username) and bool(player_two_username) and bool(game_token)
        response = {
            "request_type": "create_game",
            "player_one_username": player_one_username,
            "player_two": player_two_username,
            "game_token": game_token,
            RESULT: Status.was_success(was_successful)
        }
        self.response_obj = json.dumps(response)

    @logged_method
    def check_for_game_response(self, player_one_username: str, game_token: str) -> None:  # TODO add docString

        response = {
            "request_type": "create_game",
            "username": player_one_username,
            "game_token": game_token,
            RESULT: Status.was_success(was_successful)
        }
        self.response_obj = json.dumps(response)

    @logged_method
    def create_random_game_resp(self, game: Game) -> None:  # TODO add docString

        was_successful = bool(game)
        response = {
            "request_type": "request_game",
            "status": Status.SUCCESS,
            "game_token": game.game_token,
            "player_one_username": game.player_one.username,
            "player_two_username": game.player_two.username,
            "player_one_color": game.player_one.color,
            "player_two_color": game.player_two.color,
            "player_one_ip": game.player_one.ip,
            "player_one_port": game.player_one.port,
            "player_two_ip": game.player_two.ip,
            RESULT: Status.was_success(was_successful)
        }
        self.response_obj = json.dumps(response)

    @logged_method
    def create_random_game_resp_failure(self, username: str, was_successful: bool,
                                        reason: str) -> None:  # TODO add docString

        response = {
            "request_type": "request_game",
            "player_one_username": username,
            RESULT: Status.was_success(was_successful),
            "reason": reason
        }

        self.response_obj = json.dumps(response)

    @logged_method
    def cancel_random_game_resp(self, username: str,
                                was_successful: bool) -> None:  # TODO add docString and type of status

        response = {
            "request_type": "request_game",
            "player_one_username": username,
            RESULT: Status.was_success(was_successful)
        }

        self.response_obj = json.dumps(response)

    # FIXME I commented this out because we don't use it.
    #   If we are not going to use it, we should remove it.
    #   If we will use it, it needs to be fixed because there are Errors.
    #
    # def get_game_list_response(self, game_list: List[str], request: str = "get_game_list") -> None:
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
    #         game_Dict[game_str] = user
    #         i = i + 1
    #     response = {
    #         "request_type": "get_game_list",
    #         "count": "",
    #         "games": ""
    #     }
    #     response["request_type"] = request
    #     response["count"] = len(friendsList)
    #     response["friends"] = str(friendDict)
    #     self.response_obj = json.dumps(response)
