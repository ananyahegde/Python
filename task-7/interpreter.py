from ast_nodes import *
from environment import Environment
from lexer import TokenType

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class Interpreter:
    def __init__(self):
        self.env = Environment()

    def run(self, statements):
        for statement in statements:
            self.execute(statement)

    def execute(self, node):
        if isinstance(node, LetDecl):
            value = self.execute(node.value)
            self.env.set(node.name, value)

        elif isinstance(node, NumberLiteral):
            return node.value

        elif isinstance(node, StringLiteral):
            return node.value

        elif isinstance(node, Identifier):
            return self.env.get(node.name)

        elif isinstance(node, BinOp):
            left = self.execute(node.left)
            right = self.execute(node.right)
            if node.op == TokenType.PLUS:   return left + right
            if node.op == TokenType.MINUS:  return left - right
            if node.op == TokenType.STAR:   return left * right
            if node.op == TokenType.SLASH:  return left // right
            if node.op == TokenType.EQUALS: return left == right
            if node.op == TokenType.NE:     return left != right
            if node.op == TokenType.LT:     return left < right
            if node.op == TokenType.GT:     return left > right
            if node.op == TokenType.LTE:    return left <= right
            if node.op == TokenType.GTE:    return left >= right

        elif isinstance(node, PrintStatement):
            value = self.execute(node.value)
            print(value)

        elif isinstance(node, IfStatement):
            condition = self.execute(node.condition)
            if condition:
                for stmt in node.body:
                    self.execute(stmt)
            else:
                for stmt in node.else_body:
                    self.execute(stmt)

        elif isinstance(node, WhileLoop):
            while self.execute(node.condition):
                for stmt in node.body:
                    self.execute(stmt)

        elif isinstance(node, FunctionDecl):
            self.env.set(node.name, node)

        elif isinstance(node, FunctionCall):
            fn = self.env.get(node.name)
            args = [self.execute(a) for a in node.args]
            local_env = Environment(parent=self.env)
            for param, arg in zip(fn.params, args):
                local_env.set(param, arg)
            previous_env = self.env
            self.env = local_env
            result = None
            try:
                for stmt in fn.body:
                    self.execute(stmt)
            except ReturnException as r:
                result = r.value
            self.env = previous_env
            return result

        elif isinstance(node, ReturnStatement):
            raise ReturnException(self.execute(node.value))
