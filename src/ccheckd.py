# -*- coding: utf-8 -*-
from Queue import Queue
from threading import Thread
import time


__author__="andrus"
__date__ ="$Mar 24, 2012 2:52:57 PM$"

from collectd import Collectd

class Poller(Thread):

    def __init__ (self,q):
        Thread.__init__(self)
        self.q = q

    def run(self):
        while True:
            c = Collectd('/var/run/collectd.sock', noisy=False)
            for val in c.listval():
                stamp, identifier = val.split(' ',1)
                host, plugin, type = identifier.split('/',4)
                typeinstance = ''
                plugininstance = ''
                if "-" in plugin:
                    plugin, plugininstance = plugin.split('-',1)
                if "-" in type:
                    type, typeinstance = type.split('-',1)
                p = Plugin()
                p.name = plugin
                p.stamp = stamp
                p.host = host
                p.instance = plugininstance
                p.type = type
                p.typeinstance = typeinstance
                self.q.put(p)
            time.sleep(5)

class Worker(Thread):

    def __init__ (self,name,q):
        Thread.__init__(self)
        self.q = q
        self.name = name

    def run(self):
        while True:
            plugin = self.q.get()
            print "%s\t%s\t%s\t%s\t%s\t%s\t%s" % (self.name, plugin.stamp, plugin.host, plugin.name, plugin.instance, plugin.type, plugin.typeinstance)
            self.q.task_done()


class CCheckD():

    def start(self):
        q = Queue()
        poller = Poller(q)
        worker = Worker('a',q)
        worker.start()
        worker = Worker('b',q)
        worker.start()
        worker = Worker('c',q)
        worker.start()
        worker = Worker('d',q)
        worker.start()
        worker = Worker('e',q)
        worker.start()
        poller.start()

class Plugin():
    stamp = ''
    host = ''
    name = ''
    instance = ''
    type = ''
    typeinstance = ''
