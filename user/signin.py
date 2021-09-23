# Signin will handle the mechanics of signing a user in
import time

from user.Tokens import Tokens


class Signin:

    def __init__(self, db):
        self.db = db
        self.token = Tokens()

    def validatePassword(self, username, password):
        if (self.db.validate_user_exists(username)):
            dbPassword = self.db.getPasswordFor(username)
            dbPassword = dbPassword[0][0]
            # compare password to given getPassword
            if (password == dbPassword):
                return True
        return False

    def tokenUpToDate(self, username):
        tokenExpiration = self.db.get_token_creation_time(username)
        currentTime = time.time()
        timeDiference = currentTime - tokenExpiration[0][0]
        if (timeDiference > 86400):
            return False
        return True

    def signin(self, parsedData):
        username = parsedData["username"]
        password = parsedData["password"]
        if (self.validatePassword(username, password)):
            if (self.tokenUpToDate(username)):
                # Bundle the tocken into the response package
                signonToken = self.db.getToken(username)
                signonToken = signonToken[0][0]
                return signonToken
            else:
                signonToken = self.token.getToken()
                self.db.signin(username, signonToken, self.token.get_token_creation_time())
                return signonToken
        return False
