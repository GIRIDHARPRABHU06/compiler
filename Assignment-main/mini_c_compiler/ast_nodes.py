from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Union


@dataclass
class Node:
    line: int


@dataclass
class Program(Node):
    statements: List[Stmt]


class Stmt(Node):
    pass


class Expr(Node):
    pass


@dataclass
class Block(Stmt):
    statements: List[Stmt]


@dataclass
class VarDecl(Stmt):
    var_type: str
    name: str
    initializer: Optional[Expr] = None


@dataclass
class ArrayDecl(Stmt):
    var_type: str
    name: str
    size: int = 0


@dataclass
class Assignment(Stmt):
    target: LValue
    value: Expr


@dataclass
class PrintStmt(Stmt):
    value: Expr


@dataclass
class IfStmt(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Optional[Stmt] = None


@dataclass
class WhileStmt(Stmt):
    condition: Expr
    body: Stmt


@dataclass
class ForStmt(Stmt):
    init: Optional[Union[VarDecl, Assignment]]
    condition: Optional[Expr]
    update: Optional[Assignment]
    body: Stmt


@dataclass
class Identifier(Expr):
    name: str


@dataclass
class NumberLiteral(Expr):
    value: Union[int, float]
    num_type: str


class LValue(Expr):
    pass


@dataclass
class VarRef(LValue):
    name: str


@dataclass
class ArrayRef(LValue):
    name: str
    index: Expr


@dataclass
class BinaryOp(Expr):
    op: str
    left: Expr
    right: Expr


@dataclass
class UnaryOp(Expr):
    op: str
    operand: Expr
