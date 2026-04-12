from plugin_base import PluginBase

class MarkdownParser(PluginBase):
    name = "markdown-parser"
    version = "2.1.0"
    dependencies = []

    def activate(self):
        print(f"[{self.name}] activated — registered .md -> HTML converter")

    def deactivate(self):
        print(f"[{self.name}] deactivated")
