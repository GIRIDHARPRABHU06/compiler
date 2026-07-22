# Mini-C Compiler

A Mini-C Compiler developed in **Python** using **PLY (Python Lex-Yacc)**.

This project implements the major phases of a compiler for a subset of the C programming language.

## Features

- Lexical Analysis
- Syntax Analysis
- Semantic Analysis
- Abstract Syntax Tree (AST)
- Three-Address Code (TAC) Generation
- Error Detection and Reporting

## Technologies Used

- Python
- PLY (Python Lex-Yacc)

## Project Structure

```text
mini_c_compiler/
│
├── lexer.py
├── parser.py
├── semantic.py
├── ast_nodes.py
├── ir_gen.py
├── main.py
├── output.tac
└── README.md
```

## Supported Mini-C Features

- Variable Declarations (`int`, `float`)
- Arithmetic Expressions
- Relational Operators
- One-dimensional Arrays
- `if-else`
- `while`
- `for`
- `print()` Function

## Run

```bash
python main.py
```

## Output

The compiler generates:

- Tokens
- Parse Tree / AST
- Semantic Validation
- Three-Address Code (TAC)

## License

Developed as an academic compiler design project.
