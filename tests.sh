#!/usr/bin/env bash

TESTDIR="./examples"
TOFAIL=("${TESTDIR}/missing_halt.asm")

for filename in ${TESTDIR}/*; do
	if [[ ${TOFAIL[@]} =~ $filename ]]; then
		if python3 asm.py $filename > /dev/null
		then
			echo "${filename}: failed"
		else
			echo "${filename}: success"
		fi
	else
		if python3 asm.py $filename > /dev/null
		then
			echo "${filename}: success"
		else
			echo "${filename}: failed"
		fi
	fi

done
