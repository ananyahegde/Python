from lexer import Lexer

# test lexer
lexer = Lexer("let x = 5 + 3")
tokens = lexer.tokenize()

print("Lexer for: let x = 5 + 3")
for token in tokens:
    print(token)

lexer = Lexer("fn add(a, b) { return a + b }")
tokens = lexer.tokenize()

print("\nLexer for: fn add(a, b) { return a + b }")
for token in tokens:
    print(token)
