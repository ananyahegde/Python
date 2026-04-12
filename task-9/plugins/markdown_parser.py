from plugin_base import PluginBase

class MarkdownParser(PluginBase):
    name = "markdown-parser"
    version = "2.1.0"
    dependencies = []

    @classmethod
    def activate(cls):
        print(f"[{cls.name}] activated — registered .md -> HTML converter")

    @classmethod
    def deactivate(cls):
        print(f"[{cls.name}] deactivated")
