import sys

class Plugin():
    def __init__(self, name, host):
        self.__class__ = getattr(sys.modules[__name__], name.capitalize())
        self.name = name
        self.host = host
        self.instances = {}
        self.identifiers = []
        self.stampMin = 0
        self.stampMax = 0

    def run(self):
        print "%s: %s" (self.__class__.__name__, ', '.join(self.identifiers))

class Cpu(Plugin):
    def run(self):
        super(self.__class__, self).run()

class Interface(Plugin):
    def run(self):
        super(self.__class__, self).run()

class Load(Plugin):
    def run(self):
        super(self.__class__, self).run()