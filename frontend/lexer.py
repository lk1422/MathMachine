from .token import Tokens, Token, SPECIAL_SYMBOLS
from error_handling.errors import critical_error, report

class Lexer():
    def __init__(self, filename):
        #\n ends statements
        self.raw_text = self._read_file(filename)
        self.current_ptr = 0
        self.line_no = 0
        #self.statements = []

    def lex_file(self):
        statements = []
        while self.current_ptr != len(self.raw_text):
            statements.append(self.lex_statement())
        return statements

    def lex_statement(self):
        """
            Statements typically are just a single line, thus we parse the tokens off of a line.
            However the Show expr From{...} ... Conclusion is a block statement, thus is all
            parsed together in a single line.
        """
        statement_tokens = []

        eos = self._get_end_of_statement()
        while self.current_ptr != eos:
            if (tok := self.scan_token()):
                statement_tokens.append(tok)
        return statement_tokens

    def peek(self, chars):
        if self.current_ptr + chars <= len(self.raw_text):
            return self.raw_text[self.current_ptr : self.current_ptr+chars]
        else:
            return ""

    @property
    def char(self):
        return self.raw_text[self.current_ptr]
            
    def advance_ptr(self, amt=1):
        self.current_ptr += amt

    def scan_token(self):
        """
            Parse invidiual token
        """
        match self.char:
            case "(":
                self.advance_ptr()
                return Token(Tokens.OPEN_PAREN, None)

            case ")":
                self.advance_ptr()
                return Token(Tokens.CLOSED_PAREN, None)

            case "{":
                self.advance_ptr()
                return Token(Tokens.OPEN_BRACKET, None)

            case "}":
                self.advance_ptr()
                return Token(Tokens.CLOSED_BRACKET, None)

            case ",":
                self.advance_ptr()
                return Token(Tokens.COMMA, None)

            case "&":
                self.advance_ptr()
                return Token(Tokens.AND_OP, None)

            case "|":
                self.advance_ptr()
                return Token(Tokens.OR_OP, None)

            case "~":
                self.advance_ptr()
                return Token(Tokens.NOT_OP, None)

            case ":":
                self.advance_ptr()
                return Token(Tokens.PREDICATE_DECL, None)

            case "<":
                return self.handle_lt()

            case "-":
                return self.handle_minus()

            case "\n":
                self.line_no += 1
                self.advance_ptr()
                return None

            case _:
                if self.char.isspace():
                    self.advance_ptr()
                    return None

                elif self.peek(len("Decl")) == "Decl":
                    self.advance_ptr(len("Decl"))
                    return Token(Tokens.DECL, None)

                elif self.peek(len("Thus")) == "Thus":
                    self.advance_ptr(len("Decl"))
                    return Token(Tokens.THUS, None)

                elif self.peek(len("import")) == "import":
                    self.advance_ptr(len("import"))
                    return Token(Tokens.IMPORT, None)

                elif self.peek(len("Show")) == "Show":
                    self.advance_ptr(len("Show"))
                    return Token(Tokens.SHOW, None)

                elif self.peek(len("From")) == "From":
                    self.advance_ptr(len("From"))
                    return Token(Tokens.FROM, None)

                elif self.peek(len("Conclude")) == "Conclude":
                    self.advance_ptr(len("Conclude"))
                    return Token(Tokens.CONCLUDE, None)

                elif self.char.isupper():
                    return self.predicate()

                elif self.char.islower():
                    return self.word()

                else:
                    sym = self.raw_text[self.current_ptr] 
                    report(self.line_no, f"Cannot Reckognize Symbol {sym}")

    def handle_lt(self):
        if self.peek(len("<->")) == "<->":
            self.advance_ptr(len("<->"))
            return Token(Tokens.BICOND_OP, None)
        else:
            report(self.line_no, "Invalid sequence of charecters followed from '<'")

    def handle_minus(self):
        if self.peek(len("->")) == "->":
            self.advance_ptr(len("->"))
            return Token(Tokens.COND_OP, None)
        else:
            report(self.line_no, "Invalid sequence of charecters followed from '-'")

    def predicate(self):
        name = ""
        while self.char != "(":
           if self.char.isspace():
               report(self.line_no, "Unexpected space before '(' in predicate")

           elif self.char in SPECIAL_SYMBOLS:
               report(self.line_no, "Unexpected symbol in predicate name")

           name += self.char
           self.advance_ptr()
        return Token(Tokens.PREDICATE_NAME, name)

    def word(self):
        word = ""
        while self.current_ptr < len(self.raw_text) \
            and not self.char.isspace() and not self.char in SPECIAL_SYMBOLS:
            word += self.char
            self.advance_ptr()
        return Token(Tokens.WORD, word)

    def _get_end_of_statement(self):
        """
            Return the index directly after the current statement
        """
        try:
            if self.peek(len("Show")) == "Show":
                return self.raw_text.index("Conclude", self.current_ptr) + len("Conclude")
            else:
                next_line = self.raw_text.find("\n", self.current_ptr)
                return next_line+1 if next_line != -1 else len(self.raw_text)
        except Exception as e:
            report(self.line_no, "Failed to find ending of sequence")

    @staticmethod
    def _read_file(filename):
        try:
            with open(filename) as f:
                return f.read()
        except:
            critical_error(f"Lexer failed to read file {filename}")
