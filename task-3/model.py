from field import Field, CharField
from db import execute

class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        fields = {}
        for key, val in attrs.items():
            if isinstance(val, Field):
                fields[key] = val
        attrs['_fields'] = fields
        attrs['_table'] = name.lower()
        return super().__new__(cls, name, bases, attrs)


class Model(metaclass=ModelMeta):
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    def save(self):
        columns = ', '.join(self._fields.keys())
        placeholders = ', '.join(['?' for _ in self._fields])
        values = [getattr(self, col, None) for col in self._fields]
        
        # print sql equivalent statement
        sql = f"INSERT INTO {self._table} ({columns}) VALUES ({placeholders})"
        print(f"SQL: {sql}")
        print(f"VALUES: {values}")
        
        execute(sql, values)

    @classmethod
    def create_table(cls):
        columns = []
        columns.append("id INTEGER PRIMARY KEY AUTOINCREMENT")
        for name, field in cls._fields.items():
            col_type = "VARCHAR" if isinstance(field, CharField) else "INTEGER"
            nullable = "" if getattr(field, 'nullable', False) else " NOT NULL"
            columns.append(f"{name} {col_type}{nullable}")
        sql = f"CREATE TABLE IF NOT EXISTS {cls._table} ({', '.join(columns)})"
        
        # print sql equivalent statement
        print(f"SQL: {sql}")

        execute(sql)
