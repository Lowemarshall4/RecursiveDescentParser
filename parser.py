###################################################################################
# Name: Marshall Lowe                                                             #
# Penn State User ID: MHL5178                                                     #
# Purpose: Building a recursive descent parser                                    #
###################################################################################

from enum import Enum
import sys

# constants
LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

DIGITS = "0123456789"

KEYWORDS = ["b", "/b", "body", "/body", "i", "/i", "ul", "/ul", "li", "/li"]

class Constants(Enum):
    INVALID = 0
    STR = 1
    KEYWORD = 2
    EOI = 3



class Token:
    # class for representing tokens
    def __init__(self, type, val):
        self.type = type
        self.val = val

    def getTokenType(self):
        return self.type

    def getTokenVal(self):
        return self.val

    def __repr__(self) -> str:
        if self.type in [Constants.STR, Constants.KEYWORD]:
            return str(self.val)
        elif self.type == Constants.EOI:
            return ""
        elif self.type == Constants.INVALID:
            return "INVALID"

    
class Lexer():
    # class for representing lexer

    def __init__(self, s):
        self.stmt = s
        self.index = 0
        self.nextChar()
    
    def nextToken(self):
        while(True):
            if self.checkChar(' '):                         # skip whitespace
                continue
            if self.ch.isalpha() or self.ch.isdigit():      # tokenize it a string
                id = self.consumeChars(LETTERS+DIGITS)
                return Token(Constants.STR, id)
            elif self.checkChar('<'):                       # helper method to tokenize it as a Keyword
                return self.checkValidKeyword()
            elif self.checkChar('$'):                       # tokenize as end of input
                return Token(Constants.EOI, "")
            else:
                return Token(Constants.INVALID, self.ch)    #tokenize as invalid

    def nextChar(self):
        # get next char in statement
        self.ch = self.stmt[self.index]
        self.index += 1

    def consumeChars(self, charSet):
        # concatenate all chars into one string if they sequentially belong to charSet
        r = self.ch
        self.nextChar()
        while(self.ch in charSet):
            r = r + self.ch
            self.nextChar()
        return r

    def checkChar(self, c):
        # check if self.ch is a given character
        if self.ch == c:
            self.nextChar()
            return True
        return False

    def checkValidKeyword(self):
        # build and determine if a given keyword is valid or not
        id = '<'
        if(self.checkChar('>')):
            return Token(Constants.INVALID,id+'>')
        else:
            id += self.consumeChars(LETTERS+DIGITS+'/')
            if not self.checkChar('>'):
                self.nextChar()
                return Token(Constants.INVALID,'')
            elif(id[1:] in KEYWORDS):
                return Token(Constants.KEYWORD, id + '>')
            else: return Token(Constants.INVALID,'')

