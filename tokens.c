enum Tokens {
    // Single Character Tokens
    COMMA,
    EQUALS,
    RBRACKET,
    LBRACKET,
    AT,
    DOLAR,

    // 1-2 Character Tokens 

    // Literals
    NUMBER,
    LABEL,
    LITERAL,
    REGISTER,

    // Keywords
    LOAD,
    STORE,
    READ,
    WRITE,

    ADD,
    SUB,
    MUL,
    DIV,
    INC,

    SKIP,

    BR,
    BLT,
    BGT,
    BLEQ,
    BGEQ,
    BEQ,

    HALT,

    EOF,
};