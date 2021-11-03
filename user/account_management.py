# TODO Remove if not needed
#
# Is this class nececary? Should it be combined with signin?
# from database.db import DB
# from database.mysql_db import MysqlQueryBuilder
#
# from mysql.connector import Error as MySQLError
#
#
# class AccountManager:
#
#     log_function_name = lambda x: logger.debug(f"func {inspect.stack()[1][3]}")
#
#     username = ''
#     password = ''
#
#     def __init__(self, mysqlDB):
#         self.db: MysqlQueryBuilder = mysqlDB
#
#     def validate_username(self, username):
#         self.log_function_name()
#         if self.db.user_exists(username):
#             return True
#         return False
#
#     def create_account(self, parsedData):
#         self.log_function_name()
#         # check if username exists
#         # return false if username alread exists
#         username_is_available = not self.db.user_exists(parsedData["username"])
#         # call mysqlDB to create CreateAccount
#         if username_is_available:
#             try:
#                 self.db.create_user(parsedData)  # FIXME
#                 return True
#             except MySQLError:
#                 return False
#         else:
#             return False
#         # if account creation is successful return true otherwise False
#
#     def get_user_stats(self, parsed_data, req_item):
#         self.log_function_name()
#         stats = self.db.get_user_stats(parsed_data["username"])  # FIXME
#         req_item.getUSerStatsResponse(stats[0])
