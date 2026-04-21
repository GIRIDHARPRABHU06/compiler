from __future__ import annotations

from typing import List

from ast_nodes import (
    ArrayDecl,
    ArrayRef,
    Assignment,
    BinaryOp,
    Block,
    Expr,
    ForStmt,
    IfStmt,
    NumberLiteral,
    PrintStmt,
    Program,
    UnaryOp,
    VarDecl,
    VarRef,
    WhileStmt,
)


class IRGenerator:
    def __init__(self) -> None:
        self.instructions: List[str] = []
        self.temp_count = 0
        self.label_count = 0

    def _new_temp(self) -> str:
        self.temp_count += 1
        return f"t{self.temp_count}"

    def _new_label(self) -> str:
        self.label_count += 1
        return f"L{self.label_count}"

    def _emit(self, code: str) -> None:
        self.instructions.append(code)

    def generate(self, program: Program) -> List[str]:
        self.instructions.clear()
        self.temp_count = 0
        self.label_count = 0

        for stmt in program.statements:
            self._gen_stmt(stmt)
        return self.instructions

    def _gen_stmt(self, stmt) -> None:
        if isinstance(stmt, VarDecl):
            if stmt.initializer is not None:
                rhs = self._gen_expr(stmt.initializer)
                self._emit(f"{stmt.name} = {rhs}")
            return

        if isinstance(stmt, ArrayDecl):
            self._emit(f"decl {stmt.name}[{stmt.size}]")
            return

        if isinstance(stmt, Assignment):
            rhs = self._gen_expr(stmt.value)
            lhs = self._gen_lvalue(stmt.target)
            self._emit(f"{lhs} = {rhs}")
            return

        if isinstance(stmt, PrintStmt):
            value = self._gen_expr(stmt.value)
            self._emit(f"print {value}")
            return

        if isinstance(stmt, Block):
            for inner in stmt.statements:
                self._gen_stmt(inner)
            return

        if isinstance(stmt, IfStmt):
            cond = self._gen_expr(stmt.condition)
            else_label = self._new_label()
            end_label = self._new_label()
            self._emit(f"ifFalse {cond} goto {else_label}")
            self._gen_stmt(stmt.then_branch)
            self._emit(f"goto {end_label}")
            self._emit(f"{else_label}:")
            if stmt.else_branch is not None:
                self._gen_stmt(stmt.else_branch)
            self._emit(f"{end_label}:")
            return

        if isinstance(stmt, WhileStmt):
            start_label = self._new_label()
            end_label = self._new_label()
            self._emit(f"{start_label}:")
            cond = self._gen_expr(stmt.condition)
            self._emit(f"ifFalse {cond} goto {end_label}")
            self._gen_stmt(stmt.body)
            self._emit(f"goto {start_label}")
            self._emit(f"{end_label}:")
            return

        if isinstance(stmt, ForStmt):
            start_label = self._new_label()
            end_label = self._new_label()
            if stmt.init is not None:
                self._gen_stmt(stmt.init)
            self._emit(f"{start_label}:")
            if stmt.condition is not None:
                cond = self._gen_expr(stmt.condition)
                self._emit(f"ifFalse {cond} goto {end_label}")
            self._gen_stmt(stmt.body)
            if stmt.update is not None:
                self._gen_stmt(stmt.update)
            self._emit(f"goto {start_label}")
            self._emit(f"{end_label}:")
            return

        raise ValueError(f"Unsupported statement node: {type(stmt).__name__}")

    def _gen_lvalue(self, expr) -> str:
        if isinstance(expr, VarRef):
            return expr.name
        if isinstance(expr, ArrayRef):
            idx = self._gen_expr(expr.index)
            return f"{expr.name}[{idx}]"
        raise ValueError(f"Unsupported lvalue node: {type(expr).__name__}")

    def _gen_expr(self, expr: Expr) -> str:
        if isinstance(expr, NumberLiteral):
            return str(expr.value)

        if isinstance(expr, VarRef):
            return expr.name

        if isinstance(expr, ArrayRef):
            idx = self._gen_expr(expr.index)
            t = self._new_temp()
            self._emit(f"{t} = {expr.name}[{idx}]")
            return t

        if isinstance(expr, UnaryOp):
            operand = self._gen_expr(expr.operand)
            t = self._new_temp()
            self._emit(f"{t} = {expr.op}{operand}")
            return t

        if isinstance(expr, BinaryOp):
            left = self._gen_expr(expr.left)
            right = self._gen_expr(expr.right)
            t = self._new_temp()
            self._emit(f"{t} = {left} {expr.op} {right}")
            return t

        raise ValueError(f"Unsupported expression node: {type(expr).__name__}")
