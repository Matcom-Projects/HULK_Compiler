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
        T, F, A = G.NonTerminals('T F A')
        pipe, star, opar, cpar, symbol, epsilon = G.Terminals('| * ( ) symbol ε')


        # ############################## BEGIN PRODUCTIONS ##############################  
        # # ========================== {  E --> E | T  } ============================== #                     
        # # ========================== {  E --> T      } ============================== #
        E %= E + pipe + T, lambda h,s: UnionNode(s[1],s[3])
        E %= T, lambda h,s: s[1]                                                   
        # # ========================== {   T --> T F   } ============================== #
        # # ========================== {   T --> F     } ============================== #                     
        T %= T + F, lambda h,s: ConcatNode(s[1],s[2])
        T %= F, lambda h,s:s[1]
        # # ========================== {   F --> A *   } ============================== #
        # # ========================== {   F --> A     } ============================== #
        F %= A + star, lambda h,s: ClosureNode(s[1])
        F %= A,lambda h,s:s[1]
        # # ========================== { A --> symbol  } ============================== #
        # # ========================== { A --> ( E )   } ============================== #
        # # ========================== { A --> epsilon } ============================== #
        A %= symbol, lambda h,s: SymbolNode(s[1]) 
        A %= opar + E + cpar, lambda h,s: s[2]
        A %= epsilon, lambda h,s: EpsilonNode(s[1])
        # ############################### END PRODUCTIONS ###############################

        self.G = G
        self.automaton = self.build_automaton(text)

    def build_automaton(self,text):
        tokens = self.regex_tokenizer(text,self.G)
        parser = LR1Parser(self.G)
        parse,operation = parser([token.token_type for token in tokens],get_shift_reduce=True)
        ast = evaluate_reverse_parse(parse,operation,tokens)
        nfa = ast.evaluate()
        dfa = nfa_to_dfa(nfa)
        mini = automata_minimization(dfa)
        return mini

    def regex_tokenizer(self,text, G, skip_whitespaces=True):
        blen=False
        countblen=0
        lex=''
        tokens = []
        # > fixed_tokens = ???
        # Your code here!!!
        fixed_tokens = { lex: Token(f'{lex}', G[lex]) for lex in '| * ( ) ε'.split() }
        for char in text:
            # if skip_whitespaces and char.isspace():
            #     continue
            # # Your code here!!!
            if blen:
                if char == '\\':
                    blen=True
                    countblen+=1
                    continue
                else:
                    lex=lex+char
                    countblen-=1
                    if countblen>0:
                        continue
                    else:
                        blen=False
                        tokens.append(Token(lex,G['symbol']))
                        lex=''
                        continue
            if char == '\\':
                blen=True
                countblen+=1
                continue
            try:
                token = fixed_tokens[char]
            except:
                token = Token(char,G['symbol'])
            tokens.append(token)
            
        tokens.append(Token('$', G.EOF))
        return tokens