# -*- coding: utf-8 -*-
class Plugin():
    name = ''
    host = ''
    instances = dict()

class PluginInstance():
    name = ''
    types = dict()

class Type():
    name = ''
    instances = dict()

class TypeInstance():
    name = ''
    stamp = ''
    values = dict()