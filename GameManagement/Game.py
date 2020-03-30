import json

class Game:

    def __init__(self, gameToken, parsedData, pOneIp, pOnePort, socket):
        self.gameToken = gameToken
        self.player_one = parsedData["username"]
        self.player_one_signon_token = parsedData["signon_token"]
        self.player_two = ''
        self.player_two_signon_token = ''
        self.player_one_color = ''
        self.player_two_color = ''
        self.player_one_ip = pOneIp
        self.player_two_ip = ''
        self.player_one_port = pOnePort
        self.player_two_port = ''
        self.playerOneSocket = socket
        self.playerTwoSocket = ''
        self.responseObj = ''


    def addPlayerTwo(self, username, signonToken, pTwoIp, pOnePort, socket):
        self.player_two = username
        self.player_two_signon_token = signonToken
        self.player_two_ip = pTwoIp
        self.player_two_port = pOnePort
        self.player_one_color = 'black'
        self.player_two_color = 'white'
        self.playerTwoSocket = socket

    def makeMove(self, requester, jsonObj):
        print("Making move for players")
        if(requester == self.player_one):
            self.playerTwoSocket.send(jsonObj.encode())
            print("Sent to player Two: " + jsonObj)
        elif(requester == self.player_two):
            self.playerOneSocket.send(jsonObj.encode())
            print("Sent to player One: " + jsonObj)

    def createRandomGameResp(self):
        response = {
                    "requestType":"RequestGame",
                    "game_token":"",
                    "player_one":"",
                    "player_two":"",
                    "player_one_color":"",
                    "player_two_color":"",
                    "player_one_ip":"",
                    "player_one_port":"",
                    "player_two_ip":""
        }
        response["game_token"] = self.gameToken
        response["player_one"] = self.player_one
        response["player_two"] = self.player_two
        response["player_one_color"] = self.player_one_color
        response["player_two_color"] = self.player_two_color
        response["player_one_ip"] = self.player_one_ip
        response["player_one_port"] = self.player_one_port
        response["player_two_ip"] = self.player_two_ip
        self.responseObj = json.dumps(response)

    def sendGameResposne(self):
        self.createRandomGameResp()
        self.playerOneSocket.send(self.responseObj.encode())
        self.playerTwoSocket.send(self.responseObj.encode())
