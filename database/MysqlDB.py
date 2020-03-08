import time
import json
#This class holds all the mysql syntax for the sql class
## TODO: change MysqlDB to db and change querry builder to mysqlQuerry
class MysqlDB:

    def __init__(self):
        self.tableName = 'test'

    def buildQuery(self, data):
        now = time.strftime('%Y-%m-%d %H-%M-%S')
        parsedData = json.loads(data)
        return insertStatement

    def createGame(self, gameId, gameToken, playerOneId, playerTwoId):
        statement = "INSERT INTO game VALUES("+ str(gameId)+ ",'" + gameToken + "',"\
        + str(playerOneId) + "," + str(playerTwoId) + "," + "0);"
        print(statement)
        return statement

    def createPlayer(self, gameId, playerId, ip4, ip6, port, signon_token):
        statement = "INSERT INTO player VALUES(" + str(gameId) + "," + str(playerId) +\
        ",'" + ip4 +"','" + ip6 + "'," + str(port) + ",'" + signon_token + "');"
        print(statement)
        return statement

    def getLastGameId(self):
        return "SELECT MAX(game_id) FROM game;"


    def getUserId(self, username):
        querry = "SELECT user_id FROM user WHERE username = '" + username + "';"
        return querry

    def getTokenCreationTime(self,username):
        querry = "SELECT unix_timestamp(token_creation) FROM user WHERE username='" + username + "';"
        return querry

    def sendFriendRequest(self, user_id, friend_id):
        querry = "INSERT INTO friend_list VALUES(" + str(user_id) +\
                    ","+ str(friend_id) + ",0);"
        return querry

    def acceptFriendRequest(self, userId, friendId, acceptedRequest):
        querry = "UPDATE friend_list set request_accepted = " + str(acceptedRequest) +\
                    " WHERE friend_id = " + str(friendId) + " AND user_id = " +\
                    str(userId) + ";"
        return querry

    def validateUserExists(self,username):
        querry = "SELECT EXISTS(SELECT username FROM user WHERE username = '" +\
            username + "');"
        print(querry)
        return querry

    def getSignonToken(self, username):
        querry = "SELECT signon_token FROM user WHERE username='" + username + "';"
        return querry

    def acceptGame(self, gameToken):
        querry = "UPDATE game SET game_accepted = 1 WHERE game_token = '" +\
            gameToken + "';"
        return querry

    def checkForGame(self, usernameId):
        querry = "SELECT game_token FROM game WHERE player_two = " +\
            str(usernameId) + " AND game_accepted = 0;"
        return querry

    def updateSocket(self, userId, ip, port):
        querry = "UPDATE player SET ip4 ='" + ip + "', port =" + str(port) + " WHERE" + \
            " player_id = " + str(userId) + ";"
        return querry

    def getSocket(self, userId):
        querry = "SELECT ip4, port FROM player WHERE player_id = " + str(userId) + ";"
        print(querry)
        return querry;

    def getGameId(self, token):
        querry = "SELECT game_id FROM game WHERE game_token = '" + token + "';"
        return querry
