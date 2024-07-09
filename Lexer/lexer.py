from cmp.utils import Token,UnknownToken
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
            r = Regex(regex)
            
            a,states = State.from_nfa(r.automaton,get_states=True)
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
    
        
    def _walk(self, string,line,column):
        state = self.automaton
        final = state if state.final else None
        final_lex = lex = ''
        
        for symbol in string:
            if symbol=='\n':
                symbol =' '
                column = 1
                line +=1
            try:
                state = state.transitions[symbol][0]
                lex += symbol
                if state.final:
                    final_lex = lex
                    final = state
            except KeyError:
                column+=len(final_lex)
                return final, final_lex,line,column
            
        column+=len(final_lex)
        return final, final_lex,line,column

    def _tokenize(self, text):
        line =1
        column=1
        while len(text)>0:
            if text == 0:
                break
            state_final,final,line,column = self._walk(text,line,column)
            if state_final is None:
                yield final,None,line,column
            min_tag = 10000
            for state in state_final.state:
                if state.final:
                    n,token_type = state.tag
                    if n < min_tag:
                        min_tag = n
                        final_type = token_type

            text = text[len(final):]
            yield final,final_type,line,column
        
        yield '$', self.eof,line,column
    
    def __call__(self, text):
        return [ Token(lex, ttype,line,column) if ttype is not None else UnknownToken(lex, line, column) for lex, ttype,line,column in self._tokenize(text) ]