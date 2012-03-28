# -*- coding: utf-8 -*-
from Queue import Queue
from threading import Thread
from poller import Poller
from worker import Worker

class CCheckD(Thread):

    def __init__ (self,sock_path,sleep=5,workers=1):
        Thread.__init__(self)
        self.sleep = sleep
        self.workers = workers
        self.sock_path = sock_path
        self.q = Queue()

    def run(self):
        self._startWorkers()
        self._startPoller()

    def _startPoller(self):
        poller = Poller(self.sock_path,self.q,self.sleep)
        poller.start()
        poller.join()

    def _startWorkers(self):
        for i in xrange(self.workers):
            worker = Worker(str(i),self.sock_path,self.q)
            worker.start()