##Convert AST to Truth value
##Conversion is stateful, to make use of Decl

#TODO:

from symbol import Symbol
from token import Tokens
from errors import report
import utils

import copy

class Evaluator():
    def __init__(self):
        self.state = set() # Stores variable truth values
        self.predicates = {}

    def eval(self, ast, line):
        """
        Return truth value of ast, & modify state in the case of a decl
        """
        if ast in self.state:
            return True

        elif ast.token.token_type == Tokens.WORD:
            ##ATOM NOT DEFINED BEHAVIOR
            return False

        else:
            match ast.token.token_type:
                case Tokens.AND_OP:
                    return self._perform_and(ast, line)
                case Tokens.OR_OP:
                    return self._perform_or(ast, line)
                case Tokens.COND_OP:
                    return self._perform_cond(ast, line)
                case Tokens.BICOND_OP:
                    return self._perform_bicond(ast, line)
                case Tokens.NOT_OP:
                    return self._perform_not(ast, line)
                case Tokens.PREDICATE_NAME:
                    return self._perform_pred(ast, line)
                case Tokens.DECL:
                    return self._perform_decl(ast, line)
                case _:
                    report(line, f"Unreachable case hit OP {ast.token.token_type} not recognized")


    def _perform_decl(self, ast, line):
        """
        The expression evaluates to true when declared
        Decl x
        Decl ~x
        Decl ~x | x
        """
        if len(ast.children) != 1:
            report(line, "Expect one child after DECL")
        elif ast.children[0].token.token_type == Tokens.PREDICATE_DECL:
            self._perform_pred_decl(ast.children[0], line)
        else:
            self.state.add(ast.children[0])

        return True


    def _perform_and(self, ast, line):
        #Eval Children then perform and
        if len(ast.children) != 2:
            report(line, f"Invalid AND found in AST, 2 children required\n {str(ast)}")
        lhs = self.eval(ast.children[0], line)
        if not lhs: #Short Circuit
            return False
        rhs = self.eval(ast.children[1], line)
        return rhs 
        

    def _perform_or(self, ast, line):
        #Eval Children then perform and
        if len(ast.children) != 2:
            report(line, f"Invalid OR found in AST, 2 children required\n {str(ast)}")
        lhs = self.eval(ast.children[0], line)
        if lhs: #Short Circuit
            return True
        rhs = self.eval(ast.children[1], line)
        return rhs 

    def _perform_not(self, ast, line):
        #Eval Children then perform not
        if len(ast.children) != 1:
            report(line, f"Invalid NOT found in AST, 1 children required\n {str(ast)}")
        return not self.eval(ast.children[0], line)

    def _perform_cond(self, ast, line):
        #Eval Children then perform cond
        #~p v q
        if len(ast.children) != 2:
            report(line, f"Invalid COND found in AST, 2 children required\n {str(ast)}")
        lhs = self.eval(ast.children[0], line)
        if not lhs: #Short Circuit
            return True
        rhs = self.eval(ast.children[1], line)
        return rhs 

    def _perform_bicond(self, ast, line):
        #Eval Children then perform cond
        #~p v q
        if len(ast.children) != 2:
            report(line, f"Invalid COND found in AST, 2 children required\n {str(ast)}")
        lhs = self.eval(ast.children[0], line)
        rhs = self.eval(ast.children[1], line)
        return lhs == rhs

    def _perform_pred(self, ast, line):
        #Rename with variables passed in
        predicate_name = ast.token.literal
        num_args = len(ast.children)
        full_name = f"{predicate_name}/{num_args}"
        if not full_name in self.predicates:
            report(line, f"Undefined Predicate {full_name}")

        predicate, expr = self.predicates[full_name]
        expr = copy.deepcopy(expr)
        assert len(predicate.children) == len(ast.children)
        arg_map = { 
            pred_arg.token.literal : called_arg.token.literal
                for pred_arg, called_arg in zip(predicate.children, ast.children)
        }
        utils._recursive_rename(expr, arg_map)
        return self.eval(expr, line)

    def _perform_pred_decl(self, ast, line):
        if len(ast.children) != 2:
            report(line, f"Invalid predicate decl found in AST, 2 children required\n {str(ast)}")
        predicate_name = ast.children[0].token.literal
        num_args = len(ast.children[0].children)
        full_name = f"{predicate_name}/{num_args}"
        self.predicates[full_name] = (ast.children[0], ast.children[1])



