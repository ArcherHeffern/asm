from sys import argv
from dataclasses import dataclass
from pathlib import Path
from enum import Enum, auto

EXT_SUCCESS = 0
EXT_ERR_BAD_ARGUMENTS = 1
EXT_ERR_NOT_A_FILE = 2
EXT_ERR_SCAN_ERROR = 3 

ERROR = False

def error(msg: str):
    global ERROR
    ERROR = True
    print(msg)
    exit(EXT_ERR_SCAN_ERROR)


class TokenType(Enum):
    # Single character Tokens
    COMMA = auto()
    EQUALS = auto()
    RBRACET = auto()
    LBRACET = auto()
    AT = auto()
    DOLLAR = auto()

    # Literals 
    LITERAL = auto()
    NUMBER = auto()
    LABEL = auto()
    REGISTER = auto()

    # Keywords
    LOAD = auto()
    STORE = auto()

    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()

    HALT = auto()


REGISTER_SET = (
    "R1", "R2", "R3", "R4", "R5", "R6"
)

KEYWORDS = {
    "LOAD": TokenType.LOAD,
    "STORE": TokenType.STORE,
    "ADD": TokenType.ADD,
    "SUB": TokenType.SUB,
    "MUL": TokenType.MUL,
    "DIV": TokenType.DIV,
    "HALT": TokenType.HALT,
}

@dataclass
class Token:
    tokentype: TokenType
    lexeme: str
    literal: str|None 

    def __repr__(self):
        if self.literal is not None:
            return f"{self.tokentype.name}: {self.literal}"
        return f"{self.tokentype.name}"

class Scanner:
    def __init__(self, lines: list[str]):
        self.lines = lines
        self.line_number = 1

        self.line = None
        self.start = 0
        self.curr = 0
        self.tokens: list[Token] = []

    def scan(self) -> list[list[Token]]:
        lines: list[list[Token]] = []
        for line in self.lines:
            self.line = line
            self.scan_line()
            lines.append(self.tokens)
            self.start = 0
            self.curr = 0
            self.line_number += 1
            self.tokens = []
        return lines

    def __is_at_end(self):
        return self.curr >= len(self.line)

    def __advance(self):
        c = self.line[self.curr]
        self.curr += 1
        return c
    
    def __add_token(self, token: TokenType, literal: str|None = None):
        lex = Token(token, self.line[self.start: self.curr], literal)
        self.tokens.append(lex)
    
    def scan_line(self) -> list[Token]|None:
        while not self.__is_at_end():
            self.start = self.curr
            c = self.__advance()
            match c:
                case ",":
                    self.__add_token(TokenType.COMMA)
                case "=":
                    self.__add_token(TokenType.EQUALS)
                case "[":
                    self.__add_token(TokenType.LBRACET)
                case "]":
                    self.__add_token(TokenType.RBRACET)
                case "@":
                    self.__add_token(TokenType.AT)
                case "$":
                    self.__add_token(TokenType.DOLLAR)
                case " "|"\n"|"\t":
                    ...
                case _:
                    if c.isnumeric():
                        self.__number()
                    elif c.isalpha():
                        self.__identifier()
                    else: 
                        error("Lexeme not found")

    def __number(self):
        while self.__peek().isnumeric():
            self.__advance()
        number = int(self.line[self.start: self.curr])
        self.__add_token(TokenType.NUMBER, number)
        ...

    def __identifier(self):
        while self.__peek().isalnum():
            self.__advance()
        val = self.line[self.start: self.curr]
        if self.__peek() == ":":
            self.__advance()
            self.__add_token(TokenType.LABEL, val)
        else:
            self.__add_token(TokenType.LITERAL, val)

    def __peek(self) -> str:
        if self.__is_at_end():
            return "\0"
        return self.line[self.curr]
    
    def __peek_next(self) -> str:
        if self.curr + 1 >= len(self.line):
            return "\0"
        return self.line[self.curr + 1]
        

if len(argv) != 2:
    print("Usage: asm.py FILENAME")
    exit(EXT_ERR_BAD_ARGUMENTS)

filename = Path(argv[1])

if not filename.is_file():
    print(f"{filename} is not a file")
    exit(EXT_ERR_NOT_A_FILE)

with open(filename, "r") as f:
    lines = f.readlines()
    scanner = Scanner(lines)
    tokens = scanner.scan()
    print(tokens)
