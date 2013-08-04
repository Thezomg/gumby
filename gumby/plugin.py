#!/usr/bin/env python

"""
Simple plugin loader from http://yannik520.github.io/python_plugin_framework.html
"""


import os,sys

class _Plugin(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(_Plugin, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    class __metaclass__(type):
        def __init__(cls, name, bases, attrs):
            if not hasattr(cls, 'plugins'):
                cls.plugins = {}
            else:
                cls.plugins[attrs['name']] = cls()
        def show_plugins(cls):
            for kls in cls.plugins.values():
                    print kls
        def get_plugins(cls):
            return cls.plugins

    def process_file(self, config, path):
        raise NotImplementedError("%s does not implement process_file" % (self.get_name().strip()))

    def process_pom(self, config, path):
        raise NotImplementedError("%s does not implement process_pom" % (self.get_name().strip()))


class PluginMgr(object):
    plugin_dirs = {}
    # make the manager class as singleton
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PluginMgr, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self):
        self.plugin_dir="plugins/"
        self.plugin_dirs[self.plugin_dir] = False

    def _load_all(self):
        for (pdir, loaded) in self.plugin_dirs.iteritems():
            if loaded: continue

            sys.path.insert(0, pdir)
            for mod in [x[:-3] for x in os.listdir(pdir) if x.endswith(".py")]:
                if mod and mod != '__init__':
                    if mod in sys.modules:
                        print "Module %s already exists, skip" % mod
                    else:
                        try:
                            pymod = __import__(mod)
                            self.plugin_dirs[pdir] = True
                            print "Plugin module %s:%s imported"\
                                        % (mod, pymod.__file__)
                        except ImportError, e:
                            print 'Loading failed, skip plugin %s/%s'\
                                          % (os.path.basename(pdir), mod)

            del(sys.path[0])


    def get_plugins(self):
        """ the return value is dict of name:class pairs """
        self._load_all()
        return _Plugin.get_plugins()

pluginmgr = PluginMgr()