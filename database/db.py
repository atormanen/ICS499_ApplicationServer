from typing import Union

import mysql.connector
from mysql.connector import CMySQLConnection, MySQLConnection
from mysql.connector import Error as MySQLError

from database.mysql_db import MysqlDB
from manifest import Manifest


# from queryBuilder import queryBuilder

# MysqlDB is a class used to implement common database queries programaticly. It
# uses the querryBuilder class which holds the actual mysql syntax.
class DB:

    def __init__(self, user, password, reader, writer, database):
        self.manifest = Manifest()
        self.builder = MysqlDB()
        self.user = user
        self.password = password
        self.reader = reader
        self.writer = writer
        self.database = database

    def db_insert(self, statement):
        mydb = None
        cursor = None
        result = False
        try:
            mydb = mysql.connector.connect(user=self.user,
                                           password=self.password,
                                           host=self.writer,
                                           database=self.database,
                                           auth_plugin='mysql_native_password')
            cursor = mydb.cursor()
            cursor.execute(statement)
            mydb.commit()
            result = True
            print(result)
        except MySQLError as error:
            ## TODO: Log to error log
            print("Insert errror")
        finally:
            if mydb is not None and mydb.is_connected():
                if cursor is not None:
                    cursor.close()
                mydb.close()
            return result

    def user_db_fetch(self, statement):
        try:
            result = ''
            mydb = mysql.connector.connect(user=self.user,
                                           password=self.password,
                                           host=self.reader,
                                           database=self.manifest.user_database_name,
                                           auth_plugin='mysql_native_password')
            cursor = mydb.cursor()
            cursor.execute(statement)
            result = cursor.fetchall()
        except MySQLError as e:  # FIXME this needs to refined
            ## TODO: Log error to log
            # print("Error fetching data from db")
            result = False
        finally:
            if (mydb.is_connected()):
                cursor.close()
                mydb.close()
            return result

    def user_db_update(self, statement) -> bool:
        try:
            mydb: Union[CMySQLConnection, MySQLConnection] = mysql.connector.connect(user=self.user,
                                                                                     password=self.password,
                                                                                     host=self.writer,
                                                                                     database='userdb',
                                                                                     auth_plugin='mysql_native_password')
            cursor = mydb.cursor()
            cursor.execute(statement)
            mydb.commit()
            result = True
        except MySQLError as error:
            ## TODO: Log error to Log
            # print("Error updating data to db")
            result = False
        finally:
            if (mydb.is_connected()):
                cursor.close()
                mydb.close()
            return result

    def db_fetch(self, statement):
        try:
            result = ''
            mydb = mysql.connector.connect(user=self.user,
                                           password=self.password,
                                           host=self.reader,
                                           database=self.database,
                                           auth_plugin='mysql_native_password')
            cursor = mydb.cursor()
            cursor.execute(statement)
            result = cursor.fetchall()
        except MySQLError as e:
            ## TODO: Log error to log
            # print("Error fetching data from db")
            result = False
        finally:
            if (mydb.is_connected()):
                cursor.close()
                mydb.close()
            return result

    def db_update(self, statement):
        try:
            mydb = mysql.connector.connect(user=self.user, password=self.password,
                                           host=self.writer,
                                           database=self.database,
                                           auth_plugin='mysql_native_password')
            cursor = mydb.cursor()
            cursor.execute(statement)
            mydb.commit()
            result = True
        except MySQLError as error:
            ## TODO: Log error to Log
            # print("Error updating data to db")
            result = False
        finally:
            if (mydb.is_connected()):
                cursor.close()
                mydb.close()
            return result

    def create_game(self, game_token, player_one_username, player_one_signon_token, \
                    player_two_username, p_one_ip4, p_one_port):
        p_one_id = self.user_db_fetch(self.builder.getUserId(player_one_username))
        p_one_id = p_one_id[0][0]
        p_two_id = self.user_db_fetch(self.builder.getUserId(player_two_username))
        p_two_id = p_two_id[0][0]
        token_creation = self.get_token_creation_time(player_one_username)
        nextId = self.db_fetch(self.builder.getLastGameId())
        print("nextId: " + str(nextId[0][0]))
        if nextId[0][0] is None:
            nextId = 1
        else:
            nextId = nextId[0][0] + 1;

        self.db_insert(self.builder.createGame(nextId, game_token, p_one_id, p_two_id))
        self.db_insert(self.builder.createPlayer(nextId, p_one_id, player_one_username, "White", p_one_ip4, "", \
                                                 p_one_port, player_one_signon_token))

    # FIXME there is an error needing a fix
    def create_random_game(self, game):
        p_one_id = self.user_db_fetch(self.builder.getUserId(game.player_one))
        p_one_id = p_one_id[0][0]
        next_id = self.db_fetch(self.builder.getLastGameId())
        next_id = next_id[0][0] + 1;
        self.db_insert(self.builder.createGame(next_id, game.game_token, p_one_id, p_two_id))  # FIXME

        self.db_insert(self.builder.createPlayer(next_id, p_one_id, game.player_one,
                                                 game.player_one_color, game.player_one_ip, "",
                                                 game.player_one_port, game.player_one_signon_token))

    def complete_random_game(self, game):
        pTwoId = self.user_db_fetch(self.builder.getUserId(game.player_two))
        pTwoId = pTwoId[0][0]
        self.db_insert(self.builder.createPlayer(nextId, pTwoId, game.player_two,
                                                 game.player_two_color, game.player_two_ip, "",
                                                 game.player_two_port, game.player_two_signon_token))

    def search_for_game(self):
        result = self.db_fetch(self.builder.getOpenRandomGame())
        return result

    # Return 0 if false, 1 if true
    def validate_user_exists(self, username):
        result = self.user_db_fetch(self.builder.validateUserExists(username))
        # result = result[0][0]
        return result

    # Return 0 if false, 1 if true
    def validate_game_exists(self, game_token):
        result = self.db_fetch(self.builder.validateGameExists(game_token))
        result = result[0][0]
        print(result)
        return result

    def get_token_creation_time(self, username):
        result = self.user_db_fetch(self.builder.getTokenCreationTime(username))
        return result

    def get_signon_token(self, username):
        result = self.user_db_fetch(self.builder.getSignonToken(username))
        result = result[0][0]
        return result

    def accept_game(self, game_token):
        self.db_update(self.builder.acceptGame(game_token))

    def check_for_game(self, username):
        userId = self.user_db_fetch(self.builder.getUserId(username))
        userId = userId[0][0]
        gameToken = self.db_fetch(self.builder.checkForGame(userId))
        gameToken = gameToken[0][0]
        # print(game_token)
        return gameToken

    def update_socket(self, username, ip, port):
        userId = self.user_db_fetch(self.builder.getUserId(username))
        userId = userId[0][0]
        self.db_update(self.builder.updateSocket(userId, ip, port))

    def get_last_game_id(self):
        id = self.db_fetch(self.builder.getLastGameId())
        id = id[0][0]
        return id

    def get_socket(self, username):
        userId = self.user_db_fetch(self.builder.getUserId(username))
        userId = userId[0][0]
        socket = self.db_fetch(self.builder.getSocket(userId))
        socket = socket[0]
        # print(socket)
        return socket

    def get_game_id(self, token):
        gameId = self.db_fetch(self.builder.getGameId(token))
        gameId = gameId[0][0]
        return gameId

    def create_player(self, game_id, username, ip4, port, signon_token):
        userId = self.user_db_fetch(self.builder.getUserId(username))
        userId = userId[0][0]
        self.db_insert(self.builder.createPlayer(game_id, userId, ip4, "",
                                                 port, signon_token))

    def get_game(self, game_token):
        gameId = self.get_game_id(game_token)
        game = self.db_fetch(self.builder.getGame(gameId))
        return game

    def get_avatar(self, username):
        avatarInt = self.user_db_fetch(self.builder.getAvatar(username))
        avatarInt = avatarInt[0][0]
        return avatarInt

    def add_game_won(self, username):
        userId = self.user_db_fetch(self.builder.getUserId(username))
        userId = userId[0][0]
        self.user_db_update(self.builder.addGameWon(userId))

    def add_game_lost(self, username):
        userId = self.user_db_fetch(self.builder.getUserId(username))
        userId = userId[0][0]
        self.user_db_update(self.builder.addGameLost(userId))

    def add_game_resigned(self, username):
        userId = self.user_db_fetch(self.builder.getUserId(username))
        userId = userId[0][0]
        self.user_db_update(self.builder.addGameResigned(userId))

    def add_game_played(self, username):
        userId = self.user_db_fetch(self.builder.getUserId(username))
        userId = userId[0][0]
        self.user_db_update(self.builder.addGamePlayed(userId))
