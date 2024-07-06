import pydot
from cmp.utils import ContainerSet

class NFA:
    def __init__(self, states, finals, transitions, start=0):
        self.states = states
        self.start = start
        self.finals = set(finals)
        self.map = transitions
        self.vocabulary = set()
        self.transitions = { state: {} for state in range(states) }
        
        for (origin, symbol), destinations in transitions.items():
            assert hasattr(destinations, '__iter__'), 'Invalid collection of states'
            self.transitions[origin][symbol] = destinations
            self.vocabulary.add(symbol)
            
        self.vocabulary.discard('')
        
    def epsilon_transitions(self, state):
        assert state in self.transitions, 'Invalid state'
        try:
            return self.transitions[state]['']
        except KeyError:
            return ()
            
    def graph(self):
        G = pydot.Dot(rankdir='LR', margin=0.1)
        G.add_node(pydot.Node('start', shape='plaintext', label='', width=0, height=0))

        for (start, tran), destinations in self.map.items():
            tran = 'ε' if tran == '' else tran
            G.add_node(pydot.Node(start, shape='circle', style='bold' if start in self.finals else ''))
            for end in destinations:
                G.add_node(pydot.Node(end, shape='circle', style='bold' if end in self.finals else ''))
                G.add_edge(pydot.Edge(start, end, label=tran, labeldistance=2))

        G.add_edge(pydot.Edge('start', self.start, label='', style='dashed'))
        return G

    def _repr_svg_(self):
        try:
            return self.graph().create_svg().decode('utf8')
        except:
            pass



class DFA(NFA):
    
    def __init__(self, states, finals, transitions, start=0):
        assert all(isinstance(value, int) for value in transitions.values())
        assert all(len(symbol) > 0 for origin, symbol in transitions)
        
        transitions = { key: [value] for key, value in transitions.items() }
        NFA.__init__(self, states, finals, transitions, start)
        self.current = start
        
    def _move(self, symbol):
        try:
            self.current = self.transitions[self.current][symbol][0]
            return 1
        except:
            return 0
    
    def _reset(self):
        self.current = self.start
        
    def recognize(self, string):
        resp = self.current in self.finals
        for i in string:
            if self._move(i):
                resp = self.current in self.finals
            else:
                return 0
        self.current = self.start
        return resp
    
def move(automaton, states, symbol):
    moves = set()
    for state in states:
        try:
            for item in automaton.transitions[state][symbol]:
                moves.add(item)
        except:
                pass
    return moves

def epsilon_closure(automaton, states):
    pending = [ s for s in states ] 
    closure = { s for s in states } 

    while pending:
        state = pending.pop()
        closure.add(state)
        try:
            for item in automaton.transitions[state]['']:
                pending.append(item)
        except KeyError:
                        pass
                
    return ContainerSet(*closure)

def nfa_to_dfa(automaton):
    transitions = {}
    
    start = epsilon_closure(automaton, [automaton.start])
    start.id = 0
    start.is_final = any(s in automaton.finals for s in start)
    states = [ start ]

    pending = [ start ]
    while pending:
        state = pending.pop()
        
        for symbol in automaton.vocabulary:
            # Your code here
            go_to = move(automaton,state,symbol)
            e_closure = epsilon_closure(automaton,go_to)

            epsilonClosure = ContainerSet(*e_closure)
            if epsilonClosure not in states and len(epsilonClosure):
                epsilonClosure.id = len(states)
                epsilonClosure.is_final = any(s in automaton.finals for s in epsilonClosure)
                states.append(epsilonClosure)
                pending.append(epsilonClosure)
            # ...

            try:
                transitions[state.id, symbol]
                assert False, 'Invalid DFA!!!'
            except KeyError:
                if len(epsilonClosure):
                    a ={ (state.id,symbol): states.index(epsilonClosure)}
                    transitions.update(a)
    
    finals = [ state.id for state in states if state.is_final ]
    dfa = DFA(len(states), finals, transitions)
    return dfa