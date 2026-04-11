from lexer import Lexer
from parser import Parser

source = "let x = 5 + 3"
tokens = Lexer(source).tokenize()

print("TOKENS: ")
for token in tokens:
    print(token)

print("\nNODES: ")
ast = Parser(tokens).parse()
for node in ast:
    print(node)

source = """
fn add(a, b) {
    return a + b
}
let x = add(3, 5)
"""

tokens = Lexer(source).tokenize()

print("\n\nTOKENS: ")
for token in tokens:
    print(token)

print("\nNODES: ")
ast = Parser(tokens).parse()
for node in ast:
    print(node)

