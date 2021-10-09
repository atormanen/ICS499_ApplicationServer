# This class holds all the mysql syntax for the sql class
## TODO: change MysqlDB to db and change query builder to mysqlquery
class MysqlDB:

    log_function_name = lambda x: logger.debug(f"func {inspect.stack()[1][3]}")

    def __init__(self):
        self.tableName = 'test'

    def create_game(self, game_id, game_token, player_one_id, player_two_id):
        self.log_function_name()
        statement = "INSERT INTO game VALUES(" + str(game_id) + ",'" + game_token + "'," \
                    + str(player_one_id) + "," + str(player_two_id) + "," + "0,0);"
        return statement

    def get_open_random_game(self):
        self.log_function_name()
        statement = " select * from game inner join player on game.game_id \
                = player.game_id where game.game_complete = 0 limit 1;"
        return statement

    def create_player(self, game_id, player_id, username, piece_color, ip4, ip6,
                      port, signon_token):
        self.log_function_name()
        statement = "INSERT INTO player VALUES(" + str(game_id) + "," + str(player_id) \
                    + ",'" + username + "','" + piece_color + "','" + ip4 + "','" + ip6 + "'," \
                    + str(port) + ",'" + signon_token + "');"
        return statement

    def get_game(self, game_id):
        self.log_function_name()
        statement = "select * from game inner join player on game.game_id =\
            player.game_id where game.game_id =" + str(game_id) + ";"
        return statement

    def get_last_game_id(self):
        self.log_function_name()
        return "SELECT MAX(game_id) FROM game;"

    def get_user_id(self, username):
        self.log_function_name()
        query = "SELECT user_id FROM user WHERE username = '" + username + "';"
        return query

    def get_token_creation_time(self, username):
        self.log_function_name()
        query = "SELECT unix_timestamp(token_creation) FROM user WHERE username='" + username + "';"
        return query

    def user_exists(self, username):
        self.log_function_name()
        query = "SELECT EXISTS(SELECT username FROM user WHERE username = '" + \
                 username + "');"
        return query

    def validate_game_exists(self, game_token):
        self.log_function_name()
        query = "SELECT EXISTS(SELECT game_token FROM game WHERE game_token = '" + \
                 game_token + "');"
        return query

    def get_signon_token(self, username):
        self.log_function_name()
        query = "SELECT signon_token FROM user WHERE username='" + username + "';"
        return query

    def accept_game(self, game_token):
        self.log_function_name()
        query = "UPDATE game SET game_accepted = 1 WHERE game_token = '" + \
                 game_token + "';"
        return query

    def check_for_game(self, username_id):
        self.log_function_name()
        query = "SELECT game_token FROM game WHERE player_two = " + \
                 str(username_id) + " AND game_accepted = 0;"
        return query

    def update_socket(self, user_id, ip, port):
        self.log_function_name()
        query = "UPDATE player SET ip4 ='" + ip + "', port =" + str(port) + " WHERE" + \
                 " player_id = " + str(user_id) + ";"
        return query

    def get_socket(self, user_id):
        self.log_function_name()
        query = "SELECT ip4, port FROM player WHERE player_id = " + str(user_id) + ";"
        return query;

    def get_game_id(self, token):
        self.log_function_name()
        query = "SELECT game_id FROM game WHERE game_token = '" + token + "';"
        return query

    def get_avatar(self, username):
        self.log_function_name()
        query = "SELECT avatar FROM user WHERE username = '" + username + "';"
        return query

    def add_game_played(self, user_id):
        self.log_function_name()
        query = "UPDATE user_statistics SET games_played = games_played + 1\
        WHERE user_id = " + str(user_id) + ";"
        return query

    def add_game_won(self, user_id):
        self.log_function_name()
        query = "UPDATE user_statistics set games_won = games_won + 1, games_played = games_played + 1" + \
                 " WHERE user_id = " + str(user_id) + ";"
        return query

    def add_game_lost(self, user_id):
        self.log_function_name()
        query = "UPDATE user_statistics set games_played = games_played + 1" + \
                 " WHERE user_id = " + str(user_id) + ";"
        return query

    def add_game_resigned(self, user_id):
        self.log_function_name()
        query = "UPDATE user_statistics set games_resigned = games_resigned + 1, games_played = games_played + 1" + \
                 " WHERE user_id = " + str(user_id) + ";"
        return query
