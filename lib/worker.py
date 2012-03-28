# -*- coding: utf-8 -*-
from threading import Thread
import time
from ext import Collectd

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
        for identifier in plugin.identifiers.keys():
            i = 5;
            while i > 0:
                try:
                    values = c.getval(identifier)
                    plugin.identifiers[identifier] = values
                    break
                except KeyError:
                    i=i-1
                    print "[%s] ERROR: GETVAL %s failed (will retry %s times)" % (self.name, identifier, i)
                    time.sleep(.1)

    def run(self):
        c = Collectd(self.sock_path, noisy=False)
        while True:
            plugin = self.q.get()
            self._fetchPlugin(plugin, c)
            plugin.run()
            self.q.task_done()