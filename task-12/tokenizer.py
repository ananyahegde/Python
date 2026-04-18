from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    KEYWORD    = auto()  # CREATE, NODE, EDGE, MATCH, WHERE, RETURN, SHORTEST_PATH, STATS
    IDENT      = auto()  # alice, Person, FRIENDS_WITH
    STRING     = auto()  # "Alice"
    NUMBER     = auto()  # 30, 2.5
    COLON      = auto()  # :
    COMMA      = auto()  # ,
    DOT        = auto()  # .
    LPAREN     = auto()  # (
    RPAREN     = auto()  # )
    LBRACE     = auto()  # {
    RBRACE     = auto()  # }
    LBRACKET   = auto()  # [
    RBRACKET   = auto()  # ]
    ARROW_R    = auto()  # ->
    DASH       = auto()  # -
    STAR       = auto()  # *
    DOTDOT     = auto()  # ..
    EQUALS     = auto()  # =
    EOF        = auto()


KEYWORDS = {
    "CREATE", "NODE", "EDGE", "MATCH",
    "WHERE", "RETURN", "SHORTEST_PATH", "STATS"
}


@dataclass
class Token:
    type: TokenType
    value: str | int | float | None = None

    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"


class TokenizerError(Exception):
    pass


class Tokenizer:
    """
    Converts a raw query string into a flat list of Token objects.
    Handles keywords, identifiers, strings, numbers, and all punctuation
    used in the query language.
    """

    def __init__(self, text: str):
        self.text = text.strip()
        self.pos = 0
        self.tokens: list[Token] = []

    def tokenize(self) -> list[Token]:
        """
        Entry point. Scans the full input and returns the token list
        with a final EOF token appended.
        """
        while self.pos < len(self.text):
            self._skip_whitespace()
            if self.pos >= len(self.text):
                break
            self._scan_next()
        self.tokens.append(Token(TokenType.EOF))
        return self.tokens

    def _skip_whitespace(self):
        while self.pos < len(self.text) and self.text[self.pos] in " \t\n\r":
            self.pos += 1

    def _current(self) -> str:
        return self.text[self.pos]

    def _peek(self, offset=1) -> str | None:
        p = self.pos + offset
        return self.text[p] if p < len(self.text) else None

    def _scan_next(self):
        ch = self._current()

        if ch == '"' or ch == "'":
            self._scan_string(ch)
        elif ch.isdigit() or (ch == '-' and self._peek() and self._peek().isdigit()):
            self._scan_number()
        elif ch == '-':
            if self._peek() == '>':
                self.tokens.append(Token(TokenType.ARROW_R, '->'))
                self.pos += 2
            else:
                self.tokens.append(Token(TokenType.DASH, '-'))
                self.pos += 1
        elif ch == '.':
            if self._peek() == '.':
                self.tokens.append(Token(TokenType.DOTDOT, '..'))
                self.pos += 2
            else:
                self.tokens.append(Token(TokenType.DOT, '.'))
                self.pos += 1
        elif ch == ':':
            self.tokens.append(Token(TokenType.COLON, ':'))
            self.pos += 1
        elif ch == ',':
            self.tokens.append(Token(TokenType.COMMA, ','))
            self.pos += 1
        elif ch == '(':
            self.tokens.append(Token(TokenType.LPAREN, '('))
            self.pos += 1
        elif ch == ')':
            self.tokens.append(Token(TokenType.RPAREN, ')'))
            self.pos += 1
        elif ch == '{':
            self.tokens.append(Token(TokenType.LBRACE, '{'))
            self.pos += 1
        elif ch == '}':
            self.tokens.append(Token(TokenType.RBRACE, '}'))
            self.pos += 1
        elif ch == '[':
            self.tokens.append(Token(TokenType.LBRACKET, '['))
            self.pos += 1
        elif ch == ']':
            self.tokens.append(Token(TokenType.RBRACKET, ']'))
            self.pos += 1
        elif ch == '*':
            self.tokens.append(Token(TokenType.STAR, '*'))
            self.pos += 1
        elif ch == '=':
            self.tokens.append(Token(TokenType.EQUALS, '='))
            self.pos += 1
        elif ch.isalpha() or ch == '_':
            self._scan_ident_or_keyword()
        else:
            raise TokenizerError(f"Unexpected character: {ch!r} at position {self.pos}")

    def _scan_string(self, quote: str):
        """Scan a quoted string literal, returning its content without quotes."""
        self.pos += 1  # skip opening quote
        start = self.pos
        while self.pos < len(self.text) and self.text[self.pos] != quote:
            self.pos += 1
        if self.pos >= len(self.text):
            raise TokenizerError("Unterminated string literal")
        value = self.text[start:self.pos]
        self.pos += 1  # skip closing quote
        self.tokens.append(Token(TokenType.STRING, value))

    def _scan_number(self):
        """Scan an integer or float literal."""
        start = self.pos
        if self.text[self.pos] == '-':
            self.pos += 1
        while self.pos < len(self.text) and self.text[self.pos].isdigit():
            self.pos += 1
        if self.pos < len(self.text) and self.text[self.pos] == '.':
            self.pos += 1
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1
            self.tokens.append(Token(TokenType.NUMBER, float(self.text[start:self.pos])))
        else:
            self.tokens.append(Token(TokenType.NUMBER, int(self.text[start:self.pos])))

    def _scan_ident_or_keyword(self):
        """
        Scan an identifier or keyword. Identifiers can contain letters,
        digits, and underscores. If the uppercased value is in KEYWORDS,
        emit a KEYWORD token, otherwise emit an IDENT token.
        """
        start = self.pos
        while self.pos < len(self.text) and (self.text[self.pos].isalnum() or self.text[self.pos] == '_'):
            self.pos += 1
        value = self.text[start:self.pos]
        if value.upper() in KEYWORDS:
            self.tokens.append(Token(TokenType.KEYWORD, value.upper()))
        else:
            self.tokens.append(Token(TokenType.IDENT, value))
