from data.message_item import MessageItem
from data.responder import Responder
from database.db import DB
from game.game_generator import GameGenerator
from game.request_validator import RequestValidator
from manifest import Manifest


# from game.Tokens import Tokens


class RequestProcessor:

    # PrecessReqeust is set up to be a seperate process in the OS and
    # will hold the shared request queue object. It will pull requests
    # from the queue as they are inserted from the listener
    def __init__(self, request_queue, game_queue, game_collection):
        self.manifest: Manifest = Manifest()
        reader = self.manifest.database_reader
        writer = self.manifest.database_writer
        username = self.manifest.database_username
        password = self.manifest.database_password
        game_database = self.manifest.game_database_name
        self.database = DB(username, password, reader, writer, game_database)
        # self.database = DB('app','123','192.168.1.106', '192.168.1.106','gamedb')
        self.request_queue = request_queue
        self.game_queue = game_queue
        self.req_validation = RequestValidator()
        self.responder = Responder()
        self.game_collection = game_collection
        self.game_collection.set_database(self.database)
        self.game_generator = GameGenerator(self.database, self.game_queue, self.game_collection)

    ## TODO: find a better way to process these requests types.
    def proccesrequest_type(self, req_item: MessageItem):
        if self.req_validation.is_bad_request(req_item.parsed_data):
            self.responder.send_bad_request_response(req_item.connection_socket)
            return
        print(req_item.parsed_data)
        parsed_data = req_item.parsed_data
        try:
            if parsed_data["request_type"] == "CreateGame":
                self.game_generator.create_game(parsed_data, req_item)
                self.responder.send_response(req_item)
            elif parsed_data["request_type"] == "AcceptGame":
                self.game_generator.acceptGame(parsed_data, req_item)
                addr = self.database.get_socket(parsed_data["player_one_username"])
                pOneMsgItem = MessageItem(None, addr, None)
                self.responder.send_accepted_response(pOneMsgItem, req_item)
            elif parsed_data["request_type"] == "MatchCommunication":

                # forward the communication to the opponent
                game = self.game_collection.get_game_from_token(parsed_data["game_token"])
                was_successful: bool = game.forward_match_communication(parsed_data["username"], parsed_data["payload"])

                # send response
                req_item.create_match_communication_response(was_successful)
                self.responder.send_response(req_item)

            elif parsed_data["request_type"] == "MatchResultReport":

                # send a success response because we understand and accept the report
                # TODO implement this

                # put this as one of the results reported for that game
                # TODO implement this

                # if two results are reported, and they match, update statistics on DB
                # TODO implement this

                # else if two results are reported, regardless of if they match, end the game
                # TODO implement this

                # else if the participant that did not report is not connected, we end the game and update statistics
                # TODO implement this

                # else we keep the game alive and continue processing requests.
                # TODO implement this

                raise NotImplementedError  # FIXME by removing this line after we finish this

            elif parsed_data["request_type"] == "ErrorReport":

                # send a success response because we understand and accept the report
                # TODO implement this

                # send the opponent of the sender a ERROR match result
                # TODO implement this

                # end this game.
                # TODO implement this

                # increment the conflict count on each participant's account in DB
                # TODO implement this

                # do not track leaderboard statistics for this game

                raise NotImplementedError  # FIXME by removing this line after we finish this

            elif parsed_data["request_type"] == "CheckForGame":
                self.game_generator.checkForGame(parsed_data, req_item)
                self.responder.send_response(req_item)
            elif parsed_data["request_type"] == "RequestGame":
                result = self.game_generator.create_random_game(parsed_data, req_item)
                if (result == False):
                    self.responder.send_random_game_response(req_item)
            elif parsed_data["request_type"] == "RequestGameCanceled":
                self.game_generator.request_game_canceled(parsed_data, req_item)
                self.responder.send_response(req_item)
            else:
                self.responder.send_bad_request_response(req_item.connection_socket)
        except KeyError:
            print("Process Request - Key error")

    # The process thread will block on requestQueue.get() until something
    # arrives.
    def process_requests(self):
        while True:
            # print("blocking on req item")
            request_item = self.request_queue.get()
            print("Processing request")
            # Decrypt parsed_data
            self.proccesrequest_type(request_item)
