from token import *
from lexer import *
from parser import parse_statement
from symbol import Symbol
from evaluator import Evaluator

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
    target.children[0].children[0].add_child(Symbol(Token(Tokens.WORD, "_x")))

    pexpr = Symbol(Token(Tokens.COND_OP, None))
    pexpr.add_child(Symbol(Token(Tokens.WORD, "_x")))
    pexpr.add_child(Symbol(Token(Tokens.WORD, "y")))
    target.children[0].add_child(pexpr)

    print(tree)
    print('hashed', hash(tree))
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

def test_eval():

    lexed = lex_file("second_program.mm")
    evaluate = Evaluator()

    #Test line 1
    tree = parse_statement(lexed[0], 0)
    assert evaluate.eval(tree, 0), "All Decl's return true"
    assert tree.children[0] in evaluate.state, "Failed to store expr"

    #Test line 2
    tree = parse_statement(lexed[1], 1)
    assert evaluate.eval(tree, 1), "All Decl's return true"
    assert tree.children[0] in evaluate.state, "Failed to store expr"

    #Test line 3
    tree = parse_statement(lexed[2], 2)
    assert evaluate.eval(tree, 2), "All Decl's return true"
    assert "P/1" in evaluate.predicates, "Name Defined in map"
    assert evaluate.predicates["P/1"][0] == tree.children[0].children[0], "Same Predicate"
    assert evaluate.predicates["P/1"][1] == tree.children[0].children[1], "Same expr"

    #Test line 4
    tree = parse_statement(lexed[3], 3)
    assert evaluate.eval(tree, 3), "True Predicate found to be false"

    #Test line 5
    tree = parse_statement(lexed[4], 4)
    assert evaluate.eval(tree, 4), "All Decl's return true"

    #Test line 6
    tree = parse_statement(lexed[5], 5)
    assert evaluate.eval(tree, 5), "True Predicate found false"



    return 
    for expr in evaluate.state:
        print(expr)

    for pred, pred_value in evaluate.predicates.items():
        print("PREDICATE DECL BEGIN")
        print(pred)
        print(pred_value[0])
        print("MAPS TO")
        print(pred_value[1])
        print("PREDICATE DECL END")

    
    

if __name__ == "__main__":
    test_eval()
