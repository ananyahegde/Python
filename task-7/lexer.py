from enum import Enum, auto
from dataclasses import dataclass


class TokenType(Enum):
    # keywords
    LET    = auto()
    FN     = auto()
    IF     = auto()
    ELSE = auto()
    WHILE = auto()
    RETURN = auto()
    PRINT = auto()

    # identifiers
    IDENT = auto()

    # literals
    INT = auto()
    STRING = auto()

    # operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()

    # comparision operators
    EQUALS = auto()
    LTE = auto()
    GTE = auto()
    NE = auto()
    LT = auto()
    GT = auto()

    # assignment operator
    ASSIGN = auto()

    # paranthesis
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    COMMA = auto()

    # End of token
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: object = None


class Lexer:
    def __init__(self, source):
        self.source = source
        self.pos = 0

    def curr_char(self):
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]

    def advance(self):
        self.pos += 1

    def peek(self):
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos + 1]

    def tokenize(self):
        tokens = []
        while self.curr_char() is not None:

            # whitespace
            if self.curr_char() in (" ", "\n", "\t"):
                self.advance()

            # parentheses and braces
            elif self.curr_char() == '(':
                tokens.append(Token(TokenType.LPAREN))
                self.advance()
            elif self.curr_char() == ')':
                tokens.append(Token(TokenType.RPAREN))
                self.advance()
            elif self.curr_char() == '{':
                tokens.append(Token(TokenType.LBRACE))
                self.advance()
            elif self.curr_char() == '}':
                tokens.append(Token(TokenType.RBRACE))
                self.advance()
            elif self.curr_char() == ',':
                tokens.append(Token(TokenType.COMMA))
                self.advance()

            # operators
            elif self.curr_char() == '+':
                tokens.append(Token(TokenType.PLUS))
                self.advance()
            elif self.curr_char() == '-':
                tokens.append(Token(TokenType.MINUS))
                self.advance()
            elif self.curr_char() == '*':
                tokens.append(Token(TokenType.STAR))
                self.advance()
            elif self.curr_char() == '/':
                tokens.append(Token(TokenType.SLASH))
                self.advance()

            # comparison and assignment
            elif self.curr_char() == '=':
                if self.peek() == '=':
                    tokens.append(Token(TokenType.EQUALS))
                    self.advance()
                    self.advance()
                else:
                    tokens.append(Token(TokenType.ASSIGN))
                    self.advance()
            elif self.curr_char() == '<':
                if self.peek() == '=':
                    tokens.append(Token(TokenType.LTE))
                    self.advance()
                    self.advance()
                else:
                    tokens.append(Token(TokenType.LT))
                    self.advance()
            elif self.curr_char() == '>':
                if self.peek() == '=':
                    tokens.append(Token(TokenType.GTE))
                    self.advance()
                    self.advance()
                else:
                    tokens.append(Token(TokenType.GT))
                    self.advance()
            elif self.curr_char() == '!':
                if self.peek() == '=':
                    tokens.append(Token(TokenType.NE))
                    self.advance()
                    self.advance()

            # numbers
            elif self.curr_char().isdigit():
                num = self.curr_char()
                self.advance()
                while self.curr_char() and self.curr_char().isdigit():
                    num += self.curr_char()
                    self.advance()
                tokens.append(Token(TokenType.INT, int(num)))

            # strings
            elif self.curr_char() == '"':
                self.advance()
                s = ""
                while self.curr_char() != '"':
                    s += self.curr_char()
                    self.advance()
                self.advance()
                tokens.append(Token(TokenType.STRING, s))

            # identifiers and keywords
            elif self.curr_char().isalpha():
                word = self.curr_char()
                self.advance()
                while self.curr_char() and self.curr_char().isalpha():
                    word += self.curr_char()
                    self.advance()
                keywords = {
                    "let": TokenType.LET,
                    "fn": TokenType.FN,
                    "if": TokenType.IF,
                    "else": TokenType.ELSE,
                    "while": TokenType.WHILE,
                    "return": TokenType.RETURN,
                    "print": TokenType.PRINT,
                }
                if word in keywords:
                    tokens.append(Token(keywords[word]))
                else:
                    tokens.append(Token(TokenType.IDENT, word))

            else:
                raise Exception(f"Unknown character: {self.curr_char()}")

        tokens.append(Token(TokenType.EOF))
        return tokens
