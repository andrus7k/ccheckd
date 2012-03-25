# -*- coding: utf-8 -*-
from Queue import Queue
from threading import Thread
import time
from collectd import Collectd
from model import Plugin

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
        worker = Worker('a',q)
        worker.start()
        worker = Worker('b',q)
        worker.start()
        poller = Poller(q)
        poller.start()
