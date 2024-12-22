from token import Tokens, Token, SPECIAL_SYMBOLS
from errors import report

def lex_file(filename, return_lines=False):

    with open(filename) as f:
        lines = f.readlines()

    statements = []
    new_lines = []
    for i, line in enumerate(lines):
        if len(line.strip()) == 0:
            continue
        statements.append(scan_line(line.strip(), i+1))
        new_lines.append(line)

    if return_lines:
        return statements, new_lines

    return statements

def scan_line(raw_text, line):
    tokens = []
    current = 0
    while current < len(raw_text):
        token, current = scan_token(raw_text, line, current)
        if token:
            tokens.append(token)
    return tokens

def scan_token(raw_string, line, current):
    match raw_string[current]:

        case "(":
            return Token(Tokens.OPEN_PAREN, None), current+1

        case ")":
            return Token(Tokens.CLOSED_PAREN, None), current+1

        case ",":
            return Token(Tokens.COMMA, None), current+1

        case "&":
            return Token(Tokens.AND_OP, None), current+1

        case "|":
            return Token(Tokens.OR_OP, None), current+1

        case "~":
            return Token(Tokens.NOT_OP, None), current+1

        case ":":
            return Token(Tokens.PREDICATE_DECL, None), current+1

        case "<":
            return biconditional(current, raw_string, line)

        case "-":
            return conditional(current, raw_string, line)

        case _:

            if raw_string[current].isspace():
                return None, current+1

            elif peek_buffer(current, raw_string, "Decl"):
                return Token(Tokens.DECL, None), current+4

            elif peek_buffer(current, raw_string, "Thus"):
                return Token(Tokens.THUS, None), current+4

            elif peek_buffer(current, raw_string, "import"):
                return Token(Tokens.IMPORT, None), current+6

            elif raw_string[current].isupper():
                return predicate_name(current, raw_string, line)

            elif raw_string[current].islower():
                return word(current, raw_string, line)

            else: 
                report(line, f"UNKNOWN TOKEN, {current}")

def predicate_name(current, raw_string, line):
    name = ""
    while raw_string[current] != "(":
        if raw_string[current].isspace():
            report(line, "Unexpected White space next to predicate name")

        if raw_string[current] in SPECIAL_SYMBOLS:
            report(line, "Unexpected Symbol found in predicate name")

        name += raw_string[current]
        current += 1
    return Token(Tokens.PREDICATE_NAME, name), current

def word(current, raw_string, line):
    name = ""
    while current < len(raw_string) and not raw_string[current].isspace() and not raw_string[current] in SPECIAL_SYMBOLS:
        name += raw_string[current]
        current += 1
    return Token(Tokens.WORD, name), current

def biconditional(current, raw_string, line):
    if current+2 < len(raw_string) and raw_string[current:current+3] == "<->":
       return Token(Tokens.BICOND_OP, None), current+3
    else:
        report(line, "Invalid Use of '<' not connected to biconditional '<->'")
        
def conditional(current, raw_string, line):
    if current+1 < len(raw_string) and raw_string[current:current+2] == "->":
       return Token(Tokens.COND_OP, None), current+2
    else:
        report("Invalid Use of '-' not connected to conditional '->'", line)

def peek_buffer(current, raw_string, target):
    return current+len(target) < len(raw_string) and raw_string[current: current+len(target)] == target
        
