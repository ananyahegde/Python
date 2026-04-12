from plugin_base import PluginBase

class ImageOptimizer(PluginBase):
    name = "image-optimizer"
    version = "0.9.1"
    dependencies = []

    @classmethod
    def activate(cls):
        print(f"[{cls.name}] activated — registered post-processor for .png/.jpg")

    @classmethod
    def deactivate(cls):
        print(f"[{cls.name}] deactivated")
