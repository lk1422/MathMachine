from enum import Enum, auto
from error_handling.errors import report

SPECIAL_SYMBOLS = { ")", ")", ",", "&", "|", "<", "-", ":", "~", "}", "{" }


class Tokens(Enum):
    OPEN_PAREN     = auto()
    CLOSED_PAREN   = auto()
    OPEN_BRACKET   = auto()
    CLOSED_BRACKET = auto()
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
    THUS           = auto()
    IMPORT         = auto()
    SHOW           = auto()
    FROM           = auto()
    CONCLUDE       = auto()
    EXPRESSIONS    = auto()
    END_OF_LINE    = auto()
    PROGRAM        = auto()

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
            case _:
                return False

    def is_unary(self):
        match self:
            case Tokens.NOT_OP:
                return True
            case _:
                return False


    def is_op(self):
        return self.is_unary() or self.is_binary()


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
    def __init__(self,token_type, literal=None):
        self.token_type = token_type
        self.literal = literal

    def __str__(self):
        if self.literal:
            return f"({str(self.token_type)}, {self.literal})"
        return str(self.token_type)

    def __eq__(self, other):
        if type(self) != type(other):
            return False

        return self.token_type == other.token_type and \
               self.literal == other.literal

    def __neq__(self, other):
        return not self == other

    def __hash__(self):
        if self.literal:
            return hash(self.token_type) ^ hash(self.literal)
        return hash(self.token_type)
