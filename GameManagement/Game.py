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


    def addPlayerTwo(self, username, signonToken, pTwoIp, pOnePort, socket):
        self.player_two = username
        self.player_two_signon_token = signonToken
        self.player_two_ip = pTwoIp
        self.player_two_port = pOnePort
        self.player_one_color = 'black'
        self.player_two_color = 'white'
        self.playerTwoSocket = socket

    def makeMove(self, requester, jsonObj):
        if(requester == player_one):
            playerTwoSocket.send(jsonObj.encode())
        elif(requester == player_two):
            playerOneSocket.send(jsonObj.encode())
