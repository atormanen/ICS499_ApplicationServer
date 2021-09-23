from data.message_item import MessageItem
from data.responder import Responder
from database.db import DB
from game.game_generator import GameGenerator
from game.validate_request import ValidateRequest
from manifest import Manifest


# from game.Tokens import Tokens


class ProcessRequest:

    # PrecessReqeust is set up to be a seperate process in the OS and
    # will hold the shared request queue object. It will pull requests
    # from the queue as they are inserted from the listener
    def __init__(self, requestQueue, gameQueue, gameCollection):
        self.manifest = Manifest()
        reader = self.manifest.database_reader
        writer = self.manifest.database_writer
        username = self.manifest.database_username
        password = self.manifest.database_password
        gameDatabase = self.manifest.game_database_name
        self.database = DB(username, password, reader, writer, gameDatabase)
        # self.database = DB('app','123','192.168.1.106', '192.168.1.106','gamedb')
        self.requestQueue = requestQueue
        self.gameQueue = gameQueue
        self.reqValidation = ValidateRequest()
        self.responder = Responder()
        self.gameCollection = gameCollection
        self.gameCollection.setDatabase(self.database)
        self.gameGenerator = GameGenerator(self.database, self.gameQueue, self.gameCollection)

    ## TODO: find a better way to process these requests types.
    def proccesrequest_type(self, reqItem: MessageItem):
        if self.reqValidation.isBadRequest(reqItem.parsed_data):
            self.responder.send_bad_request_response(reqItem.connection_socket)
            return
        print(reqItem.parsed_data)
        parsedData = reqItem.parsed_data
        try:
            if parsedData["request_type"] == "CreateGame":
                self.gameGenerator.createGame(parsedData, reqItem)
                self.responder.send_response(reqItem)
            elif parsedData["request_type"] == "AcceptGame":
                self.gameGenerator.acceptGame(parsedData, reqItem)
                addr = self.database.get_socket(parsedData["player_one_username"])
                pOneMsgItem = MessageItem(None, addr, None)
                self.responder.send_accepted_response(pOneMsgItem, reqItem)
            elif parsedData["request_type"] == "MatchCommunication":

                # forward the communication to the opponent
                game = self.gameCollection.getGameFromToken(parsedData["game_token"])
                was_successful: bool = game.forward_match_communication(parsedData["username"], parsedData["payload"])

                # send response
                reqItem.create_match_communication_response(was_successful)
                self.responder.send_response(reqItem)

            elif parsedData["request_type"] == "MatchResultReport":

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

            elif parsedData["request_type"] == "ErrorReport":

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

            elif parsedData["request_type"] == "CheckForGame":
                self.gameGenerator.checkForGame(parsedData, reqItem)
                self.responder.send_response(reqItem)
            elif parsedData["request_type"] == "RequestGame":
                result = self.gameGenerator.createRandomGame(parsedData, reqItem)
                if (result == False):
                    self.responder.send_random_game_response(reqItem)
            elif parsedData["request_type"] == "RequestGameCanceled":
                self.gameGenerator.requestGameCanceled(parsedData, reqItem)
                self.responder.send_response(reqItem)
            else:
                self.responder.send_bad_request_response(reqItem.connection_socket)
        except KeyError:
            print("Process Request - Key error")

    # The process thread will block on requestQueue.get() until something
    # arrives.
    def processRequests(self):
        while True:
            # print("blocking on req item")
            requestItem = self.requestQueue.get()
            print("Processing request")
            # Decrypt parsed_data
            self.proccesrequest_type(requestItem)
