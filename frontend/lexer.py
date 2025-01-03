from .token import Tokens, Token, SPECIAL_SYMBOLS
from error_handling.errors import critical_error, report

class Lexer():
    def __init__(self, filename):
        #\n ends statements
        self.raw_text = self._read_file(filename)
        self.current_ptr = 0
        self.line_no = 0
        self._tokens = []

    @property
    def tokens(self):
        
        if len(self._tokens) == 0:
            return self._tokens

        if self._tokens[-1] != Token(Tokens.END_OF_LINE):
            self._tokens.append(Token(Tokens.END_OF_LINE))

        return self._tokens

    def lex_file(self):
        while self.current_ptr != len(self.raw_text):
            self.scan_token()
        return self.tokens

    def get_tokens(self):
        return self.tokens

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
                self._tokens.append(Token(Tokens.OPEN_PAREN))

            case ")":
                self.advance_ptr()
                self._tokens.append(Token(Tokens.CLOSED_PAREN))

            case "{":
                self.advance_ptr()
                self._tokens.append(Token(Tokens.OPEN_BRACKET))

            case "}":
                self.advance_ptr()
                self._tokens.append(Token(Tokens.CLOSED_BRACKET))

            case ",":
                self.advance_ptr()
                self._tokens.append(Token(Tokens.COMMA))

            case "&":
                self.advance_ptr()
                self._tokens.append(Token(Tokens.AND_OP))

            case "|":
                self.advance_ptr()
                self._tokens.append(Token(Tokens.OR_OP))

            case "~":
                self.advance_ptr()
                self._tokens.append(Token(Tokens.NOT_OP))

            case ":":
                self.advance_ptr()
                self._tokens.append(Token(Tokens.PREDICATE_DECL))

            case "\n":
                self.line_no += 1
                self.advance_ptr()
                self._tokens.append(Token(Tokens.END_OF_LINE))

            case "<":
                self._tokens.append(self.handle_lt())

            case "-":
                self._tokens.append(self.handle_minus())

            case _:
                if self.char.isspace():
                    self.advance_ptr()

                elif self.peek(len("Decl")) == "Decl":
                    self.advance_ptr(len("Decl"))
                    self._tokens.append(Token(Tokens.DECL))

                elif self.peek(len("Thus")) == "Thus":
                    self.advance_ptr(len("Decl"))
                    self._tokens.append(Token(Tokens.THUS))

                elif self.peek(len("import")) == "import":
                    self.advance_ptr(len("import"))
                    self._tokens.append(Token(Tokens.IMPORT))

                elif self.peek(len("Show")) == "Show":
                    self.advance_ptr(len("Show"))
                    self._tokens.append(Token(Tokens.SHOW))

                elif self.peek(len("From")) == "From":
                    self.advance_ptr(len("From"))
                    self._tokens.append(Token(Tokens.FROM))

                elif self.peek(len("Conclude")) == "Conclude":
                    self.advance_ptr(len("Conclude"))
                    self._tokens.append(Token(Tokens.CONCLUDE))

                elif self.char.isupper():
                    self._tokens.append(self.predicate())

                elif self.char.islower():
                    self._tokens.append(self.word())

                else:
                    sym = self.raw_text[self.current_ptr] 
                    report(self.line_no, f"Cannot Reckognize Symbol {sym}")

    def handle_lt(self):
        if self.peek(len("<->")) == "<->":
            self.advance_ptr(len("<->"))
            return Token(Tokens.BICOND_OP)
        else:
            report(self.line_no, "Invalid sequence of charecters followed from '<'")

    def handle_minus(self):
        if self.peek(len("->")) == "->":
            self.advance_ptr(len("->"))
            return Token(Tokens.COND_OP)
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
