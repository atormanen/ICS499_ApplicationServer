from typing import Union

import mysql.connector
from mysql.connector import CMySQLConnection, MySQLConnection
from mysql.connector import Error as MySQLError

from database.mysql_db import MysqlDB
from manifest import Manifest
from global_logger import *


# from queryBuilder import queryBuilder

# MysqlDB is a class used to implement common database queries programaticly. It
# uses the querryBuilder class which holds the actual mysql syntax.
class DB:

    def __init__(self, user, password, reader, writer, database):
        self.manifest = Manifest()
        self.builder: MysqlDB = MysqlDB()
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

    @logged_method
    def create_game(self, game_token, player_one_username, player_one_signon_token,
                    player_two_username, p_one_ip4, p_one_port):

        p_one_id = self.user_db_fetch(self.builder.get_user_id(player_one_username))
        p_one_id = p_one_id[0][0]
        p_two_id = self.user_db_fetch(self.builder.get_user_id(player_two_username))
        p_two_id = p_two_id[0][0]
        token_creation = self.get_token_creation_time(player_one_username)
        next_id = self.db_fetch(self.builder.get_last_game_id())
        if next_id[0][0] is None:
            next_id = 1
        else:
            next_id = next_id[0][0] + 1;

        self.db_insert(self.builder.create_game(next_id, game_token, p_one_id, p_two_id))
        self.db_insert(self.builder.create_player(next_id, p_one_id, player_one_username, "White", p_one_ip4, "",
                                                  p_one_port, player_one_signon_token))

    # FIXME there is an error needing a fix
    @logged_method
    def create_random_game(self, game):

        p_one_id = self.user_db_fetch(self.builder.get_user_id(game.player_one))
        p_one_id = p_one_id[0][0]
        next_id = self.db_fetch(self.builder.get_last_game_id())
        next_id = next_id[0][0] + 1;
        self.db_insert(self.builder.create_game(next_id, game.game_token, p_one_id, p_two_id))  # FIXME

        self.db_insert(self.builder.create_player(next_id, p_one_id, game.player_one,
                                                  game.player_one_color, game.player_one_ip, "",
                                                  game.player_one_port, game.player_one_signon_token))

    @logged_method
    def complete_random_game(self, game):

        p_two_id = self.user_db_fetch(self.builder.get_user_id(game.player_two))
        p_two_id = p_two_id[0][0]

        self.db_insert(self.builder.create_player(game.id, p_two_id, game.player_two,
                                                  game.player_two_color, game.player_two_ip, "",
                                                  game.player_two_port, game.player_two_signon_token))

    @logged_method
    def search_for_game(self):

        result = self.db_fetch(self.builder.get_open_random_game())
        return result

    # Return 0 if false, 1 if true
    @logged_method
    def validate_user_exists(self, username):

        result = self.user_db_fetch(self.builder.user_exists(username))
        # result = result[0][0]
        return result

    # Return 0 if false, 1 if true
    @logged_method
    def validate_game_exists(self, game_token):

        result = self.db_fetch(self.builder.validate_game_exists(game_token))
        result = result[0][0]
        return result

    @logged_method
    def get_token_creation_time(self, username):

        result = self.user_db_fetch(self.builder.get_token_creation_time(username))
        return result

    @logged_method
    def get_signon_token(self, username):

        result = self.user_db_fetch(self.builder.get_signon_token(username))
        result = result[0][0]
        return result

    @logged_method
    def accept_game(self, game_token):

        self.db_update(self.builder.accept_game(game_token))

    @logged_method
    def check_for_game(self, username):

        user_id = self.user_db_fetch(self.builder.get_user_id(username))
        user_id = user_id[0][0]
        game_token = self.db_fetch(self.builder.check_for_game(user_id))
        game_token = game_token[0][0]
        return game_token

    @logged_method
    def update_socket(self, username, ip, port):

        user_id = self.user_db_fetch(self.builder.get_user_id(username))
        user_id = user_id[0][0]
        self.db_update(self.builder.update_socket(user_id, ip, port))

    @logged_method
    def get_last_game_id(self):

        id = self.db_fetch(self.builder.get_last_game_id())
        id = id[0][0]
        return id

    @logged_method
    def get_socket(self, username):

        user_id = self.user_db_fetch(self.builder.get_user_id(username))
        user_id = user_id[0][0]
        socket = self.db_fetch(self.builder.get_socket(user_id))
        socket = socket[0]
        return socket

    @logged_method
    def get_game_id(self, token):

        game_id = self.db_fetch(self.builder.get_game_id(token))
        game_id = game_id[0][0]
        return game_id

    @logged_method
    def create_player(self, game_id, username, ip4, port, signon_token):

        user_id = self.user_db_fetch(self.builder.get_user_id(username))
        user_id = user_id[0][0]
        self.db_insert(self.builder.create_player(game_id, user_id, ip4, "",
                                                  port, signon_token))

    @logged_method
    def get_game(self, game_token):

        game_id = self.get_game_id(game_token)
        game = self.db_fetch(self.builder.get_game(game_id))
        return game

    @logged_method
    def get_avatar(self, username):

        avatar_int = self.user_db_fetch(self.builder.get_avatar(username))
        avatar_int = avatar_int[0][0]
        return avatar_int

    @logged_method
    def add_game_won(self, username):

        user_id = self.user_db_fetch(self.builder.get_user_id(username))
        user_id = user_id[0][0]
        self.user_db_update(self.builder.add_game_won(user_id))

    @logged_method
    def add_game_lost(self, username):

        user_id = self.user_db_fetch(self.builder.get_user_id(username))
        user_id = user_id[0][0]
        self.user_db_update(self.builder.add_game_lost(user_id))

    @logged_method
    def add_game_resigned(self, username):

        user_id = self.user_db_fetch(self.builder.get_user_id(username))
        user_id = user_id[0][0]
        self.user_db_update(self.builder.add_game_resigned(user_id))

    @logged_method
    def add_game_played(self, username):

        user_id = self.user_db_fetch(self.builder.get_user_id(username))
        user_id = user_id[0][0]
        self.user_db_update(self.builder.add_game_played(user_id))
