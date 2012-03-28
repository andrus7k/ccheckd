# -*- coding: utf-8 -*-
from Queue import Queue
from threading import Thread
import time
from lib.ext.collectd import Collectd
from lib.plugins.plugins import Plugin

class Poller(Thread):
    evicted = list()
    def __init__ (self,sock_path,q):
        Thread.__init__(self)
        self.daemon = True
        self.q = q
        self.sock_path = sock_path

    def parseIdentifier(self, val):
        stamp, identifier = val.split(' ', 1)
        hostName, pluginName = identifier.split('/', 3)[:2]
        if "-" in pluginName:
            pluginName= pluginName.split('-', 1)[0]

        return stamp, hostName, pluginName, identifier

    def processIdentifiers(self, identifiers):
        for identifier in identifiers:
            stamp, hostName, pluginName, identifier = self.parseIdentifier(identifier)
            if self.evicted.__contains__(pluginName):
                continue
            try:
                if 'plugin' not in locals():
                    plugin = Plugin(pluginName, hostName)
                elif plugin.name != pluginName:
                    self.q.put(plugin)
                    plugin = Plugin(pluginName, hostName)
                plugin.identifiers.append(identifier)
            except AttributeError:
                self.evicted.append(pluginName)

    def run(self):
        c = Collectd(self.sock_path, noisy=True)
        while True:
            identifiers = c.listval()
            self.processIdentifiers(identifiers)
            time.sleep(5)


class Worker(Thread):

    def __init__ (self,name,sock_path,q):
        Thread.__init__(self)
        self.daemon = True
        self.q = q
        self.name = name
        self.sock_path = sock_path

    def _echoPlugin(self, plugin):
        for instance in plugin.instances.values():
            print "\tinstance=%s" % (instance.name)
            for type in instance.types.values():
                print "\t\ttype=%s" % (type.name)
                for typeInstance in type.instances.values():
                    print "\t\t\t%s:" % (typeInstance.identifier)

    def _fetchPlugin(self, plugin, c):
        for identifier in plugin.identifiers:
                    values = c.getval(identifier)
                    print "[%s] %s: %s" % (self.name, identifier, ', '.join(values))

    def run(self):
        c = Collectd(self.sock_path, noisy=False)
        while True:
            plugin = self.q.get()
            self._fetchPlugin(plugin, c)
            self.q.task_done()


class CCheckD(Thread):

    def __init__ (self,sock_path,workers=1):
        Thread.__init__(self)
        self.workers = workers
        self.sock_path = sock_path
        self.q = Queue()


    def run(self):
        self._startWorkers()
        self._startPoller()

    def _startPoller(self):
        poller = Poller(self.sock_path,self.q)
        poller.start()
        poller.join()

    def _startWorkers(self):
        for i in xrange(self.workers):
            worker = Worker(str(i),self.sock_path,self.q)
            worker.start()