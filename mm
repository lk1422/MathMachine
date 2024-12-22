#!/bin/python3
#Evaluate If all statements in a file logically follow from Decl
import sys
import evaluator
import lexer
import parser


def main():
    assert len(sys.argv) == 2, "Expected mm <filename>"
    file = sys.argv[1]
    evaluate = evaluator.Evaluator()
    lexed, raw_text = lexer.lex_file(file, return_lines=True)
    passed = True
    for i, lex in enumerate(lexed):
        print("EVALUATING", raw_text[i])
        expr = parser.parse_statement(lex, i+1)
        #print([str(tok) for tok in lex])
        #print(expr)
        truth_val = evaluate.eval(expr, i+1)
        if not truth_val:
            
            print("False Expression found, proof doesn't follow line:", i+1)
            passed = False
            break
    if passed:
        print("Proof Verified")

if __name__ == "__main__":
    main()


