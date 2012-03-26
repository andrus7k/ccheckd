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

    def parseIdentifier(self, val):
        stamp, identifier = val.split(' ', 1)
        hostName, pluginName, typeName = identifier.split('/', 4)
        typeInstanceName = ''
        pluginInstanceName = ''
        if "-" in pluginName:
            pluginName, pluginInstanceName = pluginName.split('-', 1)
        if "-" in typeName:
            typeName, typeInstanceName = typeName.split('-', 1)
        return stamp, hostName, pluginName, pluginInstanceName, typeName, typeInstanceName, identifier

    def processIdentifiers(self, identifiers):
        for identifier in identifiers:
            stamp, hostName, pluginName, pluginInstanceName, typeName, typeInstanceName, identifier = self.parseIdentifier(identifier)

            if 'plugin' not in locals():
                plugin = Plugin(pluginName, hostName)
            elif plugin.name != pluginName:
                self.q.put(plugin)
                plugin = Plugin(pluginName, hostName)

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
                typeInstance.identifier = identifier
                type.instances[typeInstanceName] = typeInstance

            typeInstance.stamp = stamp

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
        for instance in plugin.instances.values():
            for type in instance.types.values():
                for typeInstance in type.instances.values():
                    values = c.getval(typeInstance.identifier)
                    print "[%s] %s: %s" % (self.name, typeInstance.identifier, ', '.join(values))

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