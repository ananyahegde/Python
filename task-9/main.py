from plugin_loader import PluginLoader
from dependency_resolver import resolve

loader = PluginLoader()
plugins = loader.load()

activation_order = resolve(plugins)

for plugin in activation_order:
    plugin.activate()
