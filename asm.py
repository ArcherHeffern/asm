from sys import argv
from typing import Iterable, NewType, Callable
from dataclasses import dataclass
from pathlib import Path
from enum import Enum, auto

"""
TODO: 
- ALlow for multiple register sets
- Feature to add line numbers
- MMU to translate addresses
- History feature - go back in time
"""

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

    PRINT = auto()


KEYWORDS = {
    "LOAD": TokenType.LOAD,
    "STORE": TokenType.STORE,
    "ADD": TokenType.ADD,
    "SUB": TokenType.SUB,
    "MUL": TokenType.MUL,
    "DIV": TokenType.DIV,
    "HALT": TokenType.HALT,
    "PRINT": TokenType.PRINT,
}


@dataclass
class Memory:
    addresses: list[list[str]]
    starting_address: int
    parser: 'Parser'
    scanner: 'Scanner'

    registers = {
        "R1": 0, 
        "R2": 1, 
        "R3": 2, 
        "R4": 3, 
        "R5": 4, 
        "R6": 5,
    }

    status_registers = {
        "ip": 0
    }

    def __get_instruction(self):
        return self.addresses[self.__mmu(self.status_registers["ip"])]

    def fde_cycle(self):
        while (True):
            instruction = self.__get_instruction()
            tokens = self.scanner.scan_line(instruction)
            ast = self.parser(tokens)
            ast()
            self.status_registers["ip"] += 1

    def get_register(self, register: str):
        return self.REGISTERS[register]

    def set_register(self, register: str, value: int):
        self.REGISTERS[register] = value

    def __mmu(self, address):
        return address - self.starting_address

    def get_val(self, address: int):
        return self.addresses[self.__mmu(address)]

    def set_val(self, address: int, value: str):
        self.addresses[self.__mmu(address)] = value

@dataclass
class Token:
    tokentype: TokenType
    lexeme: str
    literal: str|None 
    line_number: int

    def __repr__(self):
        if self.literal is not None:
            return f"{self.tokentype.name}: {self.literal}"
        return f"{self.tokentype.name}"

class Scanner:
    def __init__(self, lines: list[str]):
        self.lines = lines

    
    def scan_line(self, line_number: int, memory: Memory) -> list[Token]|None:
        # Actual Line Number no MMU
        self.start = 0
        self.curr = 0
        self.line_number = line_number
        self.line = memory.get_val(line_number)
        self.tokens = []

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
                        self.__identifier(memory)
                    else: 
                        error("Lexeme not found")
        return self.tokens

    def __is_at_end(self):
        return self.curr >= len(self.line)

    def __advance(self):
        c = self.line[self.curr]
        self.curr += 1
        return c
    
    def __add_token(self, token: TokenType, literal: str|None = None):
        lex = Token(token, self.line[self.start: self.curr], literal, self.line_number)
        self.tokens.append(lex)

    def __number(self):
        while self.__peek().isnumeric():
            self.__advance()
        number = int(self.line[self.start: self.curr])
        self.__add_token(TokenType.NUMBER, number)
        ...

    def __identifier(self, memory: Memory):
        while self.__peek().isalnum():
            self.__advance()
        val = self.line[self.start: self.curr]
        if self.__peek() == ":":
            self.__advance()
            self.__add_token(TokenType.LABEL, val)
        else:
            token_type = None
            if val in KEYWORDS:
                token_type = KEYWORDS[val]
            elif val in memory.registers:
                token_type = TokenType.REGISTER
            else:
                token_type = TokenType.LITERAL
            self.__add_token(token_type, val)

    def __peek(self) -> str:
        if self.__is_at_end():
            return "\0"
        return self.line[self.curr]

