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
    
    def __repr__(self):
        return f"{self.__dict__}"
    
    @classmethod
    def create_table(cls):
        """
            Class method for User and Post.
        """
        columns = []
        columns.append("id INTEGER PRIMARY KEY AUTOINCREMENT")
        for name, field in cls._fields.items():
            col_type = "VARCHAR" if isinstance(field, CharField) else "INTEGER"
            nullable = "" if getattr(field, 'nullable', False) else " NOT NULL"
            columns.append(f"{name} {col_type}{nullable}")

        # print sql equivalent statement
        sql = f"CREATE TABLE IF NOT EXISTS {cls._table} ({', '.join(columns)})"
        print(f"SQL: {sql}")

        execute(sql)

    @classmethod
    def read_all(cls):
        sql = f"SELECT * FROM {cls._table}"
        cursor = execute(sql)
        rows = cursor.fetchall()

        results = []
        for row in rows:
            data = dict(row)
            obj = cls(**{k: v for k, v in data.items() if k != 'id'})
            results.append(obj)
        return results
    
    @classmethod
    def read_one(cls, **kwargs):
        conditions = " AND ".join([f"{k}=?" for k in kwargs])
        sql = f"SELECT * FROM {cls._table} WHERE {conditions}"
        
        cursor = execute(sql, list(kwargs.values()))
        row = cursor.fetchone()

        if not row:
            return None

        data = dict(row)
        obj = cls(**{k: v for k, v in data.items() if k != 'id'})
        
        return obj


    def save(self):
        if hasattr(self, 'id') and self.id:
            self.update()

        else:
            columns = ', '.join(self._fields.keys())
            placeholders = ', '.join(['?' for _ in self._fields])
            values = [getattr(self, col, None) for col in self._fields]

            # print sql equivalent statement
            sql = f"INSERT INTO {self._table} ({columns}) VALUES ({placeholders})"
            print(f"SQL: {sql}")

            cursor = execute(sql, values)
            self.id = cursor.lastrowid

    def update(self, **kwargs):
        if not kwargs:
            return

        for key, val in kwargs.items():
            setattr(self, key, val)

        values = list(kwargs.values()) + [self.id]

        sql = f"UPDATE {self._table} SET {', '.join([f"{key}=?" for key in kwargs])} WHERE id=?"
        print(sql)
        
        execute(sql, values)
    
    def delete(self):
        if not getattr(self, 'id', None):
            return
        
        sql = f"DELETE FROM {self._table} WHERE id=?"
        print(sql)
        execute(sql, [self.id])

