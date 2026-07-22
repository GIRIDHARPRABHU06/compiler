from __future__ import annotations

from typing import List, Optional, Union

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
    Stmt,
    UnaryOp,
    VarDecl,
    VarRef,
    WhileStmt,
)
from lexer import Token


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.current = 0

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _is_at_end(self) -> bool:
        return self._peek().token_type == "EOF"

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _check(self, *token_types: str) -> bool:
        if self._is_at_end():
            return False
        return self._peek().token_type in token_types

    def _match(self, *token_types: str) -> bool:
        if self._check(*token_types):
            self._advance()
            return True
        return False

    def _consume(self, token_type: str, message: str) -> Token:
        if self._check(token_type):
            return self._advance()
        tok = self._peek()
        raise ParserError(f"{message} at line {tok.line}, col {tok.column}")

    def parse(self) -> Program:
        statements: List[Stmt] = []
        while not self._is_at_end():
            statements.append(self._statement())
        return Program(line=1, statements=statements)

    def _statement(self) -> Stmt:
        if self._match("INT", "FLOAT"):
            return self._declaration(self._previous())
        if self._match("IF"):
            return self._if_statement(self._previous().line)
        if self._match("WHILE"):
            return self._while_statement(self._previous().line)
        if self._match("FOR"):
            return self._for_statement(self._previous().line)
        if self._match("PRINT"):
            return self._print_statement(self._previous().line)
        if self._match("LBRACE"):
            return self._block(self._previous().line)
        return self._assignment_statement()

    def _block(self, line: int) -> Block:
        statements: List[Stmt] = []
        while not self._check("RBRACE") and not self._is_at_end():
            statements.append(self._statement())
        self._consume("RBRACE", "Expected '}' after block")
        return Block(line=line, statements=statements)

    def _declaration(self, type_token: Token) -> Union[VarDecl, ArrayDecl]:
        name_token = self._consume("IDENTIFIER", "Expected identifier after type")
        var_type = type_token.value

        if self._match("LBRACKET"):
            size_token = self._consume("INT_LITERAL", "Expected integer array size")
            self._consume("RBRACKET", "Expected ']' after array size")
            self._consume("SEMICOLON", "Expected ';' after array declaration")
            return ArrayDecl(
                line=type_token.line,
                var_type=var_type,
                name=name_token.value,
                size=int(size_token.value),
            )

        initializer: Optional[Expr] = None
        if self._match("ASSIGN"):
            initializer = self._expression()

        self._consume("SEMICOLON", "Expected ';' after declaration")
        return VarDecl(
            line=type_token.line,
            var_type=var_type,
            name=name_token.value,
            initializer=initializer,
        )

    def _print_statement(self, line: int) -> PrintStmt:
        self._consume("LPAREN", "Expected '(' after print")
        value = self._expression()
        self._consume("RPAREN", "Expected ')' after print value")
        self._consume("SEMICOLON", "Expected ';' after print statement")
        return PrintStmt(line=line, value=value)

    def _if_statement(self, line: int) -> IfStmt:
        self._consume("LPAREN", "Expected '(' after if")
        condition = self._expression()
        self._consume("RPAREN", "Expected ')' after if condition")
        then_branch = self._statement()
        else_branch = self._statement() if self._match("ELSE") else None
        return IfStmt(line=line, condition=condition, then_branch=then_branch, else_branch=else_branch)

    def _while_statement(self, line: int) -> WhileStmt:
        self._consume("LPAREN", "Expected '(' after while")
        condition = self._expression()
        self._consume("RPAREN", "Expected ')' after while condition")
        body = self._statement()
        return WhileStmt(line=line, condition=condition, body=body)

    def _for_statement(self, line: int) -> ForStmt:
        self._consume("LPAREN", "Expected '(' after for")

        init: Optional[Union[VarDecl, Assignment]] = None
        if self._match("INT", "FLOAT"):
            init = self._declaration_fragment(self._previous())
        elif not self._check("SEMICOLON"):
            init = self._assignment_fragment()
        self._consume("SEMICOLON", "Expected ';' after for init")

        condition: Optional[Expr] = None
        if not self._check("SEMICOLON"):
            condition = self._expression()
        self._consume("SEMICOLON", "Expected ';' after for condition")

        update: Optional[Assignment] = None
        if not self._check("RPAREN"):
            update = self._assignment_fragment()
        self._consume("RPAREN", "Expected ')' after for clauses")

        body = self._statement()
        return ForStmt(line=line, init=init, condition=condition, update=update, body=body)

    def _declaration_fragment(self, type_token: Token) -> VarDecl:
        name_token = self._consume("IDENTIFIER", "Expected identifier in for declaration")
        initializer: Optional[Expr] = None
        if self._match("ASSIGN"):
            initializer = self._expression()
        return VarDecl(
            line=type_token.line,
            var_type=type_token.value,
            name=name_token.value,
            initializer=initializer,
        )

    def _assignment_statement(self) -> Assignment:
        assignment = self._assignment_fragment()
        self._consume("SEMICOLON", "Expected ';' after assignment")
        return assignment

    def _assignment_fragment(self) -> Assignment:
        target = self._lvalue()
        eq = self._consume("ASSIGN", "Expected '=' in assignment")
        value = self._expression()
        return Assignment(line=eq.line, target=target, value=value)

    def _lvalue(self) -> Union[VarRef, ArrayRef]:
        ident = self._consume("IDENTIFIER", "Expected identifier")
        if self._match("LBRACKET"):
            index_expr = self._expression()
            self._consume("RBRACKET", "Expected ']' after index")
            return ArrayRef(line=ident.line, name=ident.value, index=index_expr)
        return VarRef(line=ident.line, name=ident.value)

    def _expression(self) -> Expr:
        return self._equality()

    def _equality(self) -> Expr:
        expr = self._comparison()
        while self._match("EQ", "NE"):
            op = self._previous().value
            right = self._comparison()
            expr = BinaryOp(line=self._previous().line, op=op, left=expr, right=right)
        return expr

    def _comparison(self) -> Expr:
        expr = self._term()
        while self._match("LT", "LE", "GT", "GE"):
            op = self._previous().value
            right = self._term()
            expr = BinaryOp(line=self._previous().line, op=op, left=expr, right=right)
        return expr

    def _term(self) -> Expr:
        expr = self._factor()
        while self._match("PLUS", "MINUS"):
            op = self._previous().value
            right = self._factor()
            expr = BinaryOp(line=self._previous().line, op=op, left=expr, right=right)
        return expr

    def _factor(self) -> Expr:
        expr = self._unary()
        while self._match("STAR", "SLASH"):
            op = self._previous().value
            right = self._unary()
            expr = BinaryOp(line=self._previous().line, op=op, left=expr, right=right)
        return expr

    def _unary(self) -> Expr:
        if self._match("MINUS"):
            op = self._previous()
            right = self._unary()
            return UnaryOp(line=op.line, op=op.value, operand=right)
        return self._primary()

    def _primary(self) -> Expr:
        if self._match("INT_LITERAL"):
            tok = self._previous()
            return NumberLiteral(line=tok.line, value=int(tok.value), num_type="int")
        if self._match("FLOAT_LITERAL"):
            tok = self._previous()
            return NumberLiteral(line=tok.line, value=float(tok.value), num_type="float")
        if self._match("IDENTIFIER"):
            ident = self._previous()
            if self._match("LBRACKET"):
                idx = self._expression()
                self._consume("RBRACKET", "Expected ']' after array index")
                return ArrayRef(line=ident.line, name=ident.value, index=idx)
            return VarRef(line=ident.line, name=ident.value)
        if self._match("LPAREN"):
            expr = self._expression()
            self._consume("RPAREN", "Expected ')' after expression")
            return expr

        tok = self._peek()
        raise ParserError(f"Unexpected token {tok.token_type} at line {tok.line}, col {tok.column}")
