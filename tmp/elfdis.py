from sys import argv
from io import StringIO
from pprint import PrettyPrinter

PP = PrettyPrinter()

if len(argv) != 2:
	print("Usage: python elfd.py <filename>")
	exit(1)

filename = argv[1]

abis = [
"System V",
"HP-UX",
"NetBSD",
"Linux",
"Hurd",
"Solaris",
"(Monterey)",
"IRIX",
"FreeBSD",
"Tru64",
"Modesto",
"OpenBSD",
"OpenVMS",
"Kernel",
"AROS",
"FenixOS",
"CloudABI",
"OpenVOS"
]

# Object File data: (Type, Meaning)
e_types = [
	("ET_NONE", "Unknown."),
	("ET_REL", "Relocatable file."),
	("ET_EXEC", "Executable file."),
	("ET_DYN", "Shared object."),
	("ET_CORE", "Core file."),
	("ET_LOOS", "Reserved inclusive range. Operating system specific."),
	("ET_HIOS", "Reserved inclusive range. Processor specific."),
	("ET_LOPROC", "Reserved inclusive range. Processor specific."),
]

instruction_sets = {
	0: 'specific instruction set',
	1: 'AT&T WE 32100',
	2: 'SPARC',
	3: 'x86',
	4: 'Motorola 68000 (M68k)',
	5: 'Motorola 88000 (M88k)',
	6: 'Intel MCU',
	7: 'Intel 80860',
	8: 'MIPS',
	9: 'IBM System/370',
	10: 'MIPS RS3000 Little-endian',
	15: 'Hewlett-Packard PA-RISC',
	19: 'Intel 80960',
	20: 'PowerPC',
	21: 'PowerPC (64-bit)',
	22: 'S390, including S390x',
	23: 'IBM SPU/SPC',
	36: 'NEC V800',
	37: 'Fujitsu FR20',
	38: 'TRW RH-32',
	39: 'Motorola RCE',
	40: 'Arm (up to Armv7/AArch32)',
	41: 'Digital Alpha',
	42: 'SuperH',
	43: 'SPARC Version 9',
	44: 'Siemens TriCore embedded processor',
	45: 'Argonaut RISC Core',
	46: 'Hitachi H8/300',
	47: 'Hitachi H8/300H',
	48: 'Hitachi H8S',
	49: 'Hitachi H8/500',
	50: 'IA-64',
	51: 'Stanford MIPS-X',
	52: 'Motorola ColdFire',
	53: 'Motorola M68HC12',
	54: 'Fujitsu MMA Multimedia Accelerator',
	55: 'Siemens PCP',
	56: 'Sony nCPU embedded RISC processor',
	57: 'Denso NDR1 microprocessor',
	58: 'Motorola Star*Core processor',
	59: 'Toyota ME16 processor',
	60: 'STMicroelectronics ST100 processor',
	61: 'Advanced Logic Corp. TinyJ embedded processor family',
	62: 'AMD x86-64',
	63: 'Sony DSP Processor',
	64: 'Digital Equipment Corp. PDP-10',
	65: 'Digital Equipment Corp. PDP-11',
	66: 'Siemens FX66 microcontroller',
	67: 'STMicroelectronics ST9+ 8/16 bit microcontroller',
	68: 'STMicroelectronics ST7 8-bit microcontroller',
	69: 'Motorola MC68HC16 Microcontroller',
	70: 'Motorola MC68HC11 Microcontroller',
	71: 'Motorola MC68HC08 Microcontroller',
	72: 'Motorola MC68HC05 Microcontroller',
	73: 'Silicon Graphics SVx',
	74: 'STMicroelectronics ST19 8-bit microcontroller',
	75: 'Digital VAX',
	76: 'Axis Communications 32-bit embedded processor',
	77: 'Infineon Technologies 32-bit embedded processor',
	78: 'Element 14 64-bit DSP Processor',
	79: 'LSI Logic 16-bit DSP Processor',
	140: 'TMS320C6000 Family',
	175: 'MCST Elbrus e2k',
	183: 'Arm 64-bits (Armv8/AArch64)',
	220: 'Zilog Z80',
	243: 'RISC-V',
	247: 'Berkeley Packet Filter',
	257: 'WDC 65C816',
}

ph_types = [
	("PT_NULL", "Program header table entry unused."),
	("PT_LOAD", "Loadable segment."),
	("PT_DYNAMIC", "Dynamic linking information."),
	("PT_INTERP", "Interpreter information."),
	("PT_NOTE", "Auxiliary information."),
	("PT_SHLIB", "Reserved."),
	("PT_PHDR", "Segment containing program header table itself."),
	("PT_TLS", "Thread-Local Storage template.")
]

ph_flags = [
	("PF_X", "Executable segment"),
	("PF_W", "Writeable segment."),
	("PF_R", "Readable segment.")
]

sh_types = {
	0: ('SHT_NULL', 'Section header table entry unused'),
	1: ('SHT_PROGBITS', 'Program data'),
	2: ('SHT_SYMTAB', 'Symbol table'),
	3: ('SHT_STRTAB', 'String table'),
	4: ('SHT_RELA', 'Relocation entries with addends'),
	5: ('SHT_HASH', 'Symbol hash table'),
	6: ('SHT_DYNAMIC', 'Dynamic linking information'),
	7: ('SHT_NOTE', 'Notes'),
	8: ('SHT_NOBITS', 'Program space with no data (bss)'),
	9: ('SHT_REL', 'Relocation entries, no addends'),
	10: ('SHT_SHLIB', 'Reserved'),
	11: ('SHT_DYNSYM', 'Dynamic linker symbol table'),
	14: ('SHT_INIT_ARRAY', 'Array of constructors'),
	15: ('SHT_FINI_ARRAY', 'Array of destructors'),
	16: ('SHT_PREINIT_ARRAY', 'Array of pre-constructors'),
	17: ('SHT_GROUP', 'Section group'),
	18: ('SHT_SYMTAB_SHNDX', 'Extended section indices'),
	19: ('SHT_NUM', 'Number of defined types.'),
	1610612736: ('SHT_LOOS', 'Start OS-specific.'),
}

