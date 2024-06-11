from cmp.pycompiler import *
from pprint import pprint
from cmp.automata import *

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




class ShiftReduceParser:

    SHIFT = 'SHIFT'
    REDUCE = 'REDUCE'
    OK = 'OK'

    def __init__(self, G, verbose=False):
        self.G = G
        self.verbose = verbose
        self.action = {}
        self.goto = {}
        self._build_parsing_table()

    def _build_parsing_table(self):
        raise NotImplementedError()

    def __call__(self, w, get_shift_reduce=False):
        stack = [0]
        cursor = 0
        output = []
        operations = []
        while True:
            state = stack[-1]
            lookahead = w[cursor]

            if(state, lookahead) not in self.action:
                excepted_char = ''

                for (state1, i) in self.action.keys():
                    if i.IsTerminal and state1 == state:
                        excepted_char += str(i) + ', '
                parsed = ' '.join([str(m)
                                    for m in stack if not str(m).isnumeric()])
                message_error = f'It was expected "{excepted_char}" received "{lookahead}" after {parsed}'
                print("\nError. Aborting...")
                print('')
                print("\n", message_error)
                return None

            if self.action[state, lookahead] == self.OK:
                action = self.OK
            else:
                action, tag = self.action[state, lookahead]
            if action == self.SHIFT:
                operations.append(self.SHIFT)
                stack += [lookahead, tag]
                cursor += 1
            elif action == self.REDUCE:
                operations.append(self.REDUCE)
                output.append(tag)
                head, body = tag
                for symbol in reversed(body):

                    stack.pop()

                    assert stack.pop() == symbol
                    state = stack[-1]

                goto = self.goto[state, head]
                stack += [head, goto]
            elif action == self.OK:
                stack.pop()
                assert stack.pop() == self.G.startSymbol
                assert len(stack) == 1
                return output if not get_shift_reduce else(output, operations)
            else:
                raise Exception('Invalid action!!!')

class LR1Parser(ShiftReduceParser):
    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)

        automaton = build_LR1_automaton(G)
        for i, node in enumerate(automaton):
            if self.verbose: print(i, '\t', '\n\t '.join(str(x) for x in node.state), '\n')
            node.idx = i

        for node in automaton:
            idx = node.idx
            for item in node.state:
                print('current item', item)

                if  item.NextSymbol and item.NextSymbol.IsTerminal:
                    self._register(self.action, (idx, item.NextSymbol), (self.SHIFT,node.get(item.NextSymbol.Name).idx))
                elif not item.NextSymbol and not item.production.Left == G.startSymbol:
                    for lookahead in item.lookaheads:
                        self._register(self.action, (idx, lookahead), (self.REDUCE, item.production))

                elif item.IsReduceItem and item.production.Left == G.startSymbol and not item.NextSymbol:
                    self._register(self.action, (idx, G.EOF), self.OK)

                else:
                    self._register(self.goto, (idx, item.NextSymbol), node.get(item.NextSymbol.Name).idx)


    @staticmethod
    def _register(table, key, value):
        assert key not in table or table[key] == value, 'Shift-Reduce or Reduce-Reduce conflict!!!'
        table[key] = value

    @staticmethod
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

    @staticmethod
    def compress(items):
        centers = {}

        for item in items:
            center = item.Center()
            try:
                lookaheads = centers[center]
            except KeyError:
                centers[center] = lookaheads = set()
            lookaheads.update(item.lookaheads)

        return { Item(x.production, x.pos, set(lookahead)) for x, lookahead in centers.items() }

    @staticmethod
    def closure_lr1(items, firsts):
        closure = ContainerSet(*items)

        changed = True
        while changed:
            changed = False
            new_items = ContainerSet()
            for x in closure:
                expanded=expand(x, firsts)
                new_items.update(ContainerSet(*expanded))

            changed = closure.update(new_items)

        return compress(closure)


    def goto_lr1(items, symbol, firsts=None, just_kernel=False):
        assert just_kernel or firsts is not None, '`firsts` must be provided if `just_kernel=False`'
        items = frozenset(item.NextItem() for item in items if item.NextSymbol == symbol)
        return items if just_kernel else closure_lr1(items, firsts)


    @staticmethod
    def build_LR1_automaton(G):
        assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'

        firsts = compute_firsts(G)
        firsts[G.EOF] = ContainerSet(G.EOF)

        start_production = G.startSymbol.productions[0]
        start_item = Item(start_production, 0, lookaheads=(G.EOF,))
        start = frozenset([start_item])

        closure = closure_lr1(start, firsts)
        automaton = State(frozenset(closure), True)
        pending = [ start ]
        visited = { start: automaton }
        while pending:
            current = pending.pop()
            current_state = visited[current]
            new_closure = closure_lr1(current_state.state, firsts)
            for new_item in new_closure:
                for symbol in G.terminals + G.nonTerminals:
                    next_state = None
                    if symbol.Name in current_state.transitions:
                        continue
                    if new_item.NextSymbol == symbol:
                        next_state = goto_lr1(new_closure, symbol, firsts=firsts)


                        if next_state:
                            frozen = frozenset(next_state)

                            if not frozen in visited:
                                pending.append(frozen)
                                new_state = State(frozen, True)
                                visited[frozen] = new_state
                                current_state.add_transition(symbol.Name, new_state)
                            else:
                                current_state.add_transition(symbol.Name, visited[frozen])

        automaton.set_formatter(multiline_formatter)
        return automaton
