import re
from db import execute_query


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
    def __init__(self, max_length=255, unique=False):
        self.max_length = max_length
        self.unique = unique

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


class ForeignKey(Field):
    def __init__(self, to, related_name=None):
        self.to = to
        self.related_name = related_name

    def __set_name__(self, owner, name):
        self.name = name
        self.owner = owner
        self.column = f"{name}_id"
        if self.related_name:
            fk = self
            setattr(self.to, self.related_name, property(lambda instance: fk._reverse(instance)))

    def __set__(self, instance, value):
        if hasattr(value, 'id'):
            instance.__dict__[self.column] = value.id
        else:
            instance.__dict__[self.column] = value

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.column)

    def _reverse(self, instance):
        sql = f"SELECT * FROM {self.owner._table} WHERE {self.column} = ?"
        cursor = execute_query(sql, [instance.id], silent=True)
        rows = cursor.fetchall()
        results = []
        for row in rows:
            data = dict(row)
            obj = self.owner.__new__(self.owner)
            obj.id = data['id']
            for k, v in data.items():
                if k != 'id':
                    object.__setattr__(obj, k, v)
            results.append(obj)
        return results


class EmailField(CharField):
    def __set__(self, instance, value):
        if getattr(instance, 'id', None):
            super().__set__(instance, value)
            return
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError(f"{self.name} must be a valid email")

        existing = execute_query(f"SELECT id FROM {self.owner._table} WHERE email=?", [value], silent=True).fetchone()
        if existing:
            raise ValueError(f"{value} already exists")

        super().__set__(instance, value)

