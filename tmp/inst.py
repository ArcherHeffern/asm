with open("instruction_sets.txt", "r") as f, open("instruction_sets.out", "w+") as out:
	for line in f:
		if not line:
			continue
		tokens =line.split(maxsplit=1)
		out.write(f"{int(tokens[0], base=16)}: '{tokens[1].strip()}',\n")
