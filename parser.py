from tokens import Tokens, Token
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



def parse_statement(tokens, line):
    if tokens[0].token_type == Tokens.DECL:
        decl_symbol = Symbol(tokens[0])
        p_expr_tree = parse_decl(tokens[1:], line)
        decl_symbol.add_child(p_expr_tree)
        return decl_symbol
    else:
        return parse_expr(tokens, line)

def parse_decl(tokens, line):
    if tokens[0].token_type == Tokens.PREDICATE_NAME:
        return parse_predicate(tokens, line)
    else:
        return parse_pexpr(tokens, line)

def parse_expr(tokens, line):
    if tokens[0].token_type == Tokens.PREDICATE_NAME:
        return parse_predicate(tokens, line, allow_decl=False)
    else:
        return parse_pexpr(tokens, line)

def parse_predicate(tokens, line, allow_decl=True):

    pred_name = tokens[0]
    predicate = Symbol(pred_name)

    if tokens[1].token_type != Tokens.OPEN_PAREN:
        report(line, "Expected '(' after predicate declaration")

    args, remaining_tokens = parse_arglist(tokens[1:], line)

    for arg in args:
        predicate.add_child(arg)

    if len(remaining_tokens) > 0 and remaining_tokens[0].token_type == Tokens.PREDICATE_DECL:
        if not allow_decl:
            report(line, "Cannot Evaluate truth of predicate declaration add Decl before")
        decl = Symbol(remaining_tokens[0])
        expr = parse_pexpr(remaining_tokens[1:], line)
        decl.add_child(predicate)
        decl.add_child(expr)
        return decl

    return predicate

def parse_arglist(tokens, line):
    if len(tokens) == 0:
        report(line, "Error Parsing Arglist")
    elif tokens[0].token_type == Tokens.CLOSED_PAREN:
        return [], tokens[1:]

    elif tokens[0].token_type == Tokens.OPEN_PAREN:
        return parse_arglist(tokens[1:], line)

    if len(tokens) > 2 and tokens[0].token_type == Tokens.WORD  and tokens[1].token_type == Tokens.COMMA:
        args, remaining_tokens = parse_arglist(tokens[2:], line)
        return [Symbol(tokens[0])] + args, remaining_tokens
    elif tokens[0].token_type == Tokens.WORD:
        args, remaining_tokens = parse_arglist(tokens[1:], line) #Hits Basecase ')'
        return [Symbol(tokens[0])] + args, remaining_tokens
    else:
        report(line, f"Unexpected Token {tokens[0]} found in arglist")

def parse_pexpr(tokens, line):
    if len(tokens) == 0:
        report(line, f"Error Parsing Pexpr")
    if len(tokens) == 1:
        return Symbol(tokens[0])
    elif tokens[0].token_type == Tokens.OPEN_PAREN and tokens[-1].token_type == Tokens.CLOSED_PAREN:
        return parse_pexpr(tokens[1:-1], line)
    else:
        #Find Lowest Priority OP
        paren_level = 0
        lowest_priority_index = -1
        lowest_priority_value = float('inf')
        for i, tok in enumerate(tokens):
            if paren_level < 0:
                report(line, "Mismatched parethesis in pexpr")

            elif tok.token_type == Tokens.OPEN_PAREN:
                paren_level += 1
                continue

            elif tok.token_type == Tokens.CLOSED_PAREN:
                paren_level -= 1
                continue

            if paren_level > 0:
                continue

            elif tok.token_type.is_op():
                pl = tok.token_type.get_priority()
                if pl <= lowest_priority_value:
                    lowest_priority_value = pl
                    lowest_priority_index = i

        if lowest_priority_index == -1:
                report(line, "No Ops in Multi Word Expr")

        if lowest_priority_index >= len(tokens):
                report(line, "Operation Found in invalid location, at end of statement")

        if paren_level != 0:
                report(line, "Paren Never Closed")

        current_op = tokens[lowest_priority_index]
        op_symbol = Symbol(current_op)

        if current_op.token_type.is_op() and not current_op.token_type.is_binary():
            if lowest_priority_index != 0:
                report(line, "Binary Op Formatted Incorrectly")

            remaining = parse_pexpr(tokens[1:], line)
            op_symbol.add_child(remaining)

        elif current_op.token_type.is_op() and current_op.token_type.is_binary():
            lhs = parse_pexpr(tokens[:lowest_priority_index], line)
            rhs = parse_pexpr(tokens[lowest_priority_index+1:], line)
            op_symbol.add_child(lhs)
            op_symbol.add_child(rhs)

        return op_symbol

