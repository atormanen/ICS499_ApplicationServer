class MakeMove:

    def __init__(self, mysqlDB):
        self.db = mysqlDB

    def validateGame(self, username):
        #validtate game exists and is playable
        return False

    def validateUsername(self, username):
        if(self.db.validateUserExists(username)):
            return True
        return False

    def updateMove(self, parsedData):
        #get move string

        #add move to move string

        #update move string with new move string

        #update lastMove timestamp

		return False

    def getMove(self, parsedData, reqItem):
        #get move string

        #get lastMove timestamp

        rerurn False
