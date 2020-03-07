import mysql.connector
from database.MysqlDB import MysqlDB
#from queryBuilder import queryBuilder

#MysqlDB is a class used to implement common database queries programaticly. It
#uses the querryBuilder class which holds the actual mysql syntax.
class DB:

    def __init__(self, user, password, host, database):
        self.builder = MysqlDB()
        self.user = user
        self.password = password
        self.host = host
        self.database = database

    def dbInsert(self, statement):
        try:
            mydb = mysql.connector.connect(user=self.user, password=self.password,
                                  host=self.host,
                                  database=self.database,
                                  auth_plugin='mysql_native_password')
            cursor = mydb.cursor()
            cursor.execute(statement)
            mydb.commit()
            result = True
        except mysql.connector.Error as error:
            ## TODO: Log to error log
            print("Insert errror")
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
                                  host=self.host,
                                  database=self.database,
                                  auth_plugin='mysql_native_password')
            cursor = mydb.cursor()
            cursor.execute(statement)
            result = cursor.fetchall()
        except Error as e:
            ## TODO: Log error to log
            print("Error fetching data from db")
            result = False
        finally:
            if(mydb.is_connected()):
                cursor.close()
                mydb.close()
            return result

    def dbUpdate(self, statement):
        try:
            mydb = mysql.connector.connect(user=self.user, password=self.password,
                                  host=self.host,
                                  database=self.database,
                                  auth_plugin='mysql_native_password')
            cursor = mydb.cursor()
            cursor.execute(statement)
            mydb.commit()
            result = True
        except mysql.connector.Error as error:
            ## TODO: Log error to Log
            print("Error updating data to db")
            result = False
        finally:
            if(mydb.is_connected()):
                cursor.close()
                mydb.close()
            return result


    def getPasswordFor(self, username):
        result = self.dbFetch(self.builder.getPasswordFor(username))
        return result

    def incrementSigninFailed(self):
        return False

    def validateUserExists(self, username):
        statement = self.builder.validateUserExists(username)
        result = self.dbFetch(statement)
        return result

    #Returns 1\true if exits, false\0 if not
    def validateUsernameAvailable(self, username):
        statement = self.builder.validateUsernameAvailable(username)
        result = self.dbFetch(statement)
        intResult = result[0][0]
        return intResult

    def createUser(self, parsedData):
        id = self.dbFetch(self.builder.getLastUserId())
        id = str(id[0][0] + 1)
        statement = self.builder.createUser(id,parsedData)
        print(statement)
        self.dbInsert(statement)
        result = self.dbInsert(self.builder.createUserStats(id))
        return result

    def signin(self, username, token, tokenCreationTime):
        result = self.dbUpdate(self.builder.signin(username,token,tokenCreationTime))
        return result

    def getToken(self,username):
        result = self.dbFetch(self.builder.getToken(username))
        return result

    def getTokenCreationTime(self,username):
        result = self.dbFetch(self.builder.getTokenCreationTime(username))
        return result

    def getFriendsList(self, username):
        userId = self.dbFetch(self.builder.getUserId(username))
        result = self.dbFetch(self.builder.getFriendsList(userId[0][0]))
        return result

    def getUserInfo(self, username):

        return False

    def getUserStats(self, username):
        userId = self.dbFetch(self.builder.getUserId(username))
        userId = str(userId[0][0])
        result = self.dbFetch(self.builder.getUserStats(userId))
        return result

    def sendFriendRequest(self, username, friendsUsername):
        userId = self.dbFetch(self.builder.getUserId(username))
        friendsId = self.dbFetch(self.builder.getUserId(friendsUsername))
        if(userId == False):
            return False
        if(friendsId == False):
            return False
        userId = userId[0][0]
        friendsId = friendsId[0][0]
        result = self.dbInsert(self.builder.sendFriendRequest(userId,friendsId))
        return result

    def acceptFriendRequest(self, username, friendsUsername, acceptedRequest):
        userId = self.dbFetch(self.builder.getUserId(username))
        friendsId = self.dbFetch(self.builder.getUserId(friendsUsername))
        if(userId == False):
            return False
        if(friendsId == False):
            return False
        friendsId = friendsId[0][0]
        userId = userId[0][0]
        result = self.dbUpdate(self.builder.acceptFriendRequest(userId, friendsId, acceptedRequest))
        return result
