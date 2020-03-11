import json
#Message item is a wrapper class to hold the data of each reqeust.
#It holds the json object that was sent to the server as well as
#the socket

## TODO: Create subclasses for each message type.
#Too much happening here

class MessageItem:
    def __init__(self,connectionSocket, addr, parsedData):
        self.connectionSocket = connectionSocket
        self.ipAddress = addr[0]
        self.port = addr[1]
        self.parsedData = parsedData
        self.responseObj = ''

    def createGameRespNotAccepted(self, playerOne, gameToken):
        response = {
                    "requestType":"CreateGame",
                    "player_one":"",
                    "game_token":""
        }
        response["player_one"] = playerOne
        response["game_token"] = gameToken
        self.responseObj = json.dumps(response)

    def acceptGame(self, playerOne, playerTwo, gameToken):
        response = {
                    "requestType":"CreateGame",
                    "player_one":"",
                    "player_two":"",
                    "game_token":""
        }
        response["player_one"] = playerOne
        response["player_two"] = playerTwo
        response["game_token"] = gameToken
        self.responseObj = json.dumps(response)

    def checkForGameResponse(self, playerOne, gameToken):
        response = {
                    "requestType":"CreateGame",
                    "username":"",
                    "game_token":""
        }
        response["username"] = playerOne
        response["game_token"] = gameToken
        self.responseObj = json.dumps(response)
