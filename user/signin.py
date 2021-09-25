# Signin will handle the mechanics of signing a user in
import time

from user.tokens import Tokens  # FIXME

from database.db import DB
from database.mysql_db import MysqlDB


class Signin:

    def __init__(self, db):
        self.db: MysqlDB = db
        self.token = Tokens()

    def validate_password(self, username, password):
        if self.db.user_exists(username):
            db_password = self.db.get_password_for(username)  # FIXME
            db_password = db_password[0][0]
            # compare password to given getPassword
            if password == db_password:
                return True
        return False

    def token_up_to_date(self, username):
        token_expiration = self.db.get_token_creation_time(username)
        current_time = time.time()
        time_diference = current_time - token_expiration[0][0]
        if time_diference > 86400:
            return False
        return True

    def signin(self, parsed_data):
        username = parsed_data["username"]
        password = parsed_data["password"]
        if self.validate_password(username, password):
            if self.token_up_to_date(username):
                # Bundle the token into the response package
                signon_token = self.db.get_token(username)  # FIXME
                signon_token = signon_token[0][0]
                return signon_token
            else:
                signon_token = self.token.get_token()
                self.db.signin(username, signon_token, self.token.get_token_creation_time())  # FIXME
                return signon_token
        return False