sh_flags = {
	1: ('SHF_WRITE', 'Writable'),
	2: ('SHF_ALLOC', 'Occupies memory during execution'),
	4: ('SHF_EXECINSTR', 'Executable'),
	16: ('SHF_MERGE', 'Might be merged'),
	32: ('SHF_STRINGS', 'Contains null-terminated strings'),
	64: ('SHF_INFO_LINK', '\'sh_info\' contains SHT index'),
	128: ('SHF_LINK_ORDER', 'Preserve order after combining'),
	256: ('SHF_OS_NONCONFORMING', 'Non-standard OS specific handling required'),
	512: ('SHF_GROUP', 'Section is member of a group'),
	1024: ('SHF_TLS', 'Section hold thread-local data'),
	267386880: ('SHF_MASKOS', 'OS-specific'),
	4026531840: ('SHF_MASKPROC', 'Processor-specific'),
	67108864: ('SHF_ORDERED', 'Special ordering requirement (Solaris)'),
	134217728: ('SHF_EXCLUDE', 'Section is excluded unless referenced or allocated (Solaris)'),
}

def get_sh_flags(flags: int):
	out = []
	for k, v in sh_flags.items():
		if flags & k != 0:
			out.append(v)
	return out


def dissassemble_x86_64(data: bytes):
	return data

with open(filename, 'rb') as f:
	def read(n: int) -> bytes:
		return f.read(n)

	def read_u4() -> bytes:
		return read(4)

	def read_u2() -> bytes:
		return read(2)

	def read_u1() -> bytes:
		return read(1)

	def to_int(byte: bytes) -> int:
		return int.from_bytes(byte, byteorder='little')
		
	
	elf_header = {}
	elf_header["magic_number"] = read_u4()
	elf_header["ei_class"] = "32 bit" if to_int(read_u1()) == 1 else "64 bit"
	elf_header["ei_data"] = "little endian" if to_int(read_u1()) == 1 else "big endian"
	elf_header["version"] = read_u1()
	elf_header["EI_OSABI"] = abis[to_int(read_u1())]
	elf_header["EI_ABIVERSION"] = read_u1()
	read(7) # EI_PAD
	elf_header["e_type"] = e_types[to_int(read_u2())][1]
	elf_header["instruction set"] = instruction_sets[to_int(read_u2())]
	elf_header["e_version"] = to_int(read_u4())
	elf_header["e_entry"] = to_int(read(8))
	elf_header["e_phoff"] = to_int(read(8))
	elf_header["e_shoff"] = to_int(read(8))
	elf_header["e_flags"] = to_int(read_u4())
	elf_header["e_ehsize"] = to_int(read_u2())
	elf_header["e_phentsize"] = to_int(read_u2())
	elf_header["e_phnum"] = to_int(read_u2())
	elf_header["e_shentsize"] = to_int(read_u2())
	elf_header["e_shnum"] = to_int(read_u2())
	elf_header["e_shstrndx"] = to_int(read_u2())

	program_headers = []
	num_entries = elf_header["e_phnum"]
	for _ in range(num_entries):
		program_header = {}
		f.seek(elf_header["e_phoff"], whence=0)
		program_header["p_type"] = ph_types[to_int(read_u4())]
		program_header["p_flags"] = ph_flags[to_int(read_u4()) + 1]
		program_header["p_offset"] = to_int(read(8))
		program_header["p_vaddr"] = to_int(read(8))
		program_header["p_paddr"] = to_int(read(8))
		program_header["p_filesz"] = to_int(read(8))
		program_header["p_memsz"] = to_int(read(8))
		# program_header["p_flags"] = 
		program_header["p_align"] = to_int(read(8))
		program_headers.append(program_header)

	section_headers = []
	f.seek(elf_header["e_shoff"])
	shnum = elf_header["e_shnum"]
	for _ in range(shnum):
		section_header = {}
		section_header["sh_name"] = read_u4()
		section_header["sh_type"] = sh_types[to_int(read_u4())]
		section_header["sh_flags"] = get_sh_flags(to_int(read(8)))
		section_header["sh_addr"] = to_int(read(8))
		section_header["sh_offset"] = to_int(read(8))
		section_header["sh_size"] = to_int(read(8))
		section_header["sh_link"] = to_int(read_u4())
		section_header["sh_info"] = read_u4()
		section_header["sh_addralign"] = to_int(read(8))
		section_header["sh_entsize"] = to_int(read(8))
		section_headers.append(section_header)

	for section_header in section_headers:
		f.seek(section_header["sh_offset"])
		data = read(section_header["sh_size"])
		if section_header["sh_type"] == sh_types[1]:
			data = dissassemble_x86_64(data)
		section_header["contents"] = data
		
	print("__Elf Header__")
	PP.pprint(elf_header)
	print()
	print("__Program Headers__")
	PP.pprint(program_headers)
	print()
	print("__Section Headers__")
	PP.pprint(section_headers)
