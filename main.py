run from __future__ import annotations
import argparse
import json
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from ir_gen import IRGenerator
from lexer import Lexer, LexerError
from parser import Parser, ParserError
from semantic import SemanticAnalyzer


def ast_to_dict(node: Any) -> Any:
    if is_dataclass(node):
        data = asdict(node)
        return {k: ast_to_dict(v) for k, v in data.items()}
    if isinstance(node, list):
        return [ast_to_dict(item) for item in node]
    return node


def main() -> int:
    parser = argparse.ArgumentParser(description="Mini-C compiler frontend + TAC generator")
    parser.add_argument("source", help="Path to Mini-C source file")
    parser.add_argument("--tokens", action="store_true", help="Print token stream")
    parser.add_argument("--ast", action="store_true", help="Print AST as JSON")
    parser.add_argument("--symbols", action="store_true", help="Print symbol table")
    parser.add_argument("--tac", default="output.tac", help="TAC output file path")
    args = parser.parse_args()

    source_path = Path(args.source)
    if not source_path.exists():
        print(f"Error: source file not found: {source_path}")
        return 1

    source_text = source_path.read_text(encoding="utf-8")

    try:
        tokens = Lexer(source_text).tokenize()
    except LexerError as exc:
        print(f"Lexer error: {exc}")
        return 1

    if args.tokens:
        print("Token Stream:")
        for tok in tokens:
            print(f"{tok.token_type:<13} {tok.value!r:<12} line={tok.line}, col={tok.column}")
        print()

    try:
        program = Parser(tokens).parse()
    except ParserError as exc:
        print(f"Parser error: {exc}")
        return 1

    if args.ast:
        print("AST:")
        print(json.dumps(ast_to_dict(program), indent=2))
        print()

    semantic = SemanticAnalyzer()
    errors = semantic.analyze(program)
    if args.symbols:
        print("Symbol Table:")
        print(semantic.format_symbol_table())
        print()

    if errors:
        print("Semantic Errors:")
        for err in errors:
            print(f"- {err}")
        return 1

    ir = IRGenerator()
    instructions = ir.generate(program)

    print("Three-Address Code:")
    for line in instructions:
        print(line)

    tac_path = Path(args.tac)
    tac_path.write_text("\n".join(instructions) + "\n", encoding="utf-8")
    print(f"\nTAC written to: {tac_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
