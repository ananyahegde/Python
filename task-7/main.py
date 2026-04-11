from lexer import Lexer
from parser import Parser
from interpreter import Interpreter

print("="*15)
print("FIBONACCI OF 10")
print("="*15)

source = """
fn fibonacci(n) {
    if n <= 1 {
        return n
    }
    return fibonacci(n - 1) + fibonacci(n - 2)
}
let result = fibonacci(10)
print(result)
"""

tokens = Lexer(source).tokenize()
ast = Parser(tokens).parse()
interpreter = Interpreter()
interpreter.run(ast)

print("\n\n")
print("="*15)
print("WHILE LOOP")
print("="*15)

source = """
let x = 10
while x > 0 {
    print(x)
    let x = x - 1
}
"""

tokens = Lexer(source).tokenize()
ast = Parser(tokens).parse()
interpreter = Interpreter()
interpreter.run(ast)

