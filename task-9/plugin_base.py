from abc import ABC, abstractmethod

class PluginBase(ABC):
    def __init__(self):
        name = ""
        version = ""
        dependencies = []

    @abstractmethod
    def activate(self):
        pass

    @abstractmethod
    def deactivate(self):
        pass


