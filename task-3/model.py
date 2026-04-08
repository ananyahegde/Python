from field import Field, CharField, ForeignKey
from db import execute_query
from query_set import QuerySet


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
        columns = []
        columns.append("id INTEGER PRIMARY KEY AUTOINCREMENT")
        for name, field in cls._fields.items():
            if isinstance(field, ForeignKey):
                columns.append(f"{field.column} INTEGER NOT NULL")
            else:
                col_type = "VARCHAR" if isinstance(field, CharField) else "INTEGER"
                nullable = "" if getattr(field, 'nullable', False) else " NOT NULL"
                columns.append(f"{name} {col_type}{nullable}")
        sql = f"CREATE TABLE IF NOT EXISTS {cls._table} ({', '.join(columns)})"
        execute_query(sql)

    @classmethod
    def read_all(cls):
        sql = f"SELECT * FROM {cls._table}"
        cursor = execute_query(sql)
        rows = cursor.fetchall()
        results = []
        for row in rows:
            data = dict(row)
            obj = cls.__new__(cls)
            obj.id = data['id']
            for k, v in data.items():
                if k != 'id':
                    setattr(obj, k, v)
            results.append(obj)
        return results

    @classmethod
    def read(cls, **kwargs):
        conditions = " AND ".join([f"{k}=?" for k in kwargs])
        sql = f"SELECT * FROM {cls._table} WHERE {conditions}"
        cursor = execute_query(sql, list(kwargs.values()))
        rows = cursor.fetchall()
        results = []
        for row in rows:
            data = dict(row)
            obj = cls.__new__(cls)
            obj.id = data['id']
            for k, v in data.items():
                if k != 'id':
                    setattr(obj, k, v)
            results.append(obj)
        return results

    @classmethod
    def filter(cls, **kwargs):
        return QuerySet(cls).filter(**kwargs)

    @classmethod
    def order_by(cls, field):
        return QuerySet(cls).order_by(field)

    def save(self):
        if hasattr(self, 'id') and self.id:
            self.update()
        else:
            columns_list = []
            values = []
            for col, field in self._fields.items():
                if isinstance(field, ForeignKey):
                    columns_list.append(field.column)
                    values.append(self.__dict__.get(field.column))
                else:
                    columns_list.append(col)
                    values.append(getattr(self, col, None))
            columns = ', '.join(columns_list)
            placeholders = ', '.join(['?' for _ in columns_list])
            sql = f"INSERT INTO {self._table} ({columns}) VALUES ({placeholders})"
            cursor = execute_query(sql, values)
            self.id = cursor.lastrowid

    def update(self, **kwargs):
        if not kwargs:
            return
        for key, val in kwargs.items():
            setattr(self, key, val)
        values = list(kwargs.values()) + [self.id]
        sql = f"UPDATE {self._table} SET {', '.join([f"{key}=?" for key in kwargs])} WHERE id=?"
        execute_query(sql, values)

    def delete(self):
        if not getattr(self, 'id', None):
            return
        sql = f"DELETE FROM {self._table} WHERE id=?"
        execute_query(sql, [self.id])

