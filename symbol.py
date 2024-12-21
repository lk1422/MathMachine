from token import Tokens, Token
from errors import report

class Symbol():
    def __init__(self, token):
        self.token = token
        self.parent = None
        self.children = []

    def set_parent(self, parent):
        self.parent = parent

    def add_child(self, child):
        child.set_parent(self)
        self.children.append(child)

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
