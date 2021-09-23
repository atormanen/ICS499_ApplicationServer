import multiprocessing
from multiprocessing import Process
from threading import Thread

from game.game_collection import GameCollection
from listener import Listener
from manifest import Manifest
from process_request import ProcessRequest


# Controller will initilaize all the objects and processes needed
# for the applications. It will sping up a few request request processors
# and then run the listener thread.
class Controller:

    # requestQueue is shared queue among all processes
    def __init__(self):
        self.manifest = Manifest()
        self.requestQueue = multiprocessing.Queue()
        self.gameQueue = multiprocessing.Queue()
        # self.gameCollectionQueue = multiprocessing.Queue()

        self.listener = Listener(self.requestQueue)
        self.gameCollection = GameCollection(self.listener)
        # self.gameCollection.startSocketChecker()

    def createRequestProcessor(self):
        req = ProcessRequest(self.requestQueue, self.gameQueue, self.gameCollection)
        req.processRequests()

    def createRequestProcessors(self):
        processes = []
        for i in range(self.manifest.number_of_request_processors):
            processes.append(Process(target=self.createRequestProcessor))
        for i in processes:
            i.start()

    def createListener(self):
        self.listener.createListener()
        # self.listener.listen()
        thread = Thread(target=self.listener.listen)
        thread.start()
        thread.join()


def main():
    print('inside main')


if __name__ == '__main__':
    c = Controller()
    c.createRequestProcessors()
    c.createListener()
    main()
