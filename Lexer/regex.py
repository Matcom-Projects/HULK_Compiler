from Lexer.nfa_dfa import NFA, DFA, nfa_to_dfa
from Lexer.automata_operation import automata_union, automata_concatenation, automata_closure, automata_minimization
from cmp.ast import *
from ParserLR1.Parser_LR1 import *
from cmp.pycompiler import Grammar
from cmp.utils import Token
from cmp.evaluation import *

EPSILON = 'ε'

class EpsilonNode(AtomicNode):
    def evaluate(self):
        # Your code here!!!
        return NFA(states = 1,finals =[0],transitions = {})
    
class SymbolNode(AtomicNode):
    def evaluate(self):
        s = self.lex
        # Your code here!!!
        return NFA(states = 2,finals = [1],transitions = {
            (0,s):  [1]
            })
    
class ClosureNode(UnaryNode):
    @staticmethod
    def operate(value):
        # Your code here!!!
        return automata_closure(value)
    
class UnionNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        # Your code here!!!
        return automata_union(lvalue,rvalue)
    
class ConcatNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        # Your code here!!!
        return automata_concatenation(lvalue,rvalue)

class Regex:
    def __init__(self,text):
        G = Grammar()

        E = G.NonTerminal('E', True)
        T, F, A, X, Y, Z = G.NonTerminals('T F A X Y Z')
        pipe, star, opar, cpar, symbol, epsilon = G.Terminals('| * ( ) symbol ε')

        # > PRODUCTIONS???
        # Your code here!!!
        ############################ BEGIN PRODUCTIONS ############################  


        # ========================== { E --> T X } ============================== #
        E %= T + X, lambda h,s: s[2], None, lambda h,s: s[1]                      

        # ========================== { X --> |T X } ============================== #
        # ========================== { X --> epsilon } ============================== #
        X %= pipe + T + X, lambda h,s: s[3], None, None, lambda h,s: UnionNode(h[0],s[2])    
        X %= G.Epsilon, lambda h,s: h[0]                                                    

        # ========================== { T --> F Y } ============================== #
        T %= F + Y, lambda h,s: s[2], None, lambda h,s: s[1]                      

        # ========================== { Y --> F Y } ============================== #
        # ========================== { Y --> epsilon } ============================== #
        Y %= F + Y, lambda h,s: s[2], None, lambda h,s: ConcatNode(h[0] , s[1])        
        Y %= G.Epsilon, lambda h,s: h[0]                                                    

        # ========================== { F --> A Z } ============================== #
        F %= A + Z, lambda h,s: s[2],None,lambda h,s: s[1]

        # ========================== { Z --> * Z } ============================== #
        # ========================== { Z --> epsilon } ============================== #
        Z %= star + Z, lambda h,s: s[2], None,lambda h,s:ClosureNode(h[0])
        Z %= G.Epsilon, lambda h,s: h[0] 

        # ========================== { A --> symbol } ============================== #
        # ========================== { A --> ( E ) } ============================== #
        # ========================== { A --> epsilon } ============================== #
        A %= symbol, lambda h,s: SymbolNode(s[1]) , None
        A %= opar + E + cpar, lambda h,s: s[2], None, None, None
        A %= epsilon, lambda h,s: EpsilonNode(h[0])


        ############################# END PRODUCTIONS #############################
        self.G = G
        self.automaton = self.build_automaton(text)

    def build_automaton(self,text):
        # print(self.G)
        # for lex in '| * ( ) ε'.split():
        #     print(self.G[f'{lex}'])
        tokens = self.regex_tokenizer(text,self.G)
        print(tokens)
        parser = LR1Parser(self.G)
        parse,operation = parser(tokens,get_shift_reduce=True)
        parse
        ast = evaluate_reverse_parse(parse,operation,tokens)
        nfa = ast.evaluate()
        dfa = nfa_to_dfa(nfa)
        return automata_minimization(dfa)

    def regex_tokenizer(self,text, G, skip_whitespaces=True):
        tokens = []
        # > fixed_tokens = ???
        # Your code here!!!
        fixed_tokens = { lex: Token(f'{lex}', G[lex]) for lex in '| * ( ) ε'.split() }
        for char in text:
            if skip_whitespaces and char.isspace():
                continue
            # Your code here!!!
            try:
                token = fixed_tokens[char]
            except:
                token = Token(char,G['symbol'])
            tokens.append(token)
            
        tokens.append(Token('$', G.EOF))
        return tokens