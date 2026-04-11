from dataclasses import dataclass, field
from typing import Any, List

@dataclass
class NumberLiteral:
    value: int

@dataclass
class StringLiteral:
    value: str

@dataclass
class Identifier:
    name: str

@dataclass
class BinOp:
    left: Any
    op: Any
    right: Any

@dataclass
class LetDecl:
    name: str
    value: Any

@dataclass
class IfStatement:
    condition: Any
    body: List
    else_body: List = field(default_factory=list)

@dataclass
class WhileLoop:
    condition: Any
    body: List

@dataclass
class FunctionDecl:
    name: str
    params: List
    body: List

@dataclass
class FunctionCall:
    name: str
    args: List

@dataclass
class ReturnStatement:
    value: Any

@dataclass
class PrintStatement:
    value: Any
