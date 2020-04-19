import json
from threading import Thread

class Game:

    def __init__(self, gameToken, parsedData, pOneIp, pOnePort, socket, listener, db):
        self.db = db
        self.listener = listener
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
        self.playerOneSocket = ''
        self.playerTwoSocket = ''
        self.playerOneSocketInitial = socket
        self.playerTwoSocketInitial = ''
        self.playerOneSocketInitialFlag = 0
        self.playerTwoSocketInitialFlag = 0
        self.responseObj = ''
        self.lastMove = False

    def listen(self, socket):
        while(True):
            #msg = socket.recv(1024) test
            self.listener.processRequest(socket,(self.player_one_ip,self.player_two_port))

    def checkIfStillAlive(self, username):
        if(username == self.player_one):
            try:
                self.playerOneSocket.send("socket test")
            except:
                return False
        elif(username == self.player_two):
            try:
                self.playerTwoSocket.send("socket test")
            except:
                return False
        return True

    def addPlayerTwo(self, username, signonToken, pTwoIp, pTwoPort, socket):
        self.player_two = username
        self.player_two_signon_token = signonToken
        self.player_two_ip = pTwoIp
        self.player_two_port = pTwoPort
        self.player_one_color = 'black'
        self.player_two_color = 'white'
        self.playerTwoSocketInitial = socket

    def addPlayerOneSocket(self, socket):
        print("player one socket: " + str(socket))
        self.playerOneSocket = socket;
        self.playerOneSocket.setblocking(0)
        self.playerOneSocketInitialFlag = 1
        ## TODO: find a different way to handle multpiple sockets
        thread = Thread(target=self.listen,args=(self.playerOneSocket,))
        thread.start()

    def addPlayerTwoSocket(self, socket):
        print("player two socket: " + str(socket))
        self.playerTwoSocket = socket;
        self.playerTwoSocket.setblocking(0)
        self.playerTwoSocketInitialFlag = 1
        ## TODO: find a different way to handle multpiple sockets
        thread = Thread(target=self.listen,args=(self.playerTwoSocket,))
        thread.start()


    def makeMove(self, requester, jsonObj, socket):
        if(requester == self.player_one):
            self.playerTwoSocket.send(str(jsonObj).encode("utf-8"))
            if(self.lastMove):
                self.playerTwoSocket.close()
                print("closed player one socket")
        elif(requester == self.player_two):
            self.playerOneSocket.send(str(jsonObj).encode("utf-8"))
            if(self.lastMove):
                self.playerOneSocket.close()
                print("closed player one socket")


    def createRandomGameResp(self):
        response = {
                    "requestType":"RequestGame",
                    "status": "success",
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
        response["player_two_port"] = self.player_two_port
        self.responseObj = json.dumps(response)

    def sendGameResposne(self):
        self.createRandomGameResp()
        self.playerOneSocketInitial.send(self.responseObj.encode("utf-8"))
        self.playerTwoSocketInitial.send(self.responseObj.encode("utf-8"))
        print(self.player_one + "    " + str(self.playerOneSocket))
        print(self.player_two + "    " + str(self.playerTwoSocket))
        self.playerOneSocketInitial.close()
        self.playerTwoSocketInitial.close()
