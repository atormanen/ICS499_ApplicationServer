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


    def signinResponse(self,token):
        response = {
                    "requestType":"signin",
                    "status":"succes",
                    "token":""
        }
        response["token"] = token
        self.responseObj = json.dumps(response)

    def createAccountResponse(self,status,reason='null'):
        response = {
                    "requestType":"createAccount",
                    "status":"",
                    "reason":""
        }
        response["status"] = status
        response["reason"] = reason
        self.responseObj = json.dumps(response)

    def getUSerStatsResponse(self, stats):
        response = {
                    "requestType":"getUserStats",
                    "userId":"",
                    "gamesPlayed":"",
                    "gamesWon":"",
                    "gamesResigned":"",
                    "score":"",
                    "longest_win_streak":""
        }
        response["userId"] = stats[0]
        response["gamesPlayed"] = stats[1]
        response["gamesWon"] = stats[2]
        response["gamesResigned"] = stats[3]
        response["score"] = stats[4]
        response["longest_win_streak"] = stats[5]
        self.responseObj = json.dumps(response)

    def getFriendsListResponse(self, friendsList):
        response = {
                    "requestType":"getFriendsList",
                    "list":""
        }
        response["list"] = friendsList
        self.responseObj = json.dumps(response)


    def acceptFriendReqResponse(self,status):
        response = {
                    "requestType":"validateFriendRequest",
                    "status":""
        }
        response["status"] = status
        self.responseObj = json.dumps(response)

    def sendFriendReqResponse(self,status,reason='null'):
        response = {
                    "requestType":"sendFriendRequest",
                    "status":"",
                    "reason":""
        }
        response["status"] = status
        response["reason"] = reason
        self.responseObj = json.dumps(response)
