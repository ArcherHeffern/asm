All instructions (With arguments) occupy 4 bytes

16 GPR (R1..R16)
16 Status Registers (S1..S16)
Instruction size: 4 bits

Syntax: 
``` assembly
M[x] :  Denotes contents of memory at address, x
D[x] :  Denotes contents of disk at address, x 
Ri :  Denotes contents of GPR, Ri
PC :  Denotes contents of program counter
= :  Denotes assignment
```

# Instruction Set
## LOAD
1. Direct Addressing Syntax:
LOAD Ri, Addr 
Meaning: Ri ¬ M[Addr] 
Example: LOAD R3, 3000 

Load contents of memory location, 3000 into register R3

2. Immediate Operand Syntax:
LOAD Ri, =Num
Meaning: Ri ¬ Num 
Example: LOAD R3, =100

Loads constant 100, into register R3

3. Index Addressing Syntax:
LOAD Ri, [Addr, Rj]
Meaning: Ri ¬ M[Addr + Rj]
Example: LOAD R3, [3000, R4]

Suppose that 100 stored in R4 when instruction executed. Loads contents of memory location 3100 into register R3

4. Indirect Addressing Syntax: 
LOAD Ri, @ Addr
Meaning: Ri ¬ M[M[Addr]]
Example: LOAD R3, @ 3000 

Suppose that  M[3000] = 7000, and M[7000] = 100. Then this loads 100 into register R3

5. Relative Addressing Syntax:
LOAD Ri, $Num 
Meaning: Ri ¬ M[PC + Num]
Example: LOAD R3, $100 

Suppose that the above instruction has been placed in location 1000 in memory.  Then this loads the contents       of memory location 1100 into register R3 

Example 2:  LOAD R3, $R4 

Loads contents of memory location 1000 + contents of  R4 into register R3

## STORE

1. Direct Addressing Syntax: 
STORE Ri, Addr 
Meaning: M[Addr] ¬ Ri 
Example: STORE R3, 3000 

Stores contents of register R3 into memory location 3000 

2. Index Addressing Syntax: 
STORE Ri, [Addr, Rj] 
Meaning: M[Addr + Rj] ¬ Ri 
Example: STORE R3, [3000, R4] 

Suppose 100 is stored in R4 when instruction is executed.  Stores the contents of R3 into memory location 3100

3. Relative Addressing Syntax: 
STORE Ri, $Num 
Meaning: M[PC + Num] ¬ Ri 
Example: STORE R3, $100 

Suppose above instruction has been placed in location 1000 in memory.  Stores contents of R3 into memory location 1100 

Example 2:  STORE R3, $R4 

Stores contents of R3 into location 1000 + contents of R4

## ADD SUB MUL
Syntax:  
ADD Ri, Rj 
Meaning:  Ri ¬ Ri + Rj 
Example:  ADD R3, R4 4.    

Suppose R3 contains 400 and R4 contains 100.        Instruction replaces the contents of R3 with 500       and leaves R4 alone

## DIV INC LABEL SKIP BR BLT READ WRITE HALT
