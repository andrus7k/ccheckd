# -*- coding: utf-8 -*-
class Plugin():
    def __init__(self, name, host):
        self.name = name
        self.host = host
        self.instances = {}

class PluginInstance():
    def __init__(self):
        self.name = ''
        self.types = {}

class Type():
    def __init__(self):
        self.name = ''
        self.instances = {}

class TypeInstance():
    def __init__(self):
        self.name = ''
        self.stamp = ''
        self.identifier = {}
        self.values = {}