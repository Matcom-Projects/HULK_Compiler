from Lexer.nfa_dfa import DFA,NFA,nfa_to_dfa
from cmp.utils import DisjointSet

def automata_union(a1, a2):
    transitions = {}
    
    start = 0
    d1 = 1
    d2 = a1.states + d1
    final = a2.states + d2
    
    for (origin, symbol), destinations in a1.map.items():
        ## Relocate a1 transitions ...
        # Your code here
        newDestinations = []
        for item in destinations:
            newDestinations.append(item + d1)

        a = { (origin + d1, symbol): newDestinations }
        transitions.update(a)

    for (origin, symbol), destinations in a2.map.items():
        ## Relocate a2 transitions ...
        # Your code here
        newDestinations = []
        for item in destinations:
            newDestinations.append(item + d2)

        a = { (origin + d2, symbol): newDestinations }
        transitions.update(a)
    
    ## Add transitions from start state ...
    # Your code here
    startList = [a1.start + d1,a2.start + d2]
    a = { (start,''): startList }
    transitions.update(a)
    
    ## Add transitions to final state ...
    # Your code here
    finalList = [final]
    for item in a1.finals:
        a = { (item + d1,''): finalList }
        transitions.update(a)

    for item in a2.finals:
        a = { (item + d2,''): finalList }
        transitions.update(a)
            
    states = a1.states + a2.states + 2
    finals = { final }
    
    return NFA(states, finals, transitions, start)


def automata_concatenation(a1, a2):
    transitions = {}
    
    start = 0
    d1 = 0
    d2 = a1.states + d1
    final = a2.states + d2
    
    for (origin, symbol), destinations in a1.map.items():
        ## Relocate a1 transitions ...
        # Your code here
        newDest = []
        for item in destinations:
            newDest.append(item + d1)
            
        a = {(origin + d1,symbol):newDest}
        transitions.update(a)

    for (origin, symbol), destinations in a2.map.items():
        ## Relocate a2 transitions ...
        # Your code here
        newDest = []
        for item in destinations:
            newDest.append(item + d2)
            
        a = { (origin+d2,symbol):newDest }
        transitions.update(a)
    
    ## Add transitions to final state ...
    # Your code here
    for item in a1.finals:
        a = { (item + d1,''):[a2.start + d2] }
        transitions.update(a)
        
    for item in a2.finals:
        a = {(item + d2,''):[final]}
        transitions.update(a)
            
    states = a1.states + a2.states + 1
    finals = { final }
    
    return NFA(states, finals, transitions, start)



def automata_closure(a1):
    transitions = {}
    
    start = 0
    d1 = 1
    final = a1.states + d1
    
    for (origin, symbol), destinations in a1.map.items():
        ## Relocate automaton transitions ...
        # Your code here
        newDestinations = []
        for item in destinations:
            newDestinations.append(item + d1)

        a = { (origin + d1, symbol): newDestinations }
        transitions.update(a)
    
    ## Add transitions from start state ...
    # Your code here
    a = { (start,''): [a1.start + d1,final] }
    transitions.update(a)

    
    ## Add transitions to final state and to start state ...
    # Your code here
    for item in a1.finals:
        a = { (item + d1,''): [final] }
        transitions.update(a)
    
    a = { (final,''): [start] }
    transitions.update(a)
            
    states = a1.states +  2
    finals = { final }
    
    return NFA(states, finals, transitions, start)

def distinguish_states(group, automaton, partition):
    split = {}
    vocabulary = tuple(automaton.vocabulary)

    for member in group:
        for prt in split.keys():
            for symbol in vocabulary:
                try:
                    t_member = automaton.transitions[member.value][symbol][0]
                    t_member = partition[t_member].representative
                except KeyError:
                    t_member = -1
                try:
                    t_prt = automaton.transitions[prt][symbol][0]
                    t_prt = partition[t_prt].representative
                except KeyError:
                    t_prt = -1
                if not t_member == t_prt:
                    break
            else:
                split[prt].append(member.value)
                break
        else:
            split[member.value] = [member.value]

    return [group for group in split.values()]


def state_minimization(automaton):
    partition = DisjointSet(*range(automaton.states))

    ## partition = { NON-FINALS | FINALS }
    if len(automaton.finals) < automaton.states - 1:
        partition.merge(
            [
                state
                for state in range(automaton.states)
                if not state in automaton.finals
            ]
        )
    if len(automaton.finals) > 1:
        partition.merge(list(automaton.finals))

    while True:
        new_partition = DisjointSet(*range(automaton.states))

        ## Split each group if needed (use distinguish_states(group, automaton, partition))
        for group in partition.groups:
            for new_group in distinguish_states(group, automaton, partition):
                if len(new_group) > 1:
                    new_partition.merge(new_group)

        if len(new_partition) == len(partition):
            break

        partition = new_partition

    return partition


def automata_minimization(automaton):
    partition = state_minimization(automaton)

    states = [s for s in partition.representatives]

    transitions = {}
    for i, state in enumerate(states):
        ## origin = ???
        origin = state.value
        for symbol, destinations in automaton.transitions[origin].items():
            trans = states.index(partition[destinations[0]].representative)

            try:
                transitions[i, symbol]
                assert False
            except KeyError:
                transitions[i, symbol] = trans

    ## finals = ???
    ## start  = ???
    finals = [i for i in range(len(states)) if states[i].value in automaton.finals]
    start = states.index(partition[automaton.start].representative)

    return DFA(len(states), finals, transitions, start)