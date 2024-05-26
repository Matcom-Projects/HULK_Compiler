from cmp.pycompiler import *



item = Item(G.Productions[0], 0, lookaheads=[G.EOF, plus])
print('item:', item)



def compute_firsts(G):
    firsts = { nt: ContainerSet() for nt in G.nonTerminals }

    change = True
    while change:
        change = False
        for production in G.Productions:
            X = production.Left
            alpha = production.Right

            local_first = compute_local_first(firsts, alpha)
            change |= firsts[X].update(local_first)

    return firsts

def compute_local_first(firsts, alpha):
    first = ContainerSet()

    for symbol in alpha:
        if symbol.IsTerminal:
            first.add(symbol)
            return first
        elif symbol.IsNonTerminal:
            first.update(firsts[symbol])
            if not firsts[symbol].contains_epsilon:
                return first
        else:
            raise ValueError("Symbol is neither terminal nor non-terminal")

    first.set_epsilon()
    return first

firsts = compute_firsts(G)
firsts[G.EOF] = ContainerSet(G.EOF)

def expand(item, firsts):
    next_symbol = item.NextSymbol
    if next_symbol is None or not next_symbol.IsNonTerminal:
        return []
    
    lookaheads = ContainerSet()
    
    for i in item.Preview():
        lookaheads.update(compute_local_first(firsts, i))
        
    
    assert not lookaheads.contains_epsilon
    productions = next_symbol.productions

    return [Item(production, 0, lookaheads) for production in productions]

for x in expand(item, firsts) :
    print(x)
assert str(expand(item, firsts)) == "[A -> .int+A, {'='}, A -> .int, {'='}]"