class Parser:
    def __init__(self, memory: Memory):
        self.memory = memory
    
    def __parse_statement(self, tokens) -> Callable:
        self.tokens = tokens
        self.current = 0

        curr = self.__peek()
        match curr.tokentype:
            case TokenType.LOAD:
                statement = self.__parse_load_statement()
            case TokenType.STORE:
                statement = self.__parse_store_statement()
            case TokenType.ADD:
                statement = self.__parse_add_statement()
            case TokenType.SUB:
                statement = self.__parse_sub_statement()
            case TokenType.MUL:
                statement = self.__parse_mul_statement()
            case TokenType.DIV:
                statement = self.__parse_div_statement()
            case TokenType.HALT:
                statement = self.__parse_halt_statement()
            case TokenType.PRINT:
                statement = self.__parse_print_statement()
            case _:
                raise Exception(f"Token {curr} handled while scanning")
        return statement

    def __parse_load_statement(self):
        self.__match(TokenType.LOAD)
        self.__match(TokenType.REGISTER)
        register = self.__previous()
        self.__match(TokenType.COMMA)
        value_at = self.__parse_load_addr_types()
        def lambda_():
            self.memory.registers[register.lexeme] = value_at
        return lambda_
        ...
    
    def __parse_load_addr_types(self):
        # TODO: How to handle if there are many possibilities: Eg. All the addressing types
        # Returns a function returning the actual value - will need to calculate on the fly
        # This one doesn't call the function because its more of a logic thingy
        curr = self.__peek()
        match curr:
            case TokenType.NUMBER:
                func = self.__parse_direct_addr()
            case TokenType.EQUALS:
                func = self.__parse_immediate_addr()
            case TokenType.LBRACET:
                func = self.__parse_index_addr()
            case TokenType.AT:
                func = self.__parse_index_addr()
            case TokenType.DOLLAR:
                func = self.__parse_relative_addr()
            case _:
                raise Exception("Error parsing load addr")
        return func
        ...

    def __parse_store_statement(self):
        ...
    def __parse_add_statement(self):
        ...
    def __parse_sub_statement(self):
        ...
    def __parse_mul_statement(self):
        ...
    def __parse_div_statement(self):
        ...
    def __parse_halt_statement(self):
        ...
    def __parse_print_statement(self):
        ...


    def __parse_direct_addr(self):
        number = self.__match(TokenType.NUMBER).literal
        def lambda_():
            return self.memory.get_val(number)
        return lambda_
    
    def __parse_immediate_addr(self):
        self.__match(TokenType.EQUALS)
        number = self.__match(TokenType.NUMBER).literal
        def lambda_():
            return number
        return lambda_

    def __parse_index_addr(self):
        self.__match(TokenType.LBRACET)
        if not (num := self.__match(TokenType.NUMBER)):
            raise Exception("Index addressing expected number")
        if not self.__match(TokenType.COMMA):
            raise Exception("Index addressing expected comma")
        if not (register := self.__match(TokenType.REGISTER)):
            raise Exception("Index addressing expected register")
        def lambda_():
            return self.memory[num + self.memory.registers[register.lexeme]]
        return lambda_

    def __parse_indirect_addr(self):
        ...

    def __parse_relative_addr(self):
        ...

    
    def __previous(self) -> Token:
        return self.tokens[self.current - 1]

    def __advance(self) -> Token:
        self.current += 1
        return self.__previous()        

    def __peek(self) -> TokenType:
        if self.__is_at_end():
            return "\0"
        return self.tokens[self.current]
    
    def __check(self, token: TokenType) -> bool:
        return self.__peek() == token
    
    def __match(self, tokens: Iterable[TokenType]) -> Token|None:
        for token in tokens:
            if self.__check(token):
                return self.__advance()
        return None


    def __is_at_end(self):
        return self.current >= len(self.tokens)
        

if len(argv) != 2:
    print("Usage: asm.py FILENAME")
    exit(EXT_ERR_BAD_ARGUMENTS)

filename = Path(argv[1])

if not filename.is_file():
    print(f"{filename} is not a file")
    exit(EXT_ERR_NOT_A_FILE)

with open(filename, "r") as f:
    lines = f.readlines()
    tokens = Scanner(lines).scan()
    ast = Parser(tokens).parse()


    # Virtual Machine
    registers = [0] * len(REGISTERS)
    ip = 0
    memory_address = 0
    for token_list in tokens:
        if len(token_list) == 0:
            continue
        match token_list[0]:
            case TokenType.LOAD:
                




