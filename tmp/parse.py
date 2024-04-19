from sys import argv, stderr
from io import StringIO

VERSION = "parse.py 0.0.1"

def print_usage():
	print("Usage: parse.py <file> -s|-m", file=stderr)

if len(argv) < 2:
	print_usage()
	exit(1)

if argv[1] in ['--help', '-h']:
	print_help()
	exit(0)

if argv[1] in ['--version', '-v']:
	print(VERSION)
	exit(0)

if len(argv) != 3:
	print_usage()
	exit(1)


indx = argv[1].find(".")
if indx != -1:
	FILE = argv[1][0:indx]
else:
	FILE = argv[1]

mode = argv[2].strip()
if mode not in ["-s", "-m"]:
	print("Expected -s or -m", file=stderr)
	exit(1)
if mode == '-s':
	splits = 1
else:
	splits = 2

with open(f"{FILE}.txt", "r") as f, open(f"{FILE}.out", "w+") as out:
	for line in f:
		if not line:
			continue
		tokens =line.split(maxsplit=splits)
		if splits == 1:
			out.write(f"{int(tokens[0], base=16)}: '{tokens[1].strip()}',\n")
		else:
			out.write(f"{int(tokens[0], base=16)}: ('{tokens[1].strip()}', '{tokens[2].strip()}'),\n")
