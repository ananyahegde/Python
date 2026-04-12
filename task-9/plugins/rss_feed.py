from plugin_base import PluginBase

class RssFeed(PluginBase):
    name = "rss-feed"
    version = "1.0.0"
    dependencies = ["markdown-parser"]

    def activate(self):
        print(f"[{self.name}] activated — registered command 'generate-rss'")

    def deactivate(self):
        print(f"[{self.name}] deactivated")

