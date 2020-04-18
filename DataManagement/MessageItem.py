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

    def createRandomGameResp(self, game):
        response = {
                    "requestType":"RequestGame",
                    "status":"success",
                    "game_token":"",
                    "player_one":"",
                    "player_two":"",
                    "player_one_color":"",
                    "player_two_color":"",
                    "player_one_ip":"",
                    "player_one_port":"",
                    "player_two_ip":""
        }
        response["game_token"] = game.gameToken
        response["player_one"] = game.player_one
        response["player_two"] = game.player_two
        response["player_one_color"] = game.player_one_color
        response["player_two_color"] = game.player_two_color
        response["player_one_ip"] = game.player_one_ip
        response["player_one_port"] = game.player_one_port
        response["player_two_ip"] = game.player_two_ip
        self.responseObj = json.dumps(response)

        def createRandomGameRespFailure(self, username, status, reason):
            response = {
                        "requestType":"RequestGame",
                        "player_one":"",
                        "status":"",
                        "reason":""
            }
            response["game_token"] = game.gameToken
            response["player_one"] = game.player_one
            response["status"] = status
            response["reason"] = reason

            self.responseObj = json.dumps(response)
