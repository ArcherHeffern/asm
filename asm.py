from sys import argv
from typing import Iterable, NewType, Callable
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum, auto

DEBUG = False

"""
TODO: 
- ALlow for multiple register sets
- Feature to add line numbers
- MMU to translate addresses
- History feature - go back in time
- Program to insert line numbers

Next Version
- Assembler
- All memory is integers
- Meta compiler: Use dictionaries to store rules
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
	INC = auto()

	HALT = auto()
	SKIP = auto()

	PRINT = auto()
	DUMP = auto()

	EOF = auto()
	EOL = auto()


KEYWORDS = {
	"LOAD": TokenType.LOAD,
	"STORE": TokenType.STORE,
	"ADD": TokenType.ADD,
	"SUB": TokenType.SUB,
	"MUL": TokenType.MUL,
	"DIV": TokenType.DIV,
	"INC": TokenType.INC,
	"HALT": TokenType.HALT,
	"SKIP": TokenType.SKIP,
	"PRINT": TokenType.PRINT,
	"DUMP": TokenType.DUMP,
}


@dataclass
class Memory:
	registers = {
		"R1": 0, 
		"R2": 0, 
		"R3": 0, 
		"R4": 0, 
		"R5": 0, 
		"R6": 0,
	}

	status_registers = {
		"ip": 0
	}

	starting_address: int = 0

	def load(self, lines: list[str], size: int = 100):
		self.addresses = [0] * size
		for i, line in enumerate(lines):
			self.addresses[i+self.starting_address] = line.strip()
			

	def fde_cycle(self, scanner: 'Scanner', parser: 'Parser'):
		while True:
			instruction = self.fetch()
			ast = self.decode(instruction, scanner, parser)
			if ast is None: # halt flag or error parsing halt flag
				break
			self.execute(ast)
			self.status_registers["ip"] += 1 

	def fetch(self):
		return self.addresses[self.__mmu(self.status_registers["ip"])]

	def decode(self, instruction, scanner: 'Scanner', parser: 'Parser'):
		tokens = scanner.scan_line(instruction)
		ast = parser.parse(tokens)
		return ast

	def execute(self, ast):
		return ast()

	def __get_register(self, register: str):
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
	literal: str|int|None 

	def __repr__(self):
		if self.literal is not None:
			return f"{self.tokentype.name}: {self.literal}"
		return f"{self.tokentype.name}"

class Scanner:
	def __init__(self, memory: Memory, lines: list[str]):
		self.memory = memory

	
	def scan_line(self, instruction) -> list[Token]|None:
		# Actual Line Number no MMU
		self.start = 0
		self.curr = 0
		self.line = instruction
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
				case "#":
					break
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
		lex = Token(token, self.line[self.start: self.curr], literal)
		self.tokens.append(lex)

	def __number(self):
		while not self.__is_at_end() and self.__peek().isnumeric():
			self.__advance()
		number = int(self.line[self.start: self.curr])
		self.__add_token(TokenType.NUMBER, number)
		...

	def __identifier(self, memory: Memory):
		while not self.__is_at_end() and self.__peek().isalnum():
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
			return Token(TokenType.EOF, "", "")	
		return self.line[self.curr]

class Parser:
	def __init__(self, memory: Memory):
		self.memory = memory
	
	def parse(self, tokens) -> Callable|None:
		if DEBUG:
			print(tokens)
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
			case TokenType.INC:
				statement = self.__parse_inc_statement()
			case TokenType.HALT:
				statement = self.__parse_halt_statement()
			case TokenType.PRINT:
				statement = self.__parse_print_statement()
			case TokenType.DUMP:
				statement = self.__parse_dump_statement()
			case TokenType.NUMBER|TokenType.EOL|TokenType.SKIP: # Do nothing in these cases
				statement = lambda: 0
			case _:
				error(f"Unexpected token {curr} on line {self.memory.status_registers['ip']}")
		return statement

	def __parse_load_statement(self):
		self.__consume(TokenType.LOAD)
		register = self.__consume(TokenType.REGISTER)
		self.__consume(TokenType.COMMA)
		value_at = self.__parse_load_addr_types()
		def lambda_():
			self.memory.registers[register.lexeme] = value_at()
		return lambda_
	
	def __parse_load_addr_types(self):
		curr = self.__peek()
		match curr.tokentype:
			case TokenType.NUMBER:
				func = self.__parse_direct_addr()
			case TokenType.EQUALS:
				func = self.__parse_immediate_addr()
			case TokenType.LBRACET:
				func = self.__parse_index_addr()
			case TokenType.AT:
				func = self.__parse_indirect_addr()
			case TokenType.DOLLAR:
				func = self.__parse_relative_addr()
			case _:
				raise Exception("Error parsing load addr")
		return func
		...

	def __parse_store_statement(self):
		self.__consume(TokenType.STORE)
		register = self.__consume(TokenType.REGISTER)
		self.__consume(TokenType.COMMA)
		value_to = self.__parse_store_addr_types()
		def lambda_():
			self.memory.addresses[value_to] = str(self.memory.registers[register.lexeme])
		return lambda_

	def __parse_store_addr_types(self) -> int:
		curr = self.__advance()
		match curr.tokentype:
			case TokenType.NUMBER:
				return curr.literal
			case TokenType.LBRACET:
				num = self.__consume(TokenType.NUMBER).literal
				self.__consume(TokenType.COMMA)
				reg = self.__consume(TokenType.REGISTER)
				self.__consume(TokenType.RBRACKET)
				return self.memory.registers[reg] + num
			case TokenType.DOLLAR:
				offset = self.__consume(TokenType.NUMBER).literal
				return self.memory.status_registers["ip"] + offset
			case _:
				error("Error parsing store addr")

	def __parse_add_statement(self):
		self.__consume(TokenType.ADD)
		r1 = self.__consume(TokenType.REGISTER).literal
		self.__consume(TokenType.COMMA)
		r2 = self.__consume(TokenType.REGISTER).literal
		def lambda_():
			self.memory.registers[r1] = self.memory.registers[r1] + self.memory.registers[r2]
		return lambda_
	
	def __parse_sub_statement(self):
		r1 = self.__consume(TokenType.REGISTER).literal
		self.__consume(TokenType.COMMA)
		r2 = self.__consume(TokenType.REGISTER).literal
		def lambda_():
			self.memory.registers[r1] = self.memory.registers[r1] - self.memory.registers[r2]

		return lambda_
	def __parse_mul_statement(self):
		r1 = self.__consume(TokenType.REGISTER).literal
		self.__consume(TokenType.COMMA)
		r2 = self.__consume(TokenType.REGISTER).literal
		def lambda_():
			self.memory.registers[r1] = self.memory.registers[r1] * self.memory.registers[r2]
		return lambda_

	def __parse_div_statement(self):
		r1 = self.__consume(TokenType.REGISTER).literal
		self.__consume(TokenType.COMMA)
		r2 = self.__consume(TokenType.REGISTER).literal
		def lambda_():
			self.memory.registers[r1] = self.memory.registers[r1] / self.memory.registers[r2]
			self.memory.registers[r2] = self.memory.registers[r1] % self.memory.registers[r2]
		return lambda_

	def __parse_inc_statement(self):
		self.__consume(TokenType.INC)
		r = self.__consume(TokenType.REGISTER).literal
		def lambda_():
			self.memory.registers[r] = int(self.memory.registers[r]) + 1
		return lambda_

	def __parse_halt_statement(self):
		self.__consume(TokenType.HALT)
		return None

	def __parse_print_statement(self):
		self.__consume(TokenType.PRINT)
		nxt = self.__peek()
		match nxt.tokentype:
			case TokenType.REGISTER:
				r = self.__consume(TokenType.REGISTER).literal
				return lambda: print(f"{r}: {self.memory.registers[r]}")
			case TokenType.NUMBER:
				n = self.consume(TokenType.NUMBER)
				return lambda: print(f"M[{n}]: {self.memory.addresses[n]}")
			case _:
				error("Error parsing print statement")
				

	def __parse_dump_statement(self):
		self.__consume(TokenType.DUMP)
		def lambda_():
			print(f"Registers: {self.memory.registers}")
			print(f"Main Memory: {self.memory.addresses}")
		return lambda_


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
		num = self.__consume(TokenType.NUMBER).literal
		self.__consume(TokenType.COMMA)
		register = self.__consume(TokenType.REGISTER).literal
		def lambda_():
			return self.memory.addresses[num + self.memory.registers[register]]
		return lambda_

	def __parse_indirect_addr(self):
		self.__consume(TokenType.AT)
		num = self.__consume(TokenType.NUMBER).literal
		def lambda_():
			first = self.memory.addresses[num]
			second = self.memory.addresses[first]
			return second
		return lambda_

	def __parse_relative_addr(self):
		self.__consume(TokenType.DOLLAR)
		num = self.__consume(TokenType.NUMBER).literal
		def lambda_():
			current_location = self.memory.status_registers["ip"]
			return self.memory.addresses[current_location + num]
		return lambda_

	
	def __previous(self) -> Token:
		return self.tokens[self.current - 1]

	def __advance(self) -> Token:
		self.current += 1
		return self.__previous()		

	def __peek(self) -> TokenType:
		if self.__is_at_end():
			return Token(TokenType.EOL, "", "")
		return self.tokens[self.current]
	
	def __check(self, token: TokenType) -> bool:
		return self.__peek().tokentype == token
	
	def __match(self, token: TokenType) -> Token|None:
		if self.__check(token):
			return self.__advance()
		return None

	def __consume(self, token: TokenType) -> Token:
		v = self.__match(token)
		if v is None:
			raise Exception(f"Token {token} expected but not found")
		return v
		
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

memory = Memory()
scanner = Scanner(memory, lines)	
parser = Parser(memory)
memory.load(lines)
memory.fde_cycle(scanner, parser)

