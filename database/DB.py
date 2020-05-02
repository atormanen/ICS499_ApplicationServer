import mysql.connector
from database.MysqlDB import MysqlDB
#from queryBuilder import queryBuilder

#MysqlDB is a class used to implement common database queries programaticly. It
#uses the querryBuilder class which holds the actual mysql syntax.
class DB:

    def __init__(self, user, password, reader, writer, database):
        self.builder = MysqlDB()
        self.user = user
        self.password = password
        self.reader = reader
        self.writer = writer
        self.database = database

    def dbInsert(self, statement):
        try:
            mydb = mysql.connector.connect(user=self.user, password=self.password,
                                  host=self.writer,
                                  database=self.database,
                                  auth_plugin='mysql_native_password')
            cursor = mydb.cursor()
            cursor.execute(statement)
            mydb.commit()
            result = True
            print(result)
        except mysql.connector.Error as error:
            ## TODO: Log to error log
            print("Insert errror")
            result = False
        finally:
            if(mydb.is_connected()):
                cursor.close()
                mydb.close()
            return result

    def userDBFetch(self, statement):
       try:
           result = ''
           mydb = mysql.connector.connect(user=self.user, password=self.password,
                                 host=self.reader,
                                 database='userdb',
                                 auth_plugin='mysql_native_password')
           cursor = mydb.cursor()
           cursor.execute(statement)
           result = cursor.fetchall()
       except Error as e:
           ## TODO: Log error to log
           #print("Error fetching data from db")
           result = False
       finally:
           if(mydb.is_connected()):
               cursor.close()
               mydb.close()
           return result

    def userDBUpdate(self, statement):
        try:
            mydb = mysql.connector.connect(user=self.user, password=self.password,
                                  host=self.writer,
                                  database='userdb',
                                  auth_plugin='mysql_native_password')
            cursor = mydb.cursor()
            cursor.execute(statement)
            mydb.commit()
            result = True
        except mysql.connector.Error as error:
            ## TODO: Log error to Log
            #print("Error updating data to db")
            result = False
        finally:
            if(mydb.is_connected()):
                cursor.close()
                mydb.close()
            return result

    def dbFetch(self, statement):
        try:
            result = ''
            mydb = mysql.connector.connect(user=self.user, password=self.password,
                                  host=self.reader,
                                  database=self.database,
                                  auth_plugin='mysql_native_password')
            cursor = mydb.cursor()
            cursor.execute(statement)
            result = cursor.fetchall()
        except Error as e:
            ## TODO: Log error to log
            #print("Error fetching data from db")
            result = False
        finally:
            if(mydb.is_connected()):
                cursor.close()
                mydb.close()
            return result

    def dbUpdate(self, statement):
        try:
            mydb = mysql.connector.connect(user=self.user, password=self.password,
                                  host=self.writer,
                                  database=self.database,
                                  auth_plugin='mysql_native_password')
            cursor = mydb.cursor()
            cursor.execute(statement)
            mydb.commit()
            result = True
        except mysql.connector.Error as error:
            ## TODO: Log error to Log
            #print("Error updating data to db")
            result = False
        finally:
            if(mydb.is_connected()):
                cursor.close()
                mydb.close()
            return result

    def createGame(self, gameToken, playerOne, playerOneSignonToken,\
                    playerTwo, pOneIp4, pOnePort):
        pOneId = self.userDBFetch(self.builder.getUserId(playerOne))
        pOneId = pOneId[0][0]
        pTwoId = self.userDBFetch(self.builder.getUserId(playerTwo))
        pTwoId = pTwoId[0][0]
        tokenCreation = self.getTokenCreationTime(playerOne)
        nextId = self.dbFetch(self.builder.getLastGameId())
        print("nextId: " + str(nextId[0][0]))
        if nextId[0][0] is None:
            nextId = 1
        else:
            nextId = nextId[0][0] + 1;

        self.dbInsert(self.builder.createGame(nextId, gameToken, pOneId, pTwoId))
        self.dbInsert(self.builder.createPlayer(nextId, pOneId, playerOne, "White", pOneIp4, "", \
                pOnePort, playerOneSignonToken))


    def createRandomGame(self, game):
        pOneId = self.userDBFetch(self.builder.getUserId(game.player_one))
        pOneId = pOneId[0][0]
        nextId = self.dbFetch(self.builder.getLastGameId())
        nextId = nextId[0][0] + 1;
        self.dbInsert(self.builder.createGame(nextId, game.gameToken, pOneId, pTwoId))

        self.dbInsert(self.builder.createPlayer(nextId, pOneId, game.player_one, \
                game.player_one_color, game.player_one_ip, "", \
                game.player_one_port, game.player_one_signon_token))



    def completeRandomGame(self, game):
        pTwoId = self.userDBFetch(self.builder.getUserId(game.player_two))
        pTwoId = pTwoId[0][0]
        self.dbInsert(self.builder.createPlayer(nextId, pTwoId, game.player_two, \
                game.player_two_color, game.player_two_ip, "", \
                game.player_two_port, game.player_two_signon_token))

    def searchForGame(self):
        result = self.dbFetch(self.builder.getOpenRandomGame())
        return result


    #Return 0 if false, 1 if true
    def validateUserExists(self, username):
        result = self.userDBFetch(self.builder.validateUserExists(username))
        #result = result[0][0]
        return result

    #Return 0 if false, 1 if true
    def validateGameExists(self, gameToken):
        result = self.dbFetch(self.builder.validateGameExists(gameToken))
        result = result[0][0]
        print(result)
        return result

    def getTokenCreationTime(self,username):
        result = self.userDBFetch(self.builder.getTokenCreationTime(username))
        return result

    def getSignonToken(self, username):
        result = self.userDBFetch(self.builder.getSignonToken(username))
        result = result[0][0]
        return result

    def acceptGame(self, gameToken):
        self.dbUpdate(self.builder.acceptGame(gameToken))

    def checkForGame(self, username):
        userId = self.userDBFetch(self.builder.getUserId(username))
        userId = userId[0][0]
        gameToken = self.dbFetch(self.builder.checkForGame(userId))
        gameToken = gameToken[0][0]
        #print(gameToken)
        return gameToken

    def updateSocket(self, username, ip, port):
        userId = self.userDBFetch(self.builder.getUserId(username))
        userId = userId[0][0]
        self.dbUpdate(self.builder.updateSocket(userId, ip, port))

    def getLastGameId(self):
        id = self.dbFetch(self.builder.getLastGameId())
        id = id[0][0]
        return id

    def getSocket(self, username):
        userId = self.userDBFetch(self.builder.getUserId(username))
        userId = userId[0][0]
        socket = self.dbFetch(self.builder.getSocket(userId))
        socket = socket[0]
        #print(socket)
        return socket

    def getGameId(self, token):
        gameId = self.dbFetch(self.builder.getGameId(token))
        gameId = gameId[0][0]
        return gameId

    def createPlayer(self, gameId, username, ip4, port, signonToken):
        userId = self.userDBFetch(self.builder.getUserId(username))
        userId = userId[0][0]
        self.dbInsert(self.builder.createPlayer(gameId, userId, ip4, "", \
                port, signonToken))

    def getGame(self, gameToken):
        gameId = self.getGameId(gameToken)
        game = self.dbFetch(self.builder.getGame(gameId))
        return game

    def getAvatar(self, username):
        avatarInt = self.userDBFetch(self.builder.getAvatar(username))
        avatarInt = avatarInt[0][0]
        return avatarInt

    def addGameWon(self, username):
        userId = self.userDBFetch(self.builder.getUserId(username))
        userId = userId[0][0]
        self.userDBUpdate(self.builder.addGameWon(userId))

    def addGameLost(self, username):
        userId = self.userDBFetch(self.builder.getUserId(username))
        userId = userId[0][0]
        self.userDBUpdate(self.builder.addGameLost(userId))

    def addGameResigned(self, username):
        userId = self.userDBFetch(self.builder.getUserId(username))
        userId = userId[0][0]
        self.userDBUpdate(self.builder.addGameResigned(userId))

    def addGamePlayed(self, username):
        userId = self.userDBFetch(self.builder.getUserId(username))
        userId = userId[0][0]
        self.userDBUpdate(self.builder.addGamePlayed(userId))
