# -*- coding: utf-8 -*-
__author__="andrus"
__date__ ="$Mar 24, 2012 2:52:57 PM$"

from collectd import Collectd

if __name__ == '__main__':
    c = Collectd('/var/run/collectd.sock', noisy=True)

    for val in c.listval():
        stamp, identifier = val.split(' ',1)
        host, plugin, type = identifier.split('/',4)
        typeinstance = ''
        plugininstance = ''

        if "-" in plugin:
            plugin, plugininstance = plugin.split('-',1)

        if "-" in type:
            type, typeinstance = type.split('-',1)

        print "%s\t%s\t%s\t%s\t%s\t%s" % (stamp, host, plugin, plugininstance, type, typeinstance)
