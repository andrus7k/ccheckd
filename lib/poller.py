# -*- coding: utf-8 -*-
from threading import Thread
from plugins import PluginFactory
from plugins import Plugin
import time
from ext import Collectd

class Poller(Thread):
    evicted = list()

    def __init__ (self,sock_path,q,sleep=30):
        Thread.__init__(self)
        self.daemon = True
        self.q = q
        self.sock_path = sock_path
        self.sleep = sleep

    def parseIdentifier(self, val):
        stamp, identifier = val.split(' ', 1)
        hostName, pluginName = identifier.split('/', 3)[:2]
        if "-" in pluginName:
            pluginName= pluginName.split('-', 1)[0]

        return stamp, hostName, pluginName, identifier

    def processIdentifiers(self, identifiers):
        plugin = None
        for identifier in identifiers:
            stamp, hostName, pluginName, identifier = self.parseIdentifier(identifier)

            if isinstance(plugin,Plugin):
                if pluginName != plugin.name:
                    print "[POLLER] QED %s@%s" % (plugin.name, plugin.host)
                    self.q.put(plugin)
                    plugin = None

            if self.evicted.__contains__(pluginName):
                continue

            try:
                if not isinstance(plugin,Plugin):
                    plugin = PluginFactory.get(pluginName, hostName)
                plugin.identifiers[identifier] = 0
            except Exception, e:
                self.evicted.append(pluginName)
                plugin = None
                print "[POLLER] ERROR evicting %s with exeception %s" % (pluginName, str(e))


    def run(self):
        c = Collectd(self.sock_path, noisy=False)
        while True:
            x1 = time.clock()
            identifiers = c.listval()
            x2 = time.clock()
            self.processIdentifiers(identifiers)
            x3 = time.clock()
            listvalTime = x2 - x1
            processingTime = x3 - x2
            print '[POLLER] LISTVAL %s in %ss, PROCESSED %ss, sleeping %ss' % (len(identifiers),listvalTime,processingTime, self.sleep)
            time.sleep(self.sleep)
