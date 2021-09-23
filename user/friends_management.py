#Friends management will handle the mechanics of sending freinds reqeusts,
#handeling friends lists, and accepting fiend requests
class FriendsManagement:

    def __init__(self, database):
        self.db = database

    def validateUsername(self, username):
        if(self.db.validate_user_exists(username)):
            return True
        return False

    def getFriendsList(self, parsedData, reqItem):
		#connect to mysqldb to get FriendsList
        friendsList = self.db.getFriendsList(parsedData["username"])
        reqItem.getFriendsListResponse(friendsList)

    def getUserStats(self, username):
        if(self.validateUsername(username)):
            stats = self.db.getUserStats(username)
            return stats
        return False

    def sendFriendRequest(self, parsedData, reqItem):
        #send a freind req
        username = parsedData["username"]
        friendsUsername = parsedData["friendsUsername"]
        result = False
        if(self.validateUsername(username)):
            if(self.validateUsername(friendsUsername)):
                result = self.db.sendFriendRequest(username, friendsUsername)
                reqItem.sendFriendReqResponse(result)
        reqItem.acceptFriendReqResponse(result)

    def validateFriendRequest(self, parsedData, reqItem):
        username = parsedData["username"]
        friendsUsername = parsedData["friendsUsername"]
        result = False
        if(self.validateUsername(username)):
            if(self.validateUsername(friendsUsername)):
                result = self.db.acceptFriendRequest(username, friendsUsername, True)
        reqItem.acceptFriendReqResponse(result)
