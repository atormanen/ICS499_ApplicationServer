#Signin will handle the mechanics of signing a user in
import random
import string
import time

class Tokens:

    def __init__(self):
        self.t = ""

    def generateToken(self):
        token = ''.join(random.SystemRandom().choice(string.ascii_uppercase +\
                        string.digits) for _ in range(30))
        return token

    def getTokenCreationTime(self):
        now = time.strftime('%Y-%m-%d %H-%M-%S')
        return now

    def getToken(self):
        return self.generateToken()
