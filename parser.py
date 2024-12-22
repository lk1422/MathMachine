#Convert Lexed Tokens to AST
from token import Tokens, Token
from errors import report
from symbol import Symbol
from utils import *

#Clean up First token keywords all have the same code
def parse_statement(tokens, line):
    if tokens[0].token_type == Tokens.DECL:
        decl_symbol = Symbol(tokens[0])
        p_expr_tree = parse_decl(tokens[1:], line)
        decl_symbol.add_child(p_expr_tree)
        return decl_symbol

    elif tokens[0].token_type == Tokens.THUS:
        thus_sym = Symbol(tokens[0])
        p_expr_tree = parse_pexpr(tokens[1:], line)
        thus_sym.add_child(p_expr_tree)
        return  thus_sym

    elif tokens[0].token_type == Tokens.IMPORT:
        import_sym = Symbol(tokens[0])
        p_expr_tree = parse_pexpr(tokens[1:], line)
        import_sym.add_child(p_expr_tree)
        return  import_sym
    else:
        return parse_expr(tokens, line)

def parse_decl(tokens, line):
    if Tokens.PREDICATE_DECL in [tok.token_type for tok in tokens]:
        return parse_predicate(tokens, line)
    else:
        return parse_pexpr(tokens, line)


def parse_expr(tokens, line):
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
        return rename_predicate_args(decl)

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
    elif enclosed_paren(tokens, line):
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
            #Can be a predicate
            if tokens[0].token_type == Tokens.PREDICATE_NAME:
                return parse_predicate(tokens, line, allow_decl=False)
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

def enclosed_paren(tokens, line):
    if tokens[0].token_type != Tokens.OPEN_PAREN:
        return False

    if tokens[-1].token_type != Tokens.CLOSED_PAREN:
        return False

    if len(tokens) < 2:
        return False

    nesting_level = 1
    for i in range(1, len(tokens)):
        if tokens[i].token_type == Tokens.OPEN_PAREN:
            nesting_level += 1

        if tokens[i].token_type == Tokens.CLOSED_PAREN:
            nesting_level -= 1

        if nesting_level == 0 and i != len(tokens) - 1:
            return False

    return True


