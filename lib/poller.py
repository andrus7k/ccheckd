# -*- coding: utf-8 -*-
from threading import Thread
from plugins import Plugin
import time
from ext import Collectd

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
