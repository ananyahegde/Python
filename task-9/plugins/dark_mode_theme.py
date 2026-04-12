from plugin_base import PluginBase

class DarkModeTheme(PluginBase):
    name = "dark-mode-theme"
    version = "1.3.2"
    dependencies = []

    @classmethod
    def activate(cls):
        print(f"[{cls.name}] activated — registered theme 'dark-mode'")

    @classmethod
    def deactivate(cls):
        print(f"[{cls.name}] deactivated")
