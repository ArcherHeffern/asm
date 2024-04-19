from sys import argv

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
		
	
	data = {}
	data["magic_number"] = read_u4()
	data["ei_class"] = "32 bit" if to_int(read_u1()) == 1 else "64 bit"
	data["ei_data"] = "little endian" if to_int(read_u1()) == 1 else "big endian"
	data["version"] = read_u1()
	data["EI_OSABI"] = abis[to_int(read_u1())]
	data["EI_ABIVERSION"] = read_u1()
	read(7) # EI_PAD
	data["e_type"] = e_types[to_int(read_u2())][1]
	data["instruction set"] = instruction_sets[to_int(read_u2())]
	print(data)
