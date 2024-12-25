##Convert AST to Truth value
##Conversion is stateful, to make use of Decl

#TODO:

from symbol import Symbol
from token import Tokens
from errors import report
from lexer import lex_file
from parser import parse_statement
import utils

import copy

class Evaluator():
    def __init__(self):
        self.state = set() # Stores variable truth values
        self.predicates = {}
        self.rules = {}

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
                case Tokens.THUS:
                    return self._perform_thus(ast, line)
                case Tokens.IMPORT:
                    return self._perform_import(ast, line)
                case _:
                    report(line, f"Unreachable case hit OP {ast.token.token_type} not recognized")


    def _perform_import(self, ast, line):
        if len(ast.children) != 1 and ast.children[0].token.token_type != Tokens.WORD:
            report(line, f"Expected Filename got {ast.children[0].token}")
        rule_name = ast.children[0].token.literal
        const, result = self._parse_rule(rule_name, line)
        self.rules[rule_name] = (const, result)
        return True

    def _perform_thus(self, ast, line):
        
        for rule_name, (const, res) in self.rules.items():
            for true_expr in list(self.state):
                cons_mapping, res_mapping = dict(), dict()
                result_res = self._satisfy_rule(res, ast.children[0], False, res_mapping)
                if not result_res:
                    continue
                cons_res = self._satisfy_rule(const, true_expr, True, cons_mapping)
                if cons_res and result_res:
                    for key, value in res_mapping.items():
                        if key in cons_mapping and cons_mapping[key] == value:
                            self.state.add(ast.children[0])
                            self._add_resulting_statement(ast.children[0])
                            return True
        return False

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
        elif ast.children[0].token.token_type == Tokens.PREDICATE_NAME:
            self._add_resulting_statement(ast.children[0])
            self.state.add(ast.children[0])
        else:
            self.state.add(ast.children[0])

        return True

    def _add_resulting_statement(self, ast):

        if ast.token.token_type != Tokens.PREDICATE_NAME:
            return
        predicate_name = ast.token.literal
        num_args = len(ast.children)
        full_name = f"{predicate_name}/{num_args}"
        if not full_name in self.predicates:
            return

        predicate, expr = self.predicates[full_name]
        expr = copy.deepcopy(expr)
        assert len(predicate.children) == len(ast.children)
        arg_map = { 
            pred_arg.token.literal : called_arg.token.literal
                for pred_arg, called_arg in zip(predicate.children, ast.children)
        }
        utils._recursive_rename(expr, arg_map)
        self.state.add(expr)
        

    def _perform_and(self, ast, line): #Eval Children then perform and
        if len(ast.children) != 2:
            report(line, f"Invalid AND found in AST, 2 children required\n {str(ast)}")
        lhs = self.eval(ast.children[0], line)
        if not lhs: #Short Circuit
            return False
        rhs = self.eval(ast.children[1], line)
        if rhs:
            self.state.add(ast)
        return rhs 

    def _perform_or(self, ast, line):
        #Eval Children then perform and
        if len(ast.children) != 2:
            report(line, f"Invalid OR found in AST, 2 children required\n {str(ast)}")
        lhs = self.eval(ast.children[0], line)
        if lhs: #Short Circuit
            self.state.add(ast)
            return True
        rhs = self.eval(ast.children[1], line)
        if rhs:
            self.state.add(ast)
        return rhs 

    def _perform_not(self, ast, line):
        #Eval Children then perform not
        if len(ast.children) != 1:
            report(line, f"Invalid NOT found in AST, 1 children required\n {str(ast)}")

        tv = not self.eval(ast.children[0], line)
        if tv:
            self.state.add(ast)
        return tv

    def _perform_cond(self, ast, line):
        #Eval Children then perform cond
        #~p v q
        if len(ast.children) != 2:
            report(line, f"Invalid COND found in AST, 2 children required\n {str(ast)}")
        lhs = self.eval(ast.children[0], line)
        if not lhs: #Short Circuit
            self.state.add(ast)
            return True
        rhs = self.eval(ast.children[1], line)
        if rhs:
            self.state.add(ast)
        return rhs 

    def _perform_bicond(self, ast, line):
        #Eval Children then perform cond
        #~p v q
        if len(ast.children) != 2:
            report(line, f"Invalid COND found in AST, 2 children required\n {str(ast)}")
        lhs = self.eval(ast.children[0], line)
        rhs = self.eval(ast.children[1], line)
        tv = lhs == rhs
        if tv:
            self.state.add(ast)
        return tv

    def _perform_pred(self, ast, line):
        #Rename with variables passed in
        predicate_name = ast.token.literal
        num_args = len(ast.children)
        full_name = f"{predicate_name}/{num_args}"
        if not full_name in self.predicates:
            return False
            #report(line, f"Undefined Predicate {full_name}")

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


    def _parse_rule(self, filename, line):
        with open(filename) as f:
            lines = f.readlines()
        assert len(lines) == 2, "Expected 2 line theorem"
        lexed = lex_file(filename)
        const = parse_statement(lexed[0], line)
        result = parse_statement(lexed[1], line)
        return const, result

    def _satisfy_rule(self, rule, apply, constraint, variable_mapping):
        status = self._match_rule_tree(rule, apply, constraint, variable_mapping)
        return status and (not constraint or self.eval(apply, -1))

    def _match_rule_tree(self, rule, apply, constraint, variable_mapping):
        if rule.token.token_type == Tokens.WORD:
            #Check for override
            if not rule.token.literal in variable_mapping:
                variable_mapping[rule.token.literal] = apply
                return True
            return variable_mapping[rule.token.literal] == apply

        if rule.token.token_type != apply.token.token_type:
            return False

        elif len(rule.children) != len(apply.children):
            return False

        for r_c, a_c in zip(rule.children, apply.children):
            if not self._match_rule_tree(r_c, a_c, constraint, variable_mapping):
                return False

        return True
