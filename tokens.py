from enum import Enum, auto
from errors import report

SPECIAL_SYMBOLS = { ")", ")", ",", "&", "|", "<", "-", ":", "~" }


class Tokens(Enum):
    OPEN_PAREN     = auto()
    CLOSED_PAREN   = auto()
    COMMA          = auto()
    DASH           = auto()
    LEFT_ANG       = auto()
    AND_OP         = auto()
    OR_OP          = auto()
    COND_OP        = auto()
    NOT_OP         = auto()
    BICOND_OP      = auto()
    PREDICATE_NAME = auto()
    PREDICATE_DECL = auto()
    WORD           = auto()
    DECL           = auto()

    def is_binary(self):
        match self:
            case Tokens.AND_OP:
                return True
            case Tokens.OR_OP:
                return True
            case Tokens.COND_OP:
                return True
            case Tokens.BICOND_OP:
                return True
            case Tokens.NOT_OP:
                return False
            case _:
                return False


    def is_op(self):
        match self:
            case Tokens.AND_OP:
                return True
            case Tokens.OR_OP:
                return True
            case Tokens.COND_OP:
                return True
            case Tokens.BICOND_OP:
                return True
            case Tokens.NOT_OP:
                return True
            case _:
                return False


    def get_priority(self):
        match self:
            case Tokens.AND_OP:
                return 1
            case Tokens.OR_OP:
                return 1
            case Tokens.COND_OP:
                return 0
            case Tokens.BICOND_OP:
                return 0
            case Tokens.NOT_OP:
                return 2
            case _:
                return None

class Token():
    def __init__(self,token_type, literal):
        self.token_type = token_type
        self.literal = literal

    def __str__(self):
        if self.literal:
            return f"({str(self.token_type)}, {self.literal})"
        return str(self.token_type)

    def __eq__(self, other):
        return self.token_type == other.token_type and \
               self.literal == other.literal

def lex_file(filename):

    with open(filename) as f:
        lines = f.readlines()

    statements = []
    for i, line in enumerate(lines):
        statements.append(scan_line(line, i))

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
        
