import sys

class PluginFactory:
    @classmethod
    def get(cls,name,host):
        return getattr(sys.modules[__name__], name.capitalize())(name,host)

class Plugin(object):
    def __init__(self, name, host):
        self.name = name
        self.host = host
        self.identifiers = dict()
        self.stampMin = 0
        self.stampMax = 0

    def run(self):
        for identifier,values in self.identifiers.items():
            print "[%s] %s: %s" % (self.name, identifier, ', '.join(values))

class Cpu(Plugin):
    def __init__(self, name, host):
        super(self.__class__, self).__init__(name,host)

class Interface(Plugin):
    def __init__(self, name, host):
        super(Interface, self).__init__(name, host)

class Load(Plugin):
    def __init__(self, name, host):
        super(Load, self).__init__(name, host)

class Df(Plugin):
    def __init__(self, name, host):
        super(Df, self).__init__(name, host)

