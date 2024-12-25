from frontend.lexer import Lexer
from frontend.token import Tokens, Token


def first_test():
    lex = Lexer("tests/examples/test1.mm")
    statements = lex.lex_file()
    print([str(tok) for tok in statements[3]])

def run_all_tests():
    first_test()


if __name__ == "__main__":
    run_all_tests()
