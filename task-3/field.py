class Field:
    def __set_name__(self, owner, name):
        self.name = name
        self.owner = owner

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value


class CharField(Field):
    def __init__(self, max_length=255):
        self.max_length = max_length

    def __set__(self, instance, value):
        if not isinstance(value, str):
            raise TypeError(f"{self.name} must be a string")
        if len(value) > self.max_length:
            raise ValueError(f"{self.name} exceeds max_length of {self.max_length}")
        super().__set__(instance, value)


class IntegerField(Field):
    def __init__(self, nullable=False):
        self.nullable = nullable

    def __set__(self, instance, value):
        if value is None and self.nullable:
            super().__set__(instance, value)
            return
        if not isinstance(value, int):
            raise TypeError(f"{self.name} must be an int")
        super().__set__(instance, value)
