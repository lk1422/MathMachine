from token import Tokens, Token
from errors import report

class Symbol():
    def __init__(self, token):
        self.token = token
        self.parent = None
        self.index = -1
        self.children = []

    def set_parent(self, parent):
        self.parent = parent
        self.index = len(parent.children)

    def add_child(self, child):
        child.set_parent(self)
        self.children.append(child)


    def isomorphic_mapping(self, other):
        """
        Return True, Mapping of variables self -> other
        Return False
        Decl x ~= Decl y (SAME AST different literal values)
        True, {y : x}

        """
        variable_map = {}
        is_iso = self._recursive_isomorphic(other, variable_map)
        return is_iso, variable_map

    def _recursive_isomorphic(self, other, variable_map):
        """
        Make work on arbitrary terms, not neccasserily isomorphic
        RECURSIVE ISOMORPHIC EVAL DO THIS IN THE OTHER FUNCTION
        """
        if self.token.token_type != other.token.token_type:
            return False

        elif len(self.children) != len(other.children):
            return False

        if self.token.token_type == Tokens.WORD:
            var = self.token.literal
            other_var = other.token.literal
            if var in variable_map and variable_map[var] != other_var:
                return False
            variable_map[var] = other_var


        for s_c, o_c in zip(self.children, other.children):
            if not s_c._recursive_isomorphic(o_c, variable_map):
                return False

        return True

    def _build_predicate_name(self):
        assert self.token.token_type != Tokens.PREDICATE_NAME, "Expect Predicate Arg"
        name = self.token.literal
        name += "("
        for arg in self.children:
            name += arg.token.literal + ","

        name = name[:-1] + "_"
        return name


    def __eq__(self, other):
        #Can Only check Root Symbols
        check = self.token == other.token and \
                              len(self.children) == len(other.children)
        if check:
            for i in range(len(self.children)):
                if  self.children[i] != other.children[i]:
                    return False
            return True

        return False

    def __neq__(self, other):
        return not (self == other)

    def __hash__(self):
        hashed = hash(self.token)
        for c in self.children:
            hashed ^= hash(c)
        return hashed

    def __str__(self):
        string = ""
        return self._print_recursive(string, 0)

    def _print_recursive(self, string, level):
    
        if len(self.children) == 0:
            return ("\t\t" * level) + str(self.token) + "\n\n"

        left_ind = len(self.children)//2 
        left = self.children[:left_ind]

        if left_ind  < len(self.children):
           right = self.children[left_ind:]
           for c in right:
               string += c._print_recursive("", level + 1)

        string += ("\t\t" * level) + str(self.token) + "\n\n"

        for c in left:
           string += c._print_recursive("", level + 1)
               
        return string
