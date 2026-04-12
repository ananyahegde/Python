import os
import sys
import importlib
import inspect
from plugin_base import PluginBase

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class PluginLoader:
    plugins = []

    def scan(self, path):
        filenames = []
        for filename in os.scandir(os.path.join(BASE_DIR, path)):
            if filename.name.endswith(".py"):
                filenames.append(filename.name)
        return filenames

    def load(self, path="plugins"):
        sys.path.insert(0, os.path.join(BASE_DIR, path))
        filenames = self.scan(path)

        for filename in filenames:
            module_name = filename.replace(".py", "")
            module = importlib.import_module(module_name)
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, PluginBase) and obj is not PluginBase:
                    self.plugins.append(obj)
        return self.plugins

    def activate_all(self):
        for plugin in self.plugins:
            plugin.activate()

    def deactivate_all(self):
        for plugin in self.plugins:
            plugin.deactivate()
