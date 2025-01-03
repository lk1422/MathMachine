from frontend.token import Token, Tokens
from frontend.symbol import Symbol
from error_handling.errors import report
from utils.utils import rename_predicate_args

import sys

class Parser():
    def __init__(self, tokens, line_no=1, only_pexpr=False):
        self.tokens = tokens
        self.ast = Symbol(Token(Tokens.PROGRAM))
        self.line_no = line_no
        self.only_pexpr = False

    def build_ast(self):
        while len(self.tokens):
            self._parse_statement()
        return self.ast

    def _parse_statement(self):
        match self.tokens:
            case [
                Token(token_type=Tokens.END_OF_LINE),
                *remaining
            ]:
                self.tokens = remaining
                self.line_no += 1
                return

            case [
                Token(token_type=Tokens.IMPORT), 
                Token(token_type=Tokens.WORD, literal=file_name), 
                Token(token_type=Tokens.END_OF_LINE), 
                *remaining
            ]:
                self._handle_only_pexpr()
                self._handle_import(file_name, remaining)
                return
            
            case [
                Token(token_type=Tokens.THUS), 
                *remaining
            ]:
                self._handle_only_pexpr()
                self._handle_thus(remaining)
                return

            case [
                Token(token_type=Tokens.DECL), 
                *remaining
            ]:
                self._handle_only_pexpr()
                self._handle_decl(remaining)
                return

            case  [Token(token_type=Tokens.SHOW), *remaining]:
                self._handle_only_pexpr()
                self._handle_show(remaining)
                return

            case _:
                if len(self.tokens):
                    self._handle_pexpr(self.tokens)
                else:
                    report(self.line_no, "Unreachable")

    def _parse_pexpr(self, pexpr):
        """
        Need to get the next best operation to perform
        Invalid Current Approach
        """
        match pexpr:

            case [
                Token(token_type=Tokens.OPEN_PAREN),
                *pexpr1,
                Token(token_type=Tokens.CLOSED_PAREN)
            ] if self._balanced_paren(pexpr):
                return self._parse_pexpr(pexpr1)

            case [ 
                Token(token_type=Tokens.PREDICATE_NAME, literal=predicate_name),
                Token(token_type=Tokens.OPEN_PAREN),
                *arglist,
                Token(token_type=Tokens.CLOSED_PAREN),
            ] if (args := self._parse_arglist(arglist)) != None:

                predicate_sym = Symbol(Token(Tokens.PREDICATE_NAME, literal=predicate_name))
                arg_symbols = self._parse_arglist(arglist)
                for arg in arg_symbols:
                    predicate_sym.add_child(arg)
                return predicate_sym

            case [
                Token(token_type=Tokens.PREDICATE_NAME, literal=predicate_name),
                *remaining
            ] if self._is_decl(remaining):
                return self._handle_predicate_decl(
                    Token(Tokens.PREDICATE_NAME, literal=predicate_name), 
                    remaining
                    )

            case [
                Token(token_type=Tokens.WORD, literal=atom)
            ]:
                return Symbol(Token(Tokens.WORD, literal=atom))

                
            case _:
                return self._handle_op(pexpr)

    def _parse_arglist(self, arglist):
        match arglist:
            case []:
                return []
            case [Token(token_type=Tokens.WORD, literal=name)]:
                return [Symbol(Token(Tokens.WORD, literal=name))]
            case [Token(token_type=Tokens.WORD, literal=name), Token(token_type=Tokens.COMMA), *rem]:
                return [Symbol(Token(Tokens.WORD, literal=name))] + self._parse_arglist(rem)
            case _:
                None

