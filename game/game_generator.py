from game.game import Game
from game.tokens import Tokens
from global_logger import *


class GameGenerator:
    static_counter = 0

    def __init__(self, mysql_db, game_queue, game_collection):

        self.counter = GameGenerator.static_counter
        GameGenerator.static_counter = GameGenerator.static_counter + 1

        self.db = mysql_db
        self.token = Tokens()
        self.game_queue = game_queue
        self.game_collection = game_collection

    @logged_method
    def validate_username(self, username):

        user_exits = self.db.user_exists(username)
        if (user_exits[0][0] == 1):
            # print("user exists")
            return True
        return False

    @logged_method
    def token_up_to_date(self, username):

        token_expiration = self.db.get_token_creation_time(username)
        current_time = time.time()
        time_diference = current_time - token_expiration[0][0]
        if (time_diference > 86400 * 5):
            return False
        return True

    @logged_method
    def validate_token(self, username, signon_token):

        saved_token = self.db.get_signon_token(username)
        if saved_token == signon_token:
            return True
        return False

    @logged_method
    def create_game(self, parsed_data, req_item):

        player_one_username = parsed_data["player_one_username"]
        player_two_username = parsed_data["player_two_username"]
        player_one_signon_token = parsed_data["signon_token"]

        if not self.validate_username(player_one_username):
            return False
        if not self.validate_username(player_two_username):
            return False
        if not self.validate_token(player_one_username, player_one_signon_token):
            return False
        if not self.token_up_to_date(player_one_username):
            return False

        p_one_ip = req_item.ip_address
        p_one_port = req_item.port
        game_token = self.token.get_token()
        self.db.create_game(game_token, player_one_username, player_one_signon_token, player_two_username,
                            p_one_ip, p_one_port)
        req_item.create_game_resp_not_accepted(player_one_username, game_token)

        p_one_ip = req_item.ip_address
        p_one_port = req_item.port

        # Check for open games in game GameCollection
        # If no open games, create a game and wait for a player to join
        self.game_collection.lock.acquire()

        if (self.game_collection.check_if_already_in_game(player_one_username)):
            self.game_collection.lock.release()
            req_item.create_random_game_resp_failure(username=player_one_username, was_successful=False,
                                                     reason="User already in game")
            return False

        #  FIXME game variable is never used after this assignment.
        game = Game(game_token, parsed_data, p_one_ip, p_one_port,
                    req_item.connection_socket, self.game_collection.listener, self.db)
        self.game_collection.lock.release()

    @logged_method
    def wait_for_player(self, game_token):

        while not self.game_collection.get_game(game_token):
            time.sleep(2)

    @logged_method
    def wait_for_game(self):

        game = self.db.search_for_game()
        return game

    @logged_method
    def request_game_canceled(self, parsed_data, req_item):

        try:
            username = parsed_data["username"]
            signon_token = parsed_data["signon_token"]  # FIXME by removing assignment if we are not using signon_token
        except KeyError as e:
            log_error(e)
            return False
        if self.game_collection.check_if_already_in_game(username):
            game = self.game_collection.get_game(username)
            self.game_collection.remove_game(game)
            log('game removed', level=VERBOSE)
            req_item.cancel_random_game_resp(username, was_successful=True)
        else:
            req_item.cancel_random_game_resp(username, was_successful=False)

    @logged_method
    def create_random_game(self, parsed_data, req_item):

        try:
            player_one_username = parsed_data["username"]
            player_one_signon_token = parsed_data["signon_token"]
        except KeyError as e:
            log_error(e)
            return False
        # gaem_token = parsed_data["game_token"]
        if not self.validate_username(player_one_username):
            req_item.create_random_game_resp_failure(player_one_username, "failure", "failed validation")
            return False
        if not self.validate_token(player_one_username, player_one_signon_token):
            req_item.create_random_game_resp_failure(player_one_username, "failure", "failed validation")
            return False
        if not self.token_up_to_date(player_one_username):
            req_item.create_random_game_resp_failure(player_one_username, "failure", "expired token")
            return False

        p_one_ip = req_item.ip_address
        p_one_port = req_item.port

        # Check for open games in game GameCollection
        # If no open games, create a game and wait for a player to join

        self.game_collection.lock.acquire()

        if (self.game_collection.check_if_already_in_game(player_one_username)):
            self.game_collection.lock.release()
            req_item.create_random_game_resp_failure(player_one_username, "failure", "User already in game")
            return False

        if (self.game_collection.open_game_available()):
            game = self.game_collection.add_second_player(player_one_username, player_one_signon_token,
                                                          p_one_ip, p_one_port, req_item.connection_socket)
            self.game_collection.lock.release()
            game.send_game_response()
        else:
            game_token = self.token.get_token()
            game = Game(game_token, parsed_data, p_one_ip, p_one_port,
                        req_item.connection_socket, self.game_collection.listener, self.db)
            self.game_collection.add_open_game(game)
            # self.db.create_random_game(game)
            self.game_collection.lock.release()

    @logged_method
    def create_random_game_test(self, parsed_data, req_item):

        player_one = parsed_data["username"]
        player_one_signon_token = parsed_data["signon_token"]
        p_one_ip = req_item.ip_address
        p_one_port = req_item.port

        listener = None  # FIXME  I added this because Game.__init__ requires a listener...
        db = self.db  # TODO check this. I added it because Game.__init__ requires a db

        game_token = self.token.get_token()
        game = Game(game_token, parsed_data, p_one_ip, p_one_port, req_item.connection_socket, listener, db)
        self.game_collection.add_open_game(game)
        self.game_collection.get_game(game_token)

    @logged_method
    def accept_game(self, parsed_data, req_item):

        player_one = parsed_data["player_one_username"]
        player_two = parsed_data["player_two"]
        player_two_signon_token = parsed_data["signon_token"]
        game_token = parsed_data["game_token"]

        if (self.validate_username(player_one) == False):
            return False
        if (self.validate_username(player_two) == False):
            return False
        if (self.validate_token(player_two, player_two_signon_token) == False):
            return False
        if (self.token_up_to_date(player_one) == False):
            return False

        p_one_ip = req_item.ip_address
        p_one_port = req_item.port

        self.db.accept_game(game_token)
        self.db.update_socket(player_two, req_item.ip_address, req_item.port)
        game_id = self.db.get_game_id(game_token)
        self.db.create_player(game_id, player_two, req_item.ip_address, req_item.port,
                              game_token)
        game = self.game_collection.add_second_player(player_two, player_two_signon_token,
                                                      p_one_ip, p_one_port, req_item.connection_socket)

    # game.send_game_resposne()

    @logged_method
    def check_for_game(self, parsed_data, req_item):

        username = parsed_data["username"]
        player_one_signon_token = parsed_data["signon_token"]
        if (self.validate_username(username) == False):
            return False
        if (self.validate_token(username, player_one_signon_token) == False):
            return False
        if (self.token_up_to_date(username) == False):
            return False

        token = self.db.check_for_game(username)
        req_item.check_for_game_response(username, token)
