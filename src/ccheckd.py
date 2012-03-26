# -*- coding: utf-8 -*-
from Queue import Queue
from threading import Thread
import time
import signal
from collectd import Collectd
from model import *

class Poller(Thread):

    def __init__ (self,sock_path,q):
        Thread.__init__(self)
        self.daemon = True
        self.q = q
        self.sock_path = sock_path

    def run(self):
        plugin = Plugin()
        c = Collectd(self.sock_path, noisy=True)
        while True:
            for val in c.listval():
                stamp, identifier = val.split(' ',1)
                hostName, pluginName, typeName = identifier.split('/',4)
                typeInstanceName = ''
                pluginInstanceName = ''

                if "-" in pluginName:
                    pluginName, pluginInstanceName = pluginName.split('-',1)
                if "-" in typeName:
                    typeName, typeInstanceName = typeName.split('-',1)

                if plugin.name != pluginName:
                    self.q.put(plugin)
                    plugin=Plugin()
                    plugin.name = pluginName
                    plugin.host = hostName

                if plugin.instances.has_key(pluginInstanceName):
                    pluginInstance = plugin.instances.get(pluginInstanceName)
                else:
                    pluginInstance = PluginInstance()
                    pluginInstance.name = pluginInstanceName
                    plugin.instances[pluginInstanceName] = pluginInstance

                if pluginInstance.types.has_key(typeName):
                    type = pluginInstance.types.get(typeName)
                else:
                    type = Type()
                    type.name = typeName
                    pluginInstance.types[typeName] = type

                if type.instances.has_key(typeInstanceName):
                    typeInstance = type.instances.get(typeInstanceName)
                else:
                    typeInstance = TypeInstance()
                    typeInstance.name = typeInstanceName
                    type.instances[typeInstanceName] = pluginInstance

                typeInstance.stamp = stamp
            time.sleep(5)

class Worker(Thread):

    def __init__ (self,name,sock_path,q):
        Thread.__init__(self)
        self.daemon = True
        self.q = q
        self.name = name

    def run(self):
        while True:
            plugin = self.q.get()
            print "\t%s\t%s\t%s\t%s" % (self.name, plugin.name, plugin.host, ', '.join(plugin.instances.keys()))
            self.q.task_done()

class CCheckD(Thread):

    def __init__ (self,sock_path,workers=1):
        Thread.__init__(self)
        checkd = self
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