from nfa_dfa import DFA,NFA,nfa_to_dfa
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
    split = []
    vocabulary = tuple(automaton.vocabulary)
    myPartition = DisjointSet(*range(len(group)))

    for i in range(0,len(group)):
        for j in range(i+1,len(group)):
            for symbol in vocabulary:
                a = automaton.transitions[group[i].value][symbol][0]
                b = automaton.transitions[group[j].value][symbol][0]

                if partition[a].representative != partition[b].representative:
                    break
            else:
                myPartition.merge([i,j])

    for item in myPartition.groups:
        temp =[]
        for i in item:
            temp.append(group[i.value].value)
        split.append(temp)

    return split
            
def state_minimization(automaton):
    partition = DisjointSet(*range(automaton.states))
    
    ## partition = { NON-FINALS | FINALS }
    # Your code here
    partition.merge(automaton.finals)

    start = automaton.start

    for item in range(0,automaton.states):
        if item not in automaton.finals:
            partition.merge([start,item])
    
    while True:
        new_partition = DisjointSet(*range(automaton.states))
        
        ## Split each group if needed (use distinguish_states(group, automaton, partition))
        # Your code here
        for group in partition.groups:
            for item in distinguish_states(group,automaton,partition):
                new_partition.merge(item)

        if len(new_partition) == len(partition):
            break

        partition = new_partition
        
    return partition

def automata_minimization(automaton):
    partition = state_minimization(automaton)
    
    states = [s for s in partition.representatives]
    
    transitions = {}
    finals = []
    for i, state in enumerate(states):
        ## origin = ???
        # Your code here
        origin = state.value
        if origin in automaton.finals:
            finals.append(i)
        if origin == automaton.start:
            start = i
        for symbol, destinations in automaton.transitions[origin].items():
            # Your code here
            
            try:
                transitions[i,symbol]
                assert False
            except KeyError:
                # Your code here
                a = { (i,symbol): states.index(partition[destinations[0]].representative) }
                transitions.update(a)
                pass
    
    ## finals = ???
    ## start  = ???
    # Your code here
    
    return DFA(len(states), finals, transitions, start)