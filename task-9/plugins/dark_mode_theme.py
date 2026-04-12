from plugin_base import PluginBase

class DarkModeTheme(PluginBase):
    name = "dark-mode-theme"
    version = "1.3.2"
    dependencies = []

    def activate(self):
        print(f"[{self.name}] activated — registered theme 'dark-mode'")

    def deactivate(self):
        print(f"[{self.name}] deactivated")
