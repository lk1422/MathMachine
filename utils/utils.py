from frontend.token import Token, Tokens
from frontend.symbol import Symbol
import copy


def rename_predicate_args(ast):
    new_ast = copy.deepcopy(ast)
    args = new_ast.children[0].children
    arg_names = {}
    for arg in args:
        arg_names[arg.token.literal] = "_" + arg.token.literal
        arg.token.literal = "_" + arg.token.literal

    _recursive_rename(new_ast.children[1], arg_names)
    return new_ast

def _recursive_rename(ast, arg_names):
    if ast.token.token_type == Tokens.WORD and ast.token.literal in arg_names:
        ast.token.literal = arg_names[ast.token.literal]
        
    for c in ast.children:
        _recursive_rename(c, arg_names)

