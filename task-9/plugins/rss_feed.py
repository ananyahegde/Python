from plugin_base import PluginBase

class RssFeed(PluginBase):
    name = "rss-feed"
    version = "1.0.0"
    dependencies = ["markdown-parser"]

    @classmethod
    def activate(cls):
        print(f"[{cls.name}] activated — registered command 'generate-rss'")

    @classmethod
    def deactivate(cls):
        print(f"[{cls.name}] deactivated")

