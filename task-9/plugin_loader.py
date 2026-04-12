import os
import importlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class PluginLoader:
    plugins = []

    def scan(self, path):
        filenames = []
        for filename in os.scandir(os.path.join(BASE_DIR, path)):
            if filename.name.endswith(".py"):
                filenames.append(filename.name)
        return filenames

    def load(self):
        path ='/plugins'
        filenames = self.scan(path)
        for filename in filenames:
            module_name = filename.replace(".py", "")
            importlib.import_module(module_name)

        for filename in filenames:
            importlib.import_module(filename)

    def activate_all(self):
        for plugin in self.plugins:
            plugin.activate()

    def deactivate_all(self):
        for plugin in self.plugins:
            plugin.deactivate()
