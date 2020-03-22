class Game:

    def __init__(self, gameToken, parsedData, pOneIp, pOnePort):
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


    def addPlayerTwo(self, username, signonToken, pTwoIp):
        self.player_two = username
        self.player_two_signon_token = signonToken
        self.player_two_ip = pTwoIp
        self.player_one_color = 'black'
        self.player_two_color = 'white'

    def createAccount(self, parsedData):
		#check if username exists
        #return false if username alread exists
        result = self.db.validateUsernameAvailable(parsedData["username"])
        #call mysqlDB to create CreateAccount
        if result == 0:
            self.db.createUser(parsedData)
            return True
        else:
            return False
        #if account createion succussful return true otherwise False

    def getUserStats(self, parsedData, reqItem):
        stats = self.db.getUserStats(parsedData["username"])
        reqItem.getUSerStatsResponse(stats[0])
