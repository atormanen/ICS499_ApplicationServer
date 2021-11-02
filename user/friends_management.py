# TODO Remove if not needed
# # Friends management will handle the mechanics of sending freinds reqeusts,
# # handeling friends lists, and accepting fiend requests
# from data.message_item import MessageItem
# from global_logger import *
#
#
# class FriendsManagement:
#
#     def __init__(self, database):
#         self.db = database
#
#     @logged_method
#     def validate_username(self, username):
#
#         if self.db.user_exists(username):
#             return True
#         return False
#
#     @logged_method
#     def get_friends_list(self, parsed_data, req_item: MessageItem):
#
#         # connect to mysqldb to get FriendsList
#         friends_list = self.db.get_friends_list(parsed_data["username"])
#         req_item.getFriendsListResponse(friends_list)
#
#     @logged_method
#     def get_user_stats(self, username):
#
#         if self.validate_username(username):
#             stats = self.db.get_user_stats(username)
#             return stats
#         return False
#
#     @logged_method
#     def send_friend_request(self, parsed_data, req_item: MessageItem):
#
#         # send a freind req
#         username = parsed_data["username"]
#         friends_username = parsed_data["friends_username"]
#         result = False
#         if self.validate_username(username):
#             if self.validate_username(friends_username):
#                 result = self.db.send_friend_request(username, friends_username)
#                 req_item.sendFriendReqResponse(result)
#         req_item.acceptFriendReqResponse(result)
#
#     @logged_method
#     def validate_friend_request(self, parsed_data, req_item: MessageItem):
#
#         username = parsed_data["username"]
#         friends_username = parsed_data["friends_username"]
#         result = False
#         if self.validate_username(username):
#             if self.validate_username(friends_username):
#                 result = self.db.acceptFriendRequest(username, friends_username, True)
#         req_item.accept_friend_request_response(result)  # FIXME
