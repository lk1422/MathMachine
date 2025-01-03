from frontend.lexer import Lexer
from frontend.token import Tokens, Token


def first_test():
    lex = Lexer("tests/examples/test1.mm")
    statements = lex.lex_file()
    for s in statements:
        print([str(tok) for tok in s])
        print()

def test_file(fn):
    lex = Lexer(fn)
    toks = lex.lex_file()
    print([str(tok) for tok in toks])

def run_all_tests():
    test_file("programs/cases.mm")


if __name__ == "__main__":
    run_all_tests()