#==============================================================# 
#Statement Case Handlers                                       #
#==============================================================#

    def _handle_show(self, tokens):
        #Deal with new line_no in recursive sub programs
        goal_pexpr, remaining = self._handle_sub_pexpr(tokens)
        from_sym, remaining = self._handle_from(remaining)
        sub_program, remaining =self._handle_proof(remaining)
        self.tokens = remaining
        show = Symbol(Token(Tokens.SHOW))
        show.add_child(goal_pexpr)
        show.add_child(from_sym)
        show.add_child(sub_program)
        self.ast.add_child(show)

    def _handle_sub_pexpr(self, tokens):
        try:
            index = tokens.index(Token(Tokens.END_OF_LINE))
            rem = tokens[index+1:] if index < len(tokens)-1 else []
            pexpr = tokens[:index]
            if len(pexpr):
                parsed_pexpr = self._parse_pexpr(pexpr)
                self.line_no += 1
                return parsed_pexpr, rem
            else:
                report(self.line_no, "Expected pexpr")

        except ValueError:
            report(self.line_no, "Expected to Find EOL Token")
        

    def _handle_thus(self, tokens):
        try:
            thus_sym = Symbol(Token(Tokens.THUS))
            index = tokens.index(Token(Tokens.END_OF_LINE))
            #I can simplify this
            rem = tokens[index+1:] if index < len(tokens)-1 else []
            pexpr = tokens[:index]
            if len(pexpr):
                parsed_pexpr = self._parse_pexpr(pexpr)
                thus_sym.add_child(parsed_pexpr)
                self.ast.add_child(thus_sym)
                self.tokens = rem
                self.line_no += 1
            else:
                report(self.line_no, "Expected pexpr after THUS")

        except:
            report(self.line_no, "Expected to Find EOL Token")
        
    def _handle_decl(self, tokens):
        try:
            decl_sym = Symbol(Token(Tokens.DECL))
            index = tokens.index(Token(Tokens.END_OF_LINE))
            rem = tokens[index+1:] if index < len(tokens)-1 else []
            pexpr = tokens[:index]
            if len(pexpr):
                parsed_pexpr = self._parse_pexpr(pexpr)
                decl_sym.add_child(parsed_pexpr)
                self.ast.add_child(decl_sym)
                self.tokens = rem
                self.line_no += 1
            else:
                report(self.line_no, "Expected pexpr after DECL")


        except ValueError:
            report(self.line_no, "Expected to Find EOL Token")

    def _handle_pexpr(self, tokens):
        #COMEBACK
        try:
            index = tokens.index(Token(Tokens.END_OF_LINE))
            rem = tokens[index+1:] if index < len(tokens)-1 else []
            pexpr = tokens[:index]
            if len(pexpr):
                parsed_pexpr = self._parse_pexpr(pexpr)
                self.ast.add_child(parsed_pexpr)
                self.tokens = rem
                self.line_no += 1
            else:
                report(self.line_no, "Expected pexpr")

        except ValueError:
            report(self.line_no, "Expected to Find EOL Token")
        

    def _handle_import(self, filename, remaining):
        import_sym = Symbol(Token(Tokens.IMPORT))
        fn = Symbol(Token(Tokens.WORD, literal=filename))
        import_sym.add_child(fn)
        self.ast.add_child(import_sym)
        self.tokens = remaining
        self.line_no += 1

    def _handle_op(self, tokens):

        next_op = self._get_next_operation(tokens)

        if next_op == -1:
            report(self.line_no, "Cound't Find next operation")

        current_op = tokens[next_op]
        op_sym = Symbol(current_op)

        if current_op.token_type.is_unary():
            if next_op != 0:
                report(self.line_no, "Incorrectly Formatted Binary Operation")
            pexpr = self._parse_pexpr(tokens[1:])
            op_sym.add_child(pexpr)
            return op_sym

        elif current_op.token_type.is_binary():

            lhs = self._parse_pexpr(tokens[:next_op])
            rhs = self._parse_pexpr(tokens[next_op+1:])
            op_sym.add_child(lhs)
            op_sym.add_child(rhs)
            return op_sym
        else:
            report(self.line_no, "Op not binary or Unary Error")

    def _handle_predicate_decl(self, predicate_tok, remaining):
        if remaining[0] != Token(Tokens.OPEN_PAREN):
            report(self.line_no, "Expected Open Paren after Predicate Name")
        try:

            pred_decl_sym = Symbol(Token(Tokens.PREDICATE_DECL))
            predicate_sym = Symbol(predicate_tok)

            close_paren = remaining.index(Token(Tokens.CLOSED_PAREN))
            arglist = remaining[1 : close_paren]
            arg_symbols = self._parse_arglist(arglist)

            if remaining[close_paren+1] != Token(Tokens.PREDICATE_DECL):
                report(self.line_no, "Expected `:` after predicate name for declaration")

            pexpr = remaining[close_paren+2 :]
            mapped_expr = self._parse_pexpr(pexpr)

            for arg in arg_symbols:
                predicate_sym.add_child(arg)

            pred_decl_sym.add_child(predicate_sym)
            pred_decl_sym.add_child(mapped_expr)

            return rename_predicate_args(pred_decl_sym)

        except ValueError as e:
            report(self.line_no, "Expected CLOSED_PAREN")

    def _handle_only_pexpr(self):
        if self.only_pexpr:
            report(self.line_no, "Only Expected predicate expressions in this section")

    def _handle_from(self, tokens):
        assert tokens[0] == Token(Tokens.FROM), "Expected From token"
        assert tokens[1] == Token(Tokens.OPEN_BRACKET), "Expected From token"
        from_expr, remaining = self._get_between(
                                tokens[2:], 
                                Token(Tokens.OPEN_BRACKET),
                                Token(Tokens.CLOSED_BRACKET)
                            )
        from_expr = from_expr[:-1]
        from_expr.append(Token(Tokens.END_OF_LINE))

        sub_parser = Parser(from_expr, only_pexpr=True, line_no=self.line_no)
        from_ast = sub_parser.build_ast()
        from_ast.token = Token(Tokens.FROM)
        self.line_no = sub_parser.line_no
        return from_ast, remaining

    def _handle_proof(self, tokens):
        show_expr, remaining = self._get_between(
                                    tokens,
                                    Token(Tokens.SHOW),
                                    Token(Tokens.CONCLUDE)
                                )
        assert show_expr[-1] == Token(Tokens.CONCLUDE)
        sub_parser = Parser(show_expr[:-1], line_no=self.line_no)
        sub_ast = sub_parser.build_ast()
        self.line_no = sub_parser.line_no
        return sub_ast, remaining



