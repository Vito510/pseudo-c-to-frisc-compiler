# FRISC-C Compiler

A **compiler that translates C code into FRISC (FER RISC) assembly**, built for **educational and experimental use**.  
It demonstrates all major stages of compilation — from **lexing** to **assembly generation** — for learning and experimentation.

## Compiler Phases

### 1. Lexical Analysis
- Converts C source code into tokens
- Identifies keywords, identifiers, literals, and operators
- Removes whitespace and comments

### 2. Syntax Analysis  
- Parses tokens into Abstract Syntax Tree (AST)
- Validates program structure against C grammar
- Handles expressions, statements, and function definitions

### 3. Semantic Analysis
- Performs type checking and validation
- Manages symbol tables and scopes
- Verifies function calls and variable usage

### 4. Intermediate Code Generation
- Produces Three-Address Code (TAC) representation
- Platform-independent intermediate form
- Enables basic optimizations

### 5. Code Generation
- Translates intermediate code to FRISC assembly
- Handles register allocation and memory management
- Generates executable FRISC instructions

## Example
Input:
```c
int main() {
  int a = 3, b = 4;
  return a + b;
}
```
Output:
```frisc
MOVE 3, R1
MOVE 4, R2
ADD R1, R2, R0
RET
```

## Usage
```bash
python ./frisc-compiler < c-code.txt
```