class Parser():
    def __init__(self, s):
        self.lex = Lexer(s+"$ ")                # add $ as EOI signal and added space to avoid lexer from indexing outside bounds
        self.token = self.lex.nextToken()
        self.keywordsSeen = []                  # array used to push keywords onto stack and pop when we see they were closed
        self.iLvl = 0                           # indentation level incrememted and decremented based on # of current open tags
    
    def run(self):
        self.webpage()

    def webpage(self):
        i = 1
        val = self.match(Constants.KEYWORD)
        # webpage must start and end with a body tag
        if val != "<body>":
            print("Expected <body> Recieved: {}".format(val))
            sys.exit(1)
        self.keywordsSeen.append("<body>")
        print(val)
        
        # while we have not seen the final closing body tag or EOI statment, process a textStmt
        while((self.token.getTokenVal() != '</body>') and (self.token.getTokenType() != Constants.EOI)):
            self.textStmt()
        
        if(self.token.getTokenVal() == "</body>"):
            print("</body>")
            self.keywordsSeen.remove("<body>")

        # if we finish processing tokens and we find a tag was left unclosed
        if len(self.keywordsSeen) > 0:
            for ele in self.keywordsSeen:
                print("ERROR: Expected closing's for tags [{}] were not found!".format(",".join(self.keywordsSeen)))
        self.iLvl += 1

    def textStmt(self):
        # method for processing TEXT nonterminals
        if self.token.getTokenType() == Constants.INVALID:
            print("ERROR INVALID TOKEN")
            sys.exit(1)
        elif self.token.getTokenType() == Constants.KEYWORD:
            self.keywordStmt()
        elif self.token.getTokenType() == Constants.STR:
            print('  ' * self.iLvl + self.token.getTokenVal())
            self.token = self.lex.nextToken()

    def keywordStmt(self):
        # method for varifying and processing keyword terminals

        # if the keyword is a closing tag
        if self.token.getTokenVal()[1] == "/":
            # if we are trying to close tags in incorrect order
            if(str(self.keywordsSeen[-1])[1:] != str(self.token.getTokenVal()[2:])):
                print("  " * self.iLvl + "ERROR: Expecting closing bracket for keyword: {} ... Found: {}".format((self.keywordsSeen[-1]), self.token.getTokenVal()))
                sys.exit(1)
            else:
                #else, print closing tag and pop off keywords seen
                self.iLvl -= 1
                print('  ' * self.iLvl + self.token.getTokenVal())
                self.keywordsSeen.pop()
        # check if tag will contain LISTITEM nonterminal
        elif self.token.getTokenVal() == "<ul>":
            self.listItemStmt()
            self.iLvl += 1
        # else, it is a simple opening tag, so print and pop to seen keywords
        else:
            print('  ' * self.iLvl + self.token.getTokenVal())
            self.keywordsSeen.append(self.token.getTokenVal())
            self.iLvl+= 1
        self.token = self.lex.nextToken()


    def listItemStmt(self):
        # method for processing LISTITEM nonterminals
        print('  ' * self.iLvl + "<ul>")
        self.token = self.lex.nextToken()
        self.iLvl += 1
        self.textStmt()
        print("</ul>")
        self.iLvl -= 1

    def match (self, tp):
        # method to check for a type
        val = self.token.getTokenVal()
        if (self.token.getTokenType() == tp):
            self.token = self.lex.nextToken()
        else: self.error(tp)
        return val


        

#TESTING - Will not run all tests! If parser runs into faulty tag closure it will sys.exit(1)
if __name__ == "__main__":

    print("Testing the lexer: test 1")
    lex = Lexer ("<body>google<b><i><b>yahoo Bing</b></i></b></body> $ ")
    tk = lex.nextToken()
    while (tk.getTokenType() != Constants.EOI):
        print(tk)
        tk = lex.nextToken()
    print("")

    print("Testing the lexer: test 2")
    lex = Lexer ("<body>google<b><i><b>yahoo</b></i></b> $ ")
    tk = lex.nextToken()
    while (tk.getTokenType() != Constants.EOI):
        print(tk)
        tk = lex.nextToken()
    print("")

    print("Testing the lexer: test 3")
    lex = Lexer ("<body>google<b><i><b>yahoo<badKeyword></badKeyword></i></b></body> $ ")
    tk = lex.nextToken()
    while (tk.getTokenType() != Constants.EOI):
        print(tk)
        tk = lex.nextToken()
    print("")

    print("Testing the parser: test 1")
    parser = Parser ("<body>google<b><i><b>yahoo bing goolgl2</b></i></b></body>")
    parser.run()

    print("Testing the parser: test 2")
    parser = Parser ("<body>google<b><i><b>yahoo</b></i></b>")
    parser.run()

    print("Testing the parser: test 3")
    parser = Parser ("<body><b><i><b></b></i></b></body>")
    parser.run()

    print("Testing the parser: test 4")
    parser = Parser ("<body>google</b><i><b>yahoo</b></i></b>")
    parser.run()

    print("Testing the parser: test 5")
    parser = Parser ("<body>google<b><i><b>yahoo</i></b></body>")
    parser.run()

    print("Testing the parser: test 6")
    parser = Parser ("<body>google<b><i><b>yahoo<badKeyword></badKeyword></i></b></body>")
    parser.run()

