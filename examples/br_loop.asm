LOAD R1, =1
LOAD R2, =11
hello:
PRINT R1
INC R1
BLT R1, R2, hello
HALT
