from __future__ import annotations

from dataclasses import dataclass
from typing import List


KEYWORDS = {
    "int": "INT",
    "float": "FLOAT",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "for": "FOR",
    "print": "PRINT",
}

MULTI_CHAR_OPERATORS = {
    "<=": "LE",
    ">=": "GE",
    "==": "EQ",
    "!=": "NE",
}

SINGLE_CHAR_TOKENS = {
    "+": "PLUS",
    "-": "MINUS",
    "*": "STAR",
    "/": "SLASH",
    "<": "LT",
    ">": "GT",
    "=": "ASSIGN",
    "(": "LPAREN",
    ")": "RPAREN",
    "{": "LBRACE",
    "}": "RBRACE",
    "[": "LBRACKET",
    "]": "RBRACKET",
    ";": "SEMICOLON",
    ",": "COMMA",
}


@dataclass
class Token:
    token_type: str
    value: str
    line: int
    column: int


class LexerError(Exception):
    pass


class Lexer:
    def __init__(self, source: str) -> None:
        self.source = source
        self.length = len(source)
        self.index = 0
        self.line = 1
        self.column = 1

    def _peek(self, k: int = 0) -> str:
        pos = self.index + k
        if pos >= self.length:
            return ""
        return self.source[pos]

    def _advance(self) -> str:
        ch = self._peek()
        if not ch:
            return ""
        self.index += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def _match(self, expected: str) -> bool:
        if self._peek() == expected:
            self._advance()
            return True
        return False

    def _skip_whitespace_and_comments(self) -> None:
        while True:
            ch = self._peek()
            if ch in {" ", "\t", "\r", "\n"}:
                self._advance()
                continue
            if ch == "/" and self._peek(1) == "/":
                while self._peek() not in {"", "\n"}:
                    self._advance()
                continue
            if ch == "/" and self._peek(1) == "*":
                self._advance()
                self._advance()
                while True:
                    if self._peek() == "":
                        raise LexerError(f"Unterminated block comment at line {self.line}")
                    if self._peek() == "*" and self._peek(1) == "/":
                        self._advance()
                        self._advance()
                        break
                    self._advance()
                continue
            break

    def _scan_number(self) -> Token:
        start_line = self.line
        start_col = self.column
        start = self.index

        while self._peek().isdigit():
            self._advance()

        is_float = False
        if self._peek() == "." and self._peek(1).isdigit():
            is_float = True
            self._advance()
            while self._peek().isdigit():
                self._advance()

        text = self.source[start:self.index]
        return Token("FLOAT_LITERAL" if is_float else "INT_LITERAL", text, start_line, start_col)

    def _scan_identifier_or_keyword(self) -> Token:
        start_line = self.line
        start_col = self.column
        start = self.index

        while self._peek().isalnum() or self._peek() == "_":
            self._advance()

        text = self.source[start:self.index]
        token_type = KEYWORDS.get(text, "IDENTIFIER")
        return Token(token_type, text, start_line, start_col)

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []

        while self.index < self.length:
            self._skip_whitespace_and_comments()
            if self.index >= self.length:
                break

            line = self.line
            col = self.column
            ch = self._peek()
            two = ch + self._peek(1)

            if ch.isdigit():
                tokens.append(self._scan_number())
                continue

            if ch.isalpha() or ch == "_":
                tokens.append(self._scan_identifier_or_keyword())
                continue

            if two in MULTI_CHAR_OPERATORS:
                self._advance()
                self._advance()
                tokens.append(Token(MULTI_CHAR_OPERATORS[two], two, line, col))
                continue

            if ch in SINGLE_CHAR_TOKENS:
                self._advance()
                tokens.append(Token(SINGLE_CHAR_TOKENS[ch], ch, line, col))
                continue

            raise LexerError(f"Unexpected character '{ch}' at line {line}, col {col}")

        tokens.append(Token("EOF", "", self.line, self.column))
        return tokens
