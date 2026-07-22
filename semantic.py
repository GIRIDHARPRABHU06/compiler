from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

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


@dataclass
class Symbol:
    name: str
    var_type: str
    line: int
    scope_level: int
    is_array: bool = False
    size: int = 0


class SemanticAnalyzer:
    def __init__(self) -> None:
        self.scopes: List[Dict[str, Symbol]] = [{}]
        self.errors: List[str] = []
        self.symbols_flat: List[Symbol] = []

    def _push_scope(self) -> None:
        self.scopes.append({})

    def _pop_scope(self) -> None:
        self.scopes.pop()

    def _current_scope(self) -> Dict[str, Symbol]:
        return self.scopes[-1]

    def _scope_level(self) -> int:
        return len(self.scopes) - 1

    def _declare(self, sym: Symbol) -> None:
        cur = self._current_scope()
        if sym.name in cur:
            self.errors.append(f"Line {sym.line}: redeclaration of '{sym.name}'")
            return
        cur[sym.name] = sym
        self.symbols_flat.append(sym)

    def _lookup(self, name: str) -> Optional[Symbol]:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def analyze(self, program: Program) -> List[str]:
        for stmt in program.statements:
            self._visit_stmt(stmt)
        return self.errors

    def _visit_stmt(self, stmt) -> None:
        if isinstance(stmt, VarDecl):
            sym = Symbol(
                name=stmt.name,
                var_type=stmt.var_type,
                line=stmt.line,
                scope_level=self._scope_level(),
            )
            self._declare(sym)
            if stmt.initializer is not None:
                rhs_t = self._visit_expr(stmt.initializer)
                self._check_assignable(sym.var_type, rhs_t, stmt.line)
            return

        if isinstance(stmt, ArrayDecl):
            if stmt.size <= 0:
                self.errors.append(f"Line {stmt.line}: array '{stmt.name}' size must be > 0")
            sym = Symbol(
                name=stmt.name,
                var_type=stmt.var_type,
                line=stmt.line,
                scope_level=self._scope_level(),
                is_array=True,
                size=stmt.size,
            )
            self._declare(sym)
            return

        if isinstance(stmt, Assignment):
            target_t = self._visit_lvalue(stmt.target)
            rhs_t = self._visit_expr(stmt.value)
            self._check_assignable(target_t, rhs_t, stmt.line)
            return

        if isinstance(stmt, PrintStmt):
            self._visit_expr(stmt.value)
            return

        if isinstance(stmt, Block):
            self._push_scope()
            for inner in stmt.statements:
                self._visit_stmt(inner)
            self._pop_scope()
            return

        if isinstance(stmt, IfStmt):
            self._visit_expr(stmt.condition)
            self._visit_stmt(stmt.then_branch)
            if stmt.else_branch is not None:
                self._visit_stmt(stmt.else_branch)
            return

        if isinstance(stmt, WhileStmt):
            self._visit_expr(stmt.condition)
            self._visit_stmt(stmt.body)
            return

        if isinstance(stmt, ForStmt):
            self._push_scope()
            if stmt.init is not None:
                self._visit_stmt(stmt.init)
            if stmt.condition is not None:
                self._visit_expr(stmt.condition)
            if stmt.update is not None:
                self._visit_stmt(stmt.update)
            self._visit_stmt(stmt.body)
            self._pop_scope()
            return

        self.errors.append(f"Line {stmt.line}: unsupported statement type {type(stmt).__name__}")

    def _visit_lvalue(self, expr) -> str:
        if isinstance(expr, VarRef):
            sym = self._lookup(expr.name)
            if sym is None:
                self.errors.append(f"Line {expr.line}: undeclared variable '{expr.name}'")
                return "int"
            if sym.is_array:
                self.errors.append(f"Line {expr.line}: array '{expr.name}' requires an index")
            return sym.var_type

        if isinstance(expr, ArrayRef):
            sym = self._lookup(expr.name)
            if sym is None:
                self.errors.append(f"Line {expr.line}: undeclared array '{expr.name}'")
                return "int"
            if not sym.is_array:
                self.errors.append(f"Line {expr.line}: '{expr.name}' is not an array")
            idx_t = self._visit_expr(expr.index)
            if idx_t != "int":
                self.errors.append(f"Line {expr.line}: array index for '{expr.name}' must be int")
            if isinstance(expr.index, NumberLiteral) and expr.index.num_type == "int" and sym.is_array:
                idx = int(expr.index.value)
                if idx < 0 or idx >= sym.size:
                    self.errors.append(
                        f"Line {expr.line}: index {idx} out of bounds for '{expr.name}[0..{sym.size - 1}]'"
                    )
            return sym.var_type

        self.errors.append(f"Line {expr.line}: invalid assignment target")
        return "int"

    def _visit_expr(self, expr: Expr) -> str:
        if isinstance(expr, NumberLiteral):
            return expr.num_type

        if isinstance(expr, VarRef):
            return self._visit_lvalue(expr)

        if isinstance(expr, ArrayRef):
            return self._visit_lvalue(expr)

        if isinstance(expr, UnaryOp):
            operand_t = self._visit_expr(expr.operand)
            if operand_t not in {"int", "float"}:
                self.errors.append(f"Line {expr.line}: unary operator '{expr.op}' requires numeric operand")
            return operand_t

        if isinstance(expr, BinaryOp):
            left_t = self._visit_expr(expr.left)
            right_t = self._visit_expr(expr.right)
            if expr.op in {"+", "-", "*", "/"}:
                if left_t not in {"int", "float"} or right_t not in {"int", "float"}:
                    self.errors.append(f"Line {expr.line}: arithmetic operator '{expr.op}' requires numeric operands")
                    return "int"
                return "float" if "float" in {left_t, right_t} else "int"
            if expr.op in {"<", "<=", ">", ">=", "==", "!="}:
                if left_t not in {"int", "float"} or right_t not in {"int", "float"}:
                    self.errors.append(f"Line {expr.line}: relational operator '{expr.op}' requires numeric operands")
                return "int"
            self.errors.append(f"Line {expr.line}: unsupported binary operator '{expr.op}'")
            return "int"

        self.errors.append(f"Line {expr.line}: unsupported expression type {type(expr).__name__}")
        return "int"

    def _check_assignable(self, lhs_type: str, rhs_type: str, line: int) -> None:
        if lhs_type == rhs_type:
            return
        if lhs_type == "float" and rhs_type == "int":
            return
        self.errors.append(f"Line {line}: cannot assign {rhs_type} to {lhs_type}")

    def format_symbol_table(self) -> str:
        lines = [
            "Name       Type   Scope   Kind   Size",
            "--------------------------------------",
        ]
        for sym in self.symbols_flat:
            kind = "array" if sym.is_array else "var"
            size = str(sym.size) if sym.is_array else "-"
            lines.append(
                f"{sym.name:<10} {sym.var_type:<6} {sym.scope_level:<7} {kind:<6} {size}"
            )
        return "\n".join(lines)
