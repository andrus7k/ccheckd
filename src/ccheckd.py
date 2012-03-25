# -*- coding: utf-8 -*-
from Queue import Queue
from threading import Thread
import time
from collectd import Collectd
from model import *

class Poller(Thread):

    def __init__ (self,q):
        Thread.__init__(self)
        self.q = q

    def run(self):
        plugin = Plugin()
        while True:
            c = Collectd('/var/run/collectd.sock', noisy=False)

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
                    plugin[typeName] = type

                if type.instances.has_key(typeInstanceName):
                    typeInstance = type.instances.get(typeInstanceName)
                else:
                    typeInstance = TypeInstance()
                    typeInstance.name = typeInstanceName
                    type.instances[typeInstanceName] = pluginInstance

                typeInstance.stamp = stamp

            time.sleep(5)

class Worker(Thread):

    def __init__ (self,name,q):
        Thread.__init__(self)
        self.q = q
        self.name = name

    def run(self):
        while True:
            plugin = self.q.get()
            print "%s\t%s\t%s\t%s\t%s\t%s\t%s" % (self.name, plugin.name, plugin.host, plugin.instances)
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
