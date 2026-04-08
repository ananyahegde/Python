from db import execute_query

class QuerySet:
    def __init__(self, model):
        self.model = model
        self.conditions = []
        self.values = []
        self.order = None

    def filter(self, **kwargs):
        lookups = {
            'gte': '>=', 'lte': '<=',
            'gt': '>', 'lt': '<',
            'eq': '='
        }
        for key, val in kwargs.items():
            if '__' in key:
                col, op = key.split('__')
                self.conditions.append(f"{col} {lookups[op]} ?")
            else:
                self.conditions.append(f"{key} = ?")
            self.values.append(val)
        return self

    def order_by(self, field):
        if field.startswith('-'):
            self.order = f"{field[1:]} DESC"
        else:
            self.order = f"{field} ASC"
        return self

    def all(self):
        sql = f"SELECT * FROM {self.model._table}"
        if self.conditions:
            sql += f" WHERE {' AND '.join(self.conditions)}"
        if self.order:
            sql += f" ORDER BY {self.order}"
        cursor = execute_query(sql, self.values)
        rows = cursor.fetchall()
        results = []
        for row in rows:
            data = dict(row)
            obj = self.model.__new__(self.model)
            obj.id = data['id']
            for k, v in data.items():
                if k != 'id':
                    object.__setattr__(obj, k, v)
            results.append(obj)
        return results
