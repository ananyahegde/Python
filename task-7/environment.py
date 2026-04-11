class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars.keys():
            return self.vars[name]
        elif self.parent is not None:
            return self.parent.get(name)
        else:
            raise Exception(f"Undefined variable: {name}")

    def set(self, name, value):
        self.vars[name] = value
