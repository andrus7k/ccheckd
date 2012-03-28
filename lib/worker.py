# -*- coding: utf-8 -*-
from threading import Thread
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
        for identifier in plugin.identifiers:
            values = c.getval(identifier)
            print "[%s] %s: %s" % (self.name, identifier, ', '.join(values))

    def run(self):
        c = Collectd(self.sock_path, noisy=False)
        while True:
            plugin = self.q.get()
            self._fetchPlugin(plugin, c)
            self.q.task_done()