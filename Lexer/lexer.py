from cmp.utils import Token
from cmp.automata import State
from Lexer.regex import *

class Lexer:
    def __init__(self, table, eof):
        self.eof = eof
        self.regexs = self._build_regexs(table)
        self.automaton = self._build_automaton()
    
    def _build_regexs(self, table):
        regexs = []
        for n, (token_type, regex) in enumerate(table):
            # Your code here!!!
            # - Remember to tag the final states with the token_type and priority.
            # - <State>.tag might be useful for that purpose ;-)
            a = Regex(regex).automaton
            
            a,states = State.from_nfa(a,get_states=True)
            for state in states:
                if state.final:
                    state.tag = (n,token_type)
            regexs.append(a)
        return regexs
    
    def _build_automaton(self):
        start = State('start')
        # Your code here!!!
        for state in self.regexs:
            start.add_epsilon_transition(state)
        return start.to_deterministic()
    
        
    def _walk(self, string):
        state = self.automaton
        final = state if state.final else None
        final_lex = lex =''
        
        for symbol in string:
            # Your code here!!!
            if state.has_transition(symbol):
                final_lex += symbol
                state = state[symbol][0]

                if state.final:
                    final = state
                    final.lex = final_lex
            else:
                break
        
        if final:
            return final, final_lex

    def _tokenize(self, text):

        index = 0
        line = 1
        column = 1
        remaining_text = text

        for i, symbol in enumerate(text):
            if symbol == "\n":
                line+=1
                column=1 
                index += 1
            elif symbol == " ":
                column+= 1
                index += 1
            else:
                remaining_text = text[index:]
                break

    
        while text:

            try:
                final, TokenLex = self._walk(remaining_text)
            except TypeError:
                raise Exception(f"Lexer Exception: Token '{remaining_text[0]}' is not valid. ({line},{column})")

            index = len(TokenLex)
            for i, symbol in enumerate(remaining_text):
                if i < index:
                    continue

                if symbol == "\n": 
                    line+=1
                    column=1 
                    index += 1
                elif symbol == " ":
                    column+= 1
                    index += 1
                else:
                    remaining_text= remaining_text[index:]
                    break
            if final:
                yield TokenLex, final.tag, line,column

        yield '$', self.eof,line,column


        # # Your code here!!!
        # while len(text)>0:
        #     if text == 0:
        #         break
        #     state_final,final = self._walk(text)
        #     min_tag = 10000
        #     for state in state_final.state:
        #         if state.final:
        #             n,token_type = state.tag
        #             if n < min_tag:
        #                 min_tag = n
        #                 final_type = token_type

        #     text = text[len(final):]
        #     yield final,final_type,0,0
        
        # yield '$', self.eof,0,0
    
    def __call__(self, text):
        return [ Token(lex, ttype,line,column) for lex, ttype,line,column in self._tokenize(text) ]