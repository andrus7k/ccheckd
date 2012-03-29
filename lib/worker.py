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
                    print "[WORKER:%s] ERROR: GETVAL %s, retry=%s)" % (self.name, identifier, i)
                    time.sleep(.1)
                except Exception, e:
                    print "[WORKER:%s] ERROR: GETVAL %s, %s)" % (self.name, identifier, e)
                    break

    def run(self):
        c = Collectd(self.sock_path, noisy=False)
        while True:
            plugin = self.q.get()
            self._fetchPlugin(plugin, c)
            try:
                plugin.run()
            except Exception, e:
                print "[WORKER:%s] ERROR: %s@%s, %s" % (self.name, plugin.name, plugin.host, str(e))
            self.q.task_done()