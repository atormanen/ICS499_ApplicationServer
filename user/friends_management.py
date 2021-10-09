# Friends management will handle the mechanics of sending freinds reqeusts,
# handeling friends lists, and accepting fiend requests
from data.message_item import MessageItem


class FriendsManagement:

    log_function_name = lambda x: logger.debug(f"func {inspect.stack()[1][3]}")

    def __init__(self, database):
        self.db = database

    def validate_username(self, username):
        self.log_function_name()
        if self.db.user_exists(username):
            return True
        return False

    def get_friends_list(self, parsed_data, req_item):
        self.log_function_name()
        # connect to mysqldb to get FriendsList
        friends_list = self.db.get_friends_list(parsed_data["username"])
        req_item.getFriendsListResponse(friends_list)

    def get_user_stats(self, username):
        self.log_function_name()
        if self.validate_username(username):
            stats = self.db.get_user_stats(username)
            return stats
        return False

    def send_friend_request(self, parsed_data, req_item):
        self.log_function_name()
        # send a freind req
        username = parsed_data["username"]
        friends_username = parsed_data["friends_username"]
        result = False
        if self.validate_username(username):
            if self.validate_username(friends_username):
                result = self.db.send_friend_request(username, friends_username)
                req_item.sendFriendReqResponse(result)
        req_item.acceptFriendReqResponse(result)

    def validate_friend_request(self, parsed_data, req_item: MessageItem):
        self.log_function_name()
        username = parsed_data["username"]
        friends_username = parsed_data["friends_username"]
        result = False
        if self.validate_username(username):
            if self.validate_username(friends_username):
                result = self.db.acceptFriendRequest(username, friends_username, True)
        req_item.accept_friend_request_response(result)  # FIXME
