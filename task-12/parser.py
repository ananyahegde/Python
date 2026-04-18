from tokenizer import Token, TokenType, Tokenizer, TokenizerError


class ParseError(Exception):
    pass


class Parser:
    """
    Consumes a token list produced by Tokenizer and returns a command dict
    describing the operation to execute.
    Supported commands:
        CREATE NODE (alias:Label {props})
        CREATE EDGE (alias)-[:TYPE {props}]->(alias)
        MATCH (alias:Label)-[:TYPE]->(alias:Label) WHERE ... RETURN ...
        SHORTEST_PATH (alias)-[*min..max]->(alias)
        STATS
    """

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def _current(self) -> Token:
        return self.tokens[self.pos]

    def _peek(self, offset=1) -> Token:
        p = self.pos + offset
        return self.tokens[p] if p < len(self.tokens) else Token(TokenType.EOF)

    def _advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def _expect(self, ttype: TokenType, value: str = None) -> Token:
        """
        Consume the current token, asserting its type and optionally its value.
        Raises ParseError if the assertion fails.
        """
        tok = self._advance()
        if tok.type != ttype:
            raise ParseError(f"Expected {ttype} but got {tok.type}")
        if value is not None and tok.value != value:
            raise ParseError(f"Expected '{value}' but got '{tok.value}'")
        return tok

    def _expect_keyword(self, value: str) -> Token:
        return self._expect(TokenType.KEYWORD, value)

    def _match_keyword(self, value: str) -> bool:
        """Return True and advance if current token is the given keyword."""
        tok = self._current()
        if tok.type == TokenType.KEYWORD and tok.value == value:
            self.pos += 1
            return True
        return False

    def parse(self) -> dict:
        """Parse the full token stream and return a command dict."""
        tok = self._current()

        if tok.type == TokenType.KEYWORD and tok.value == "CREATE":
            return self._parse_create()
        elif tok.type == TokenType.KEYWORD and tok.value == "MATCH":
            return self._parse_match()
        elif tok.type == TokenType.KEYWORD and tok.value == "SHORTEST_PATH":
            return self._parse_shortest_path()
        elif tok.type == TokenType.KEYWORD and tok.value == "STATS":
            self._advance()
            return {"cmd": "STATS"}
        else:
            raise ParseError(f"Unknown command starting with: {tok}")

    # CREATE
    def _parse_create(self) -> dict:
        self._expect_keyword("CREATE")
        tok = self._current()

        if tok.type == TokenType.KEYWORD and tok.value == "NODE":
            return self._parse_create_node()
        elif tok.type == TokenType.KEYWORD and tok.value == "EDGE":
            return self._parse_create_edge()
        else:
            raise ParseError(f"Expected NODE or EDGE after CREATE, got {tok}")

    def _parse_create_node(self) -> dict:
        self._expect_keyword("NODE")
        self._expect(TokenType.LPAREN)
        alias = self._expect(TokenType.IDENT).value
        self._expect(TokenType.COLON)
        label = self._expect(TokenType.IDENT).value
        props = {}
        if self._current().type == TokenType.LBRACE:
            props = self._parse_props()
        self._expect(TokenType.RPAREN)
        return {"cmd": "CREATE_NODE", "alias": alias, "label": label, "props": props}

    def _parse_create_edge(self) -> dict:
        self._expect_keyword("EDGE")

        # (from_alias)
        self._expect(TokenType.LPAREN)
        from_alias = self._expect(TokenType.IDENT).value
        self._expect(TokenType.RPAREN)

        # -[:TYPE {props}]->
        self._expect(TokenType.DASH)
        self._expect(TokenType.LBRACKET)
        self._expect(TokenType.COLON)
        edge_type = self._expect(TokenType.IDENT).value
        props = {}
        if self._current().type == TokenType.LBRACE:
            props = self._parse_props()
        self._expect(TokenType.RBRACKET)
        self._expect(TokenType.ARROW_R)

        # (to_alias)
        self._expect(TokenType.LPAREN)
        to_alias = self._expect(TokenType.IDENT).value
        self._expect(TokenType.RPAREN)

        return {
            "cmd": "CREATE_EDGE",
            "from_alias": from_alias,
            "to_alias": to_alias,
            "edge_type": edge_type,
            "props": props
        }

    # MATCH
    def _parse_match(self) -> dict:
        """
        Parses:
            MATCH (alias:Label)-[:TYPE]->(alias:Label)-[:TYPE]->(alias:Label)...
            WHERE alias.prop = "value"
            RETURN alias.prop, alias.prop
        """
        self._expect_keyword("MATCH")

        # Parse start node
        self._expect(TokenType.LPAREN)
        start_alias = self._expect(TokenType.IDENT).value
        self._expect(TokenType.COLON)
        start_label = self._expect(TokenType.IDENT).value
        self._expect(TokenType.RPAREN)

        # alias -> position map, used to resolve WHERE and RETURN
        alias_map = {start_alias: 0}
        hops = []

        # Parse hops: -[:TYPE]->(alias:Label)
        while self._current().type == TokenType.DASH:
            self._expect(TokenType.DASH)
            self._expect(TokenType.LBRACKET)
            self._expect(TokenType.COLON)
            edge_type = self._expect(TokenType.IDENT).value
            self._expect(TokenType.RBRACKET)
            self._expect(TokenType.ARROW_R)

            self._expect(TokenType.LPAREN)
            node_alias = self._expect(TokenType.IDENT).value
            node_label = None
            if self._current().type == TokenType.COLON:
                self._advance()
                node_label = self._expect(TokenType.IDENT).value
            self._expect(TokenType.RPAREN)

            position = len(hops) + 1
            alias_map[node_alias] = position
            hops.append({
                "edge_type": edge_type,
                "node_label": node_label,
                "node_filters": {}
            })

        # WHERE alias.prop = value
        where_filters = {}
        if self._current().type == TokenType.KEYWORD and self._current().value == "WHERE":
            self._advance()
            alias = self._expect(TokenType.IDENT).value
            self._expect(TokenType.DOT)
            prop = self._expect(TokenType.IDENT).value
            self._expect(TokenType.EQUALS)
            value = self._parse_literal()
            pos = alias_map.get(alias)
            if pos is None:
                raise ParseError(f"Unknown alias in WHERE: {alias}")
            where_filters[pos] = {prop: value}

        # RETURN alias.prop, alias.prop
        return_fields = []
        if self._current().type == TokenType.KEYWORD and self._current().value == "RETURN":
            self._advance()
            while self._current().type == TokenType.IDENT:
                alias = self._expect(TokenType.IDENT).value
                self._expect(TokenType.DOT)
                prop = self._expect(TokenType.IDENT).value
                pos = alias_map.get(alias)
                if pos is None:
                    raise ParseError(f"Unknown alias in RETURN: {alias}")
                return_fields.append({"alias": alias, "prop": prop, "pos": pos})
                if self._current().type == TokenType.COMMA:
                    self._advance()

        return {
            "cmd": "MATCH",
            "start_alias": start_alias,
            "start_label": start_label,
            "start_filters": {},
            "hops": hops,
            "where_filters": where_filters,
            "return_fields": return_fields,
            "alias_map": alias_map
        }

    # SHORTEST PATH
    def _parse_shortest_path(self) -> dict:
        """
        Parses:
            SHORTEST_PATH (from_alias)-[*min..max]->(to_alias)
        """
        self._expect_keyword("SHORTEST_PATH")

        self._expect(TokenType.LPAREN)
        from_alias = self._expect(TokenType.IDENT).value
        self._expect(TokenType.RPAREN)

        self._expect(TokenType.DASH)
        self._expect(TokenType.LBRACKET)
        self._expect(TokenType.STAR)

        min_hops = 1
        max_hops = None
        if self._current().type == TokenType.NUMBER:
            min_hops = int(self._advance().value)
        if self._current().type == TokenType.DOTDOT:
            self._advance()
            if self._current().type == TokenType.NUMBER:
                max_hops = int(self._advance().value)

        self._expect(TokenType.RBRACKET)
        self._expect(TokenType.ARROW_R)

        self._expect(TokenType.LPAREN)
        to_alias = self._expect(TokenType.IDENT).value
        self._expect(TokenType.RPAREN)

        return {
            "cmd": "SHORTEST_PATH",
            "from_alias": from_alias,
            "to_alias": to_alias,
            "min_hops": min_hops,
            "max_hops": max_hops
        }

    # Shared parsers
    def _parse_props(self) -> dict:
        """
        Parses a property map: {key: value, key: value, ...}
        Values can be strings, numbers, or booleans.
        """
        props = {}
        self._expect(TokenType.LBRACE)
        while self._current().type != TokenType.RBRACE:
            key = self._expect(TokenType.IDENT).value
            self._expect(TokenType.COLON)
            value = self._parse_literal()
            props[key] = value
            if self._current().type == TokenType.COMMA:
                self._advance()
        self._expect(TokenType.RBRACE)
        return props

    def _parse_literal(self) -> str | int | float | bool:
        """Parse a single literal value — string, number, or boolean."""
        tok = self._advance()
        if tok.type == TokenType.STRING:
            return tok.value
        elif tok.type == TokenType.NUMBER:
            return tok.value
        elif tok.type == TokenType.IDENT and tok.value.lower() == "true":
            return True
        elif tok.type == TokenType.IDENT and tok.value.lower() == "false":
            return False
        else:
            raise ParseError(f"Expected a literal value, got {tok}")


def parse(query: str) -> dict:
    """Convenience function — tokenize and parse a query string in one call."""
    tokens = Tokenizer(query).tokenize()
    return Parser(tokens).parse()
