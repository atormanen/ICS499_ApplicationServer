import multiprocessing
from multiprocessing import Process
from threading import Thread

import listener
import manifest
from game.game_collection import GameCollection
from listener import Listener
from manifest import Manifest
from request_processor import RequestProcessor


# Controller will initilaize all the objects and processes needed
# for the applications. It will sping up a few request request processors
# and then run the listener thread.
class Controller:

    # requestQueue is shared queue among all processes
    def __init__(self):
        self.manifest: manifest.Manifest = Manifest()
        self.requestQueue: multiprocessing.Queue = multiprocessing.Queue()
        self.gameQueue: multiprocessing.Queue = multiprocessing.Queue()
        # self.gameCollectionQueue = multiprocessing.Queue()

        self.listener: listener.Listener = Listener(self.requestQueue)
        self.gameCollection: GameCollection = GameCollection(self.listener)
        # self.gameCollection.start_socket_checker()

    def create_request_processor(self):
        req: RequestProcessor = RequestProcessor(self.requestQueue, self.gameQueue, self.gameCollection)
        req.process_requests()

    def create_request_processors(self):
        processes = []
        for i in range(self.manifest.number_of_request_processors):
            processes.append(Process(target=self.create_request_processor))
        for i in processes:
            i.start()

    def create_listener(self):
        self.listener.create_listener()
        # self.listener.listen()
        thread = Thread(target=self.listener.listen)
        thread.start()
        thread.join()


def main():
    print('inside main')


if __name__ == '__main__':
    c = Controller()
    c.create_request_processors()
    c.create_listener()
    main()
