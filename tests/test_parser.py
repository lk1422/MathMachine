from frontend.token import Token, Tokens
from frontend.lexer import Lexer
from frontend.symbol import Symbol
from frontend.parser import Parser


def test_basic():
    lex = Lexer("programs/first_program.mm")
    tokens = lex.lex_file()
    parser = Parser(tokens)
    ast = parser.build_ast()

    test_ast = Symbol(Token(Tokens.PROGRAM))

    l1 = Symbol(Token(Tokens.IMPORT))
    l1.add_child(Symbol(Token(Tokens.WORD, "rules/predicate_calculus/modus_ponens")))
    test_ast.add_child(l1)
    assert l1==ast.children[0], "Line 1 Failure"

    l2 = Symbol(Token(Tokens.DECL))
    l2.add_child(Symbol(Token(Tokens.WORD, "y")))
    test_ast.add_child(l2)
    assert l2==ast.children[1], "Line 2 Failure"

    l3 = Symbol(Token(Tokens.DECL))
    l3.add_child(Symbol(Token(Tokens.NOT_OP)))
    l3.children[0].add_child(Symbol(Token(Tokens.WORD, "x")))
    test_ast.add_child(l3)
    assert l3==ast.children[2], "Line 3 Failure"

    l4 = Symbol(Token(Tokens.DECL))
    l4.add_child(Symbol(Token(Tokens.PREDICATE_DECL)))
    l4.children[0].add_child(Symbol(Token(Tokens.PREDICATE_NAME, "P")))
    l4.children[0].children[0].add_child(Symbol(Token(Tokens.WORD, "_x")))
    l4_pexpr = Symbol(Token(Tokens.COND_OP))
    l4_pexpr.add_child(Symbol(Token(Tokens.WORD, "_x")))
    l4_pexpr.add_child(Symbol(Token(Tokens.WORD, "y")))
    l4.children[0].add_child(l4_pexpr)
    test_ast.add_child(l4)
    assert l4==ast.children[3], "Line 4 Failure"


    l5 = Symbol(Token(Tokens.PREDICATE_NAME, "P"))
    l5.add_child(Symbol(Token(Tokens.WORD, "x")))
    test_ast.add_child(l5)
    assert l5==ast.children[4], "Line 5 Failure"

    l6 = Symbol(Token(Tokens.OR_OP))
    l6_rhs = Symbol(Token(Tokens.AND_OP))
    l6_rhs_cond = Symbol(Token(Tokens.COND_OP))
    l6_rhs_cond.add_child(Symbol(Token(Tokens.WORD, "x")))
    l6_rhs_cond.add_child(Symbol(Token(Tokens.WORD, "y")))
    l6_rhs.add_child(l6_rhs_cond)
    l6_rhs.add_child(Symbol(Token(Tokens.WORD, "w")))
    l6.add_child(l6_rhs)
    l6.add_child(Symbol(Token(Tokens.WORD, "z")))
    test_ast.add_child(l6)
    assert l6==ast.children[5], "Line 6 Failure"

    l7 = Symbol(Token(Tokens.THUS))
    l7.add_child(Symbol(Token(Tokens.WORD, 'y')))
    test_ast.add_child(l7)

    assert test_ast == ast, "Failed Test"

    print("Passed Test")

def test_proof():
    lex = Lexer("tests/examples/test2.mm")
    tokens = lex.lex_file()
    parser = Parser(tokens)
    ast = parser.build_ast()

    test_ast = Symbol(Token(Tokens.PROGRAM))

    show_symbol = Symbol(Token(Tokens.SHOW))
    goal = Symbol(Token(Tokens.WORD, "a"))
    show_symbol.add_child(goal)

    from_symbol = Symbol(Token(Tokens.FROM))

    from1 = Symbol(Token(Tokens.COND_OP))
    from1.add_child(Symbol(Token(Tokens.WORD, "b")))
    from1.add_child(Symbol(Token(Tokens.WORD, "a")))

    from2 = Symbol(Token(Tokens.WORD, "b"))

    from_symbol.add_child(from1)
    from_symbol.add_child(from2)
    show_symbol.add_child(from_symbol)

    sub_program = Symbol(Token(Tokens.PROGRAM))

    show2 = Symbol(Token(Tokens.SHOW))
    sub_sub_program = Symbol(Token(Tokens.PROGRAM))
    sub_sub_program.add_child(Symbol(Token(Tokens.WORD, "w")))
    show2.add_child(Symbol(Token(Tokens.WORD, "w")))
    show2.add_child(Symbol(Token(Tokens.FROM)))
    show2.add_child(sub_sub_program)

    sub_program.add_child(show2)

    operation = Symbol(Token(Tokens.AND_OP))
    lhs = Symbol(Token(Tokens.COND_OP))
    lhs.add_child(Symbol(Token(Tokens.WORD, "b")))
    lhs.add_child(Symbol(Token(Tokens.WORD, "a")))
    operation.add_child(lhs)
    operation.add_child(Symbol(Token(Tokens.WORD, "b")))
    sub_program.add_child(operation)

    thus = Symbol(Token(Tokens.THUS))
    thus.add_child(Symbol(Token(Tokens.WORD, "a")))
    sub_program.add_child(thus)

    show_symbol.add_child(sub_program)
    test_ast.add_child(show_symbol)

    assert test_ast == ast, "Failed Test"

    print("Passed Proof Test")



def print_ast(filename):
    lex = Lexer(filename)
    tokens = lex.lex_file()
    parser = Parser(tokens)
    ast = parser.build_ast()
    print(ast)

if __name__ == "__main__":
    test_basic()
    test_proof()
    #print_ast("programs/sixth.mm")


