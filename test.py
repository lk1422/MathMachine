from tokens import *
from parser import parse_statement, Symbol

def test_lexer():
    #example_string = "( ) , -> <-> word | & Predicate(x1,x2, x3 )"
    example_string = "Predicate(x1,x2):(x1&x2)<->x1"
    tokens = scan_line(example_string, 0)
    print([str(tok) for tok in tokens])

def test_lex_file(file):
    lexed = lex_file(file)
    for line in lexed:
        print([str(tok) for tok in line])

def test_parse_statement():
    lexed = lex_file("first_program.mm")

    #Test first tree
    tree = parse_statement(lexed[0], 0)
    target = Symbol(Token(Tokens.DECL, None))
    target.add_child(Symbol(Token(Tokens.WORD, "y")))

    print(tree)
    assert target == tree, "Failed on line 0"
    print("Parsed First Line")
    
    #Test second tree
    tree = parse_statement(lexed[1], 1)
    target = Symbol(Token(Tokens.DECL, None))
    target.add_child(Symbol(Token(Tokens.NOT_OP, None)))
    target.children[0].add_child(Symbol(Token(Tokens.WORD, "x")))
    print(tree)
    assert target == tree, "Failed on line 0"
    print("Parsed Second Line")

    #Test third tree
    tree = parse_statement(lexed[2], 2)
    target = Symbol(Token(Tokens.DECL, None))
    target.add_child(Symbol(Token(Tokens.PREDICATE_DECL, None)))
    target.children[0].add_child(Symbol(Token(Tokens.PREDICATE_NAME, "P")))
    target.children[0].children[0].add_child(Symbol(Token(Tokens.WORD, "x")))

    pexpr = Symbol(Token(Tokens.COND_OP, None))
    pexpr.add_child(Symbol(Token(Tokens.WORD, "x")))
    pexpr.add_child(Symbol(Token(Tokens.WORD, "y")))
    target.children[0].add_child(pexpr)

    print(tree)
    assert target == tree, "Failed on line 3"
    print("Parsed Third Line")

    #Test fourth tree
    tree = parse_statement(lexed[3], 3)
    target = Symbol(Token(Tokens.PREDICATE_NAME, "P"))
    target.add_child(Symbol(Token(Tokens.WORD, "x")))

    print(tree)
    print
    assert target == tree, "Failed on line 4"
    print("Parsed Fourth Line")

    tree = parse_statement(lexed[4], 4)
    print(tree)
    
    


if __name__ == "__main__":
    #test_lex_file("first_program.mm")
    test_parse_statement()
