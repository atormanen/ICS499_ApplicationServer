from Listener import Listener
from database.DB import DB
from multiprocessing import Process, Manager
from multiprocessing.managers import BaseManager
import multiprocessing
from threading import Thread
from ProcessRequest import ProcessRequest
import os
import queue
from GameManagement.GameCollection import GameCollection

#Controller will initilaize all the objects and processes needed
#for the applications. It will sping up a few request request processors
#and then run the listener thread.
class Controller:

    #requestQueue is shared queue among all processes
    def __init__(self):
        self.requestQueue = multiprocessing.Queue()
        self.gameQueue = multiprocessing.Queue()
        #self.gameCollectionQueue = multiprocessing.Queue()
        self.gameCollection = GameCollection()
        self.listener = Listener(self.requestQueue)



    def createRequestProcessor(self):
        req = ProcessRequest(self.requestQueue, self.gameQueue, self.gameCollection)
        req.processRequests()

    def createRequestProcessors(self):
        processes = []
        for i in range(1):
            #print('Createing processes %d' % i)
            processes.append(Process(target=self.createRequestProcessor))
        for i in processes:
            i.start()

    def createListener(self):
        self.listener.createListener()
        #self.listener.listen()
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
