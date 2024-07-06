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
        transitions[(origin + d1, symbol)]  = [dest + d1 for dest in destinations]

    for (origin, symbol), destinations in a2.map.items():
        ## Relocate a2 transitions ...
        # Your code here
        transitions[(origin + d2, symbol)]  = [dest + d2 for dest in destinations]
    
     ## Add transitions from start state ...
    # Your code here
    transitions[(0, '')]  = [d1, d2]
    
    ## Add transitions to final state ...
    # Your code here
    for state in range(0, a1.states):
        if state in a1.finals:
            transitions[(state + 1, '')] = [final]

    for state in range(0, a2.states):
        if state in a2.finals:
            transitions[(state + d2, '')] = [final]

    # transitions[(d2-1, '')]  = [final]
    # transitions[(final - 1, '')]  = [final]
            
    states = a1.states + a2.states + 2
    finals = { final }

    # print(transitions)
    # print(finals)
    
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
        transitions[(origin, symbol)] = destinations

    for (origin, symbol), destinations in a2.map.items():
        ## Relocate a2 transitions ...
        # Your code here
        transitions[(origin + d2, symbol)] = [dest + d2 for dest in destinations]
    
     ## Add transitions since finals states' a1 to start state's a2 ...
    # Your code here
    for state in range(0, a1.states):
        if state in a1.finals:
            transitions[(state, '')] = [d2]

    ## Add transitions to final state ...
    for state in range(0, a2.states):
        if state in a2.finals:
            try:
                transitions[(state + d2, '')] += [final]
            except KeyError:
                # Your code here
                transitions[(state + d2, '')] = [final]
            
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
        transitions[(origin + d1, symbol)] = [dest + d1 for dest in destinations]
    
    ## Add transitions from start state ...
    # Your code here
    transitions[(start, '')] = [final]
    
    ## Add transitions to final state and to start state ...
    # Your code here
    for state in range(0, a1.states):
        if state in a1.finals:
            transitions[(state + d1, '')] = [final]

    transitions[(final, '')] = [d1]
            
    states = a1.states +  2
    finals = { final }
    
    return NFA(states, finals, transitions, start)

# def distinguish_states(group, automaton, partition):
#     split = {}
#     vocabulary = tuple(automaton.vocabulary)

#     for member in group:
#         band = False
#         repr_member = partition[member.value].representative.value

#         for caract in vocabulary:
#             try:
#                 item = automaton.transitions[member.value][caract][0]
#             except KeyError:
#                 continue
            
#             repr_item = partition[item].representative.value
#             if  repr_item != repr_member:
#                 try:
#                     split[repr_item].append(member.value)
#                 except KeyError:
#                     split[repr_item] = [member.value]
#                 band = True
#                 break

#         if not band:
#             try:
#                 split[repr_member].append(member.value)
#             except KeyError:
#                 split[repr_member] = [member.value]

#     return [group for group in split.values()]


# def state_minimization(automaton):
#     partition = DisjointSet(*range(automaton.states))

#     ## partition = { NON-FINALS | FINALS }
#     if len(automaton.finals) < automaton.states - 1:
#         partition.merge(
#             [
#                 state
#                 for state in range(automaton.states)
#                 if not state in automaton.finals
#             ]
#         )
#     if len(automaton.finals) > 1:
#         partition.merge(list(automaton.finals))

#     while True:
#         new_partition = DisjointSet(*range(automaton.states))

#         ## Split each group if needed (use distinguish_states(group, automaton, partition))
#         for group in partition.groups:
#             for new_group in distinguish_states(group, automaton, partition):
#                 if len(new_group) > 1:
#                     new_partition.merge(new_group)

#         if len(new_partition) == len(partition):
#             break

#         partition = new_partition

#     return partition


# def automata_minimization(automaton):
#     partition = state_minimization(automaton)

#     states = [s for s in partition.representatives]

#     transitions = {}
#     for i, state in enumerate(states):
#         ## origin = ???
#         origin = state.value
#         for symbol, destinations in automaton.transitions[origin].items():
#             trans = states.index(partition[destinations[0]].representative)

#             try:
#                 transitions[i, symbol]
#                 assert False
#             except KeyError:
#                 transitions[i, symbol] = trans
#                 pass

#     ## finals = ???
#     ## start  = ???
#     finals = [i for i in range(len(states)) if states[i].value in automaton.finals]
#     start = states.index(partition[automaton.start].representative)

#     return DFA(len(states), finals, transitions, start)
def distinguish_states(group, automaton, partition):
    split = {}
    vocabulary = tuple(automaton.vocabulary)

    for member in group:

        ATMTransitions = automaton.transitions[member.value]

        Tags = []
        for symbol in vocabulary:
            if symbol in ATMTransitions:
                Tags.append(ATMTransitions[symbol][0])
            else:
                Tags.append(None)

        splitKey = tuple((partition[Tag].representative if Tag in partition.nodes else None) for Tag in Tags)

        try:
            split[splitKey].append(member.value)
        except KeyError:
            split[splitKey] = [member.value]

    return [group for group in split.values()]


def state_minimization(automaton):
    partition = DisjointSet(*range(automaton.states))

    ## partition = { NON-FINALS | FINALS }

    partition.merge(Ste for Ste in automaton.finals)
    partition.merge(Ste for Ste in range(automaton.states) if Ste not in automaton.finals)

    while True:
        new_partition = DisjointSet(*range(automaton.states))

        ## Split each group if needed (use distinguish_states(group, automaton, partition))

        for Group in partition.groups:
            for i in distinguish_states(Group, automaton, partition):
                new_partition.merge(i)

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

            Rep = partition[destinations[0]].representative
            RepIndex = states.index(Rep)

            try:
                transitions[i, symbol]
                assert False
            except KeyError:
                transitions[i, symbol] = RepIndex

    ## finals = ???
    ## start  = ???
    finals = []
    for i, Ste in enumerate(states):
        if Ste.value in automaton.finals:
            finals.append(i)
            
    start = states.index(partition[automaton.start].representative)

    return DFA(len(states), finals, transitions, start)