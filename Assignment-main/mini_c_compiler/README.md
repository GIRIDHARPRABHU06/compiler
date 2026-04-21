# Mini-C Compiler (Dependency-Free Python)

This project implements a simple Mini-C compiler pipeline for a compiler design assignment.

## Features

- Lexical analysis (tokens for keywords, identifiers, literals, operators, delimiters)
- Syntax analysis using a recursive descent parser
- AST generation
- Semantic analysis:
  - Redeclaration checks
  - Undeclared variable checks
  - Type mismatch checks (`int` vs `float`)
  - Array usage and static bounds checks for literal indices
- IR generation as Three-Address Code (TAC)

## Project Files

- `ast_nodes.py`: AST node definitions
- `lexer.py`: Lexer implementation
- `parser.py`: Parser + AST construction
- `semantic.py`: Symbol table + semantic checks
- `ir_gen.py`: TAC generation
- `main.py`: Pipeline entry point
- `test_program.mc`: Valid Mini-C sample
- `test_errors.mc`: Invalid Mini-C sample (semantic errors)

## Run

From this folder:

```powershell
python main.py test_program.mc --tokens --ast --symbols --tac output.tac
```

Expected behavior:

- Prints tokens, AST, symbol table, and TAC
- Writes TAC to `output.tac`

Test error handling:

```powershell
python main.py test_errors.mc --symbols
```

Expected behavior:

- Prints symbol table
- Reports semantic errors with line numbers

## Supported Mini-C Constructs

- Variable declarations: `int x;`, `float y = 1.5;`
- Array declarations: `int arr[10];`
- Assignments: `x = 3 + y;`, `arr[i] = x;`
- Control flow: `if-else`, `while`, `for`
- Printing: `print(expr);`
- Arithmetic and relational operators
