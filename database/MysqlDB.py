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

    def getPasswordFor(self, username):
        selectStatement = "SELECT password FROM user WHERE username ='" +\
            username + "';"
        return selectStatement

    def validateUserExists(self,username):
        return "SELECT EXISTS(SLECT username FROM user WHERE username = " +\
            username + " );"

    def validateUsernameAvailable(self,username):
        return "SELECT EXISTS(SELECT username FROM user WHERE username = '" +\
            username + "' );"

    def getLastUserId(self):
        return "SELECT MAX(user_id) FROM user;"

    def createUser(self, id, parsedData):
        now = time.strftime('%Y-%m-%d %H-%M-%S')
        return "INSERT INTO user VALUES("+ id +",'" + parsedData["username"] +\
            "','" +parsedData["firstName"] + "','" + parsedData["lastName"] +\
            "','" + parsedData["email"] + "',0,'" + parsedData["password"] +\
            "','" + now + "','" + "null" +\
             "');"

    def createUserStats(self, id):
        return "INSERT INTO user_statistics VALUES("+ id +" ,0,0,0,0,0,1);"

    def getFriendsList(self, id):
        querry = "select user.user_id, user.username \
                    from user \
                    inner join  friend_list \
                    on user.user_id = friend_list.friend_id \
                    where friend_list.user_id = " + str(id) + ";"
        return querry

    def getUserId(self, username):
        querry = "SELECT user_id FROM user WHERE username = '" + username + "';"
        return querry

    def getUserStats(self, id):
        querry = "SELECT * FROM user_statistics WHERE user_id = " + id + ";"
        return querry

    def signin(self, username, token, tokenExpiration):
        querry = "UPDATE user SET token_expiration='"+tokenExpiration + \
                    "',signon_token='" + token + "' WHERE username = " + \
                    "'" + username + "';"
        return querry

    def getToken(self,username):
        querry = "SELECT signon_token FROM user WHERE username='" + username + "';"
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