#==============================================================#
#Helpers                                                       #
#==============================================================#

    def _is_decl(self, remaining):
        close_paren = remaining.index(Token(Tokens.CLOSED_PAREN))
        return remaining[close_paren+1] == Token(Tokens.PREDICATE_DECL)

    def _get_between(self, tokens, open_symbol, close_symbol=None):
        """
        Finds all tokens between the nested symbols, Assumes the statement was already
        opened
        """
        if close_symbol == None:
            close_symbol = open_symbol
        index = 0
        nesting_level = 1
        while nesting_level != 0:
            if index >= len(tokens):
                report(self.line_no, f"{open_symbol} Was Never Closed")
            if tokens[index] == open_symbol:
                nesting_level += 1
            elif tokens[index] == close_symbol:
                nesting_level -= 1
            index += 1

        return tokens[:index], tokens[index:]
        
    def _balanced_paren(self, pexpr):
        count = 0
        for i, tok in enumerate(pexpr):
            if tok == Token(Tokens.OPEN_PAREN):
                count += 1
            elif tok == Token(Tokens.CLOSED_PAREN):
                count -= 1

            if count == 0 and i+1 < len(pexpr): #CATCH (expr1) OP (expr2)
                return False

            if count < 0:
                return False
        return count == 0

    def _get_next_operation(self, tokens):
        lowest_priority_index = -1
        lowest_priority_value = float('inf')
        paren_level = 0
        for i, tok in enumerate(tokens):
            if paren_level < 0:
                report(self.line_no, "Mismatched parethesis in pexpr")

            elif tok == Token(Tokens.OPEN_PAREN):
                paren_level += 1
                continue

            elif tok == Token(Tokens.CLOSED_PAREN):
                paren_level -= 1
                continue

            if paren_level > 0:
                continue

            elif tok.token_type.is_op():
                pl = tok.token_type.get_priority()
                if pl <= lowest_priority_value:
                    lowest_priority_value = pl
                    lowest_priority_index = i

        if lowest_priority_index >= len(tokens):
            report(self.line_no, "Operation Found in invalid location, at end of statement")

        elif paren_level != 0:
            report(self.line_no, "Paren Never Closed")

        return lowest_priority_index
