from lexer import TokenType, Token
from ast_nodes import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def curr_token(self):
        return self.tokens[self.pos]

    def advance(self):
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def expect(self, type):
        token = self.curr_token()
        if token.type != type:
            raise Exception(f"Expected {type} but got {token.type}")
        return self.advance()

    def parse(self):
        statements = []
        while self.curr_token().type != TokenType.EOF:
            statements.append(self.parse_statement())
        return statements

    def parse_statement(self):
        token = self.curr_token()

        if token.type == TokenType.LET:
            return self.parse_let()
        elif token.type == TokenType.FN:
            return self.parse_function()
        elif token.type == TokenType.IF:
            return self.parse_if()
        elif token.type == TokenType.WHILE:
            return self.parse_while()
        elif token.type == TokenType.RETURN:
            return self.parse_return()
        elif token.type == TokenType.PRINT:
            return self.parse_print()
        else:
            return self.parse_expression()

    def parse_let(self):
        self.advance()  # skip 'let'
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        return LetDecl(name, value)

    def parse_function(self):
        self.advance()  # skip 'fn'
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.LPAREN)
        params = []
        while self.curr_token().type != TokenType.RPAREN:
            params.append(self.expect(TokenType.IDENT).value)
            if self.curr_token().type == TokenType.COMMA:
                self.advance()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.LBRACE)
        body = []
        while self.curr_token().type != TokenType.RBRACE:
            body.append(self.parse_statement())
        self.expect(TokenType.RBRACE)
        return FunctionDecl(name, params, body)

    def parse_if(self):
        self.advance()  # skip 'if'
        condition = self.parse_expression()
        self.expect(TokenType.LBRACE)
        body = []
        while self.curr_token().type != TokenType.RBRACE:
            body.append(self.parse_statement())
        self.expect(TokenType.RBRACE)
        else_body = []
        if self.curr_token().type == TokenType.ELSE:
            self.advance()
            self.expect(TokenType.LBRACE)
            while self.curr_token().type != TokenType.RBRACE:
                else_body.append(self.parse_statement())
            self.expect(TokenType.RBRACE)
        return IfStatement(condition, body, else_body)

    def parse_while(self):
        self.advance()  # skip 'while'
        condition = self.parse_expression()
        self.expect(TokenType.LBRACE)
        body = []
        while self.curr_token().type != TokenType.RBRACE:
            body.append(self.parse_statement())
        self.expect(TokenType.RBRACE)
        return WhileLoop(condition, body)

    def parse_return(self):
        self.advance()  # skip 'return'
        value = self.parse_expression()
        return ReturnStatement(value)

    def parse_print(self):
        self.advance()  # skip 'print'
        self.expect(TokenType.LPAREN)
        value = self.parse_expression()
        self.expect(TokenType.RPAREN)
        return PrintStatement(value)

    def parse_expression(self):
        left = self.parse_term()
        while self.curr_token().type in (
            TokenType.PLUS, TokenType.MINUS,
            TokenType.EQUALS, TokenType.NE,
            TokenType.LT, TokenType.GT,
            TokenType.LTE, TokenType.GTE
        ):
            op = self.advance().type
            right = self.parse_term()
            left = BinOp(left, op, right)
        return left

    def parse_term(self):
        left = self.parse_primary()
        while self.curr_token().type in (TokenType.STAR, TokenType.SLASH):
            op = self.advance().type
            right = self.parse_primary()
            left = BinOp(left, op, right)
        return left

    def parse_primary(self):
        token = self.curr_token()

        if token.type == TokenType.INT:
            self.advance()
            return NumberLiteral(token.value)

        elif token.type == TokenType.STRING:
            self.advance()
            return StringLiteral(token.value)

        elif token.type == TokenType.IDENT:
            self.advance()
            if self.curr_token().type == TokenType.LPAREN:
                self.expect(TokenType.LPAREN)
                args = []
                while self.curr_token().type != TokenType.RPAREN:
                    args.append(self.parse_expression())
                    if self.curr_token().type == TokenType.COMMA:
                        self.advance()
                self.expect(TokenType.RPAREN)
                return FunctionCall(token.value, args)
            return Identifier(token.value)

        elif token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr

        else:
            raise Exception(f"Unexpected token: {token}")
