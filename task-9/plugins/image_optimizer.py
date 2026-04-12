from plugin_base import PluginBase

class ImageOptimizer(PluginBase):
    name = "image-optimizer"
    version = "0.9.1"
    dependencies = []

    def activate(self):
        print(f"[{self.name}] activated — registered post-processor for .png/.jpg")

    def deactivate(self):
        print(f"[{self.name}] deactivated")
