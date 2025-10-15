import re
from collections import defaultdict, deque

class LRParserGenerator:
    def __init__(self, inputPath):
        self.non_terminals = []
        self.terminals = []
        self.syn = []
        self.__rules = {}
        self.productions = []
        self.__parse_grammar(inputPath)

        self.__first_table = self.__compute_first_table()

        self.action_table = defaultdict(dict)
        self.goto_table = defaultdict(dict)

    def __parse_grammar(self, inputPath):
        lines = open(inputPath, "r", encoding="utf-8").readlines()

        current_nonterminal = None

        for line in lines:
            line = line.strip("\n")
            if not line:
                continue

            if line.startswith("%V"):
                self.non_terminals = re.findall(r"<[^>]+>", line)
            elif line.startswith("%T"):
                self.terminals = line.split()[1:]
            elif line.startswith("%Syn"):
                self.syn = line.split()[1:]
            elif re.match(r"^<[^>]+>$", line):
                current_nonterminal = line
                if current_nonterminal not in self.__rules:
                    self.__rules[current_nonterminal] = []
            elif current_nonterminal:
                if line == "$":
                    self.__rules[current_nonterminal].append([])
                else:
                    self.__rules[current_nonterminal].append(line.split())


        for l, r_list in self.__rules.items():
            for r in r_list:
                self.productions.append((l, r))


    def __compute_first_table(self):
        first = defaultdict(set)

        for t in self.terminals:
            first[t].add(t)

        for nt in self.__rules:
            _ = first[nt]

        for non_terminal, productions in self.__rules.items():
            for production in productions:
                if not production:
                    first[non_terminal].add("$")

        changed = True
        while changed:
            changed = False
            for nonTerminal, productions in self.__rules.items():
                before = len(first[nonTerminal])
                for production in productions:
                    if not production:
                        continue
                    for symbol in production:
                        first[nonTerminal].update(first[symbol] - {"$"})
                        if "$" not in first[symbol]:
                            break
                    else:
                        first[nonTerminal].add("$")
                if len(first[nonTerminal]) > before:
                    changed = True
        return first


    def __compute_clousure(self, items):
        closure_set = set(items)
        changed = True

        def first_of_sequence(seq):
            res = set()
            for sym in seq:
                if sym == "$":
                    res.add("$")
                    break
                sym_first = set(self.__first_table.get(sym, {sym}))
                res.update(sym_first - {"$"})
                if "$" not in sym_first:
                    break
            else:
                res.add("$")
            return res

        while changed:
            changed = False
            new_items = set()
            for (A, left, right, lookahead) in list(closure_set):
                if right and right[0] in self.non_terminals:
                    B = right[0]
                    rest = list(right[1:]) + [lookahead]
                    first_rest = first_of_sequence(rest)
                    for prod in self.__rules[B]:
                        prod_tuple = tuple(prod)
                        for b in first_rest:
                            new_item = (B, tuple(), prod_tuple, b)
                            if new_item not in closure_set and new_item not in new_items:
                                new_items.add(new_item)
            if new_items:
                closure_set.update(new_items)
                changed = True
        return closure_set

    def __goto(self, items, symbol):
        moved = set()
        for (A, left, right, lookahead) in items:
            if right and right[0] == symbol:
                moved.add((A, tuple(left) + (symbol,), tuple(right[1:]), lookahead))
        if not moved:
            return set()
        return self.__compute_clousure(moved)


    def __compute_states_transitions(self):
        start = self.non_terminals[0]
        augmented_start = "<%>"
        self.__rules[augmented_start] = [[start]]
        all_nonterminals = [augmented_start] + self.non_terminals

        I0 = self.__compute_clousure({(augmented_start, tuple(), (start,), "$")})

        states = [I0]
        transitions = {}
        state_queue = deque([I0])

        while state_queue:
            state = state_queue.popleft()
            for symbol in all_nonterminals + self.terminals:
                next_state = self.__goto(state, symbol)
                if not next_state:
                    continue
                if next_state not in states:
                    states.append(next_state)
                    state_queue.append(next_state)
                transitions[(states.index(state), symbol)] = states.index(next_state)
        return states, transitions


    def build_tables(self):
        states, transitions = self.__compute_states_transitions()

        for i, state in enumerate(states):
            for (A, left, right, lookahead) in state:
                if right:
                    symbol = right[0]
                    if symbol in self.terminals:
                        t = transitions.get((i, symbol))
                        if t is not None:
                            self.action_table[i][symbol] = f"S{t}"
                    elif symbol in self.non_terminals:
                        t = transitions.get((i, symbol))
                        if t is not None:
                            self.goto_table[i][symbol] = t
                else:
                    if A == "<%>":
                        self.action_table[i]["$"] = "acc"
                    else:
                        # Find corresponding production index
                        for idx, (lhs, rhs) in enumerate(self.productions):
                            if lhs == A and tuple(rhs) == left:
                                self.action_table[i][lookahead] = f"R{idx}"
                                break

    def print_grammar(self):
        print("Productions:")
        for i, (left, right) in enumerate(self.productions):
            production = f"{left} -> {' '.join(right) if right else '$'}"
            print(f"{i}: {production}")
        print("\nNon-terminals:", self.non_terminals)
        print("Terminals:", self.terminals)
        print("Synchronized token:", self.syn)

    def print_tables(self):
        print("ACTION TABLE:")
        for state, actions in sorted(self.action_table.items()):
            print(f"State {state}: {actions}")
        print("\nGOTO TABLE:")
        for state, gotos in sorted(self.goto_table.items()):
            print(f"State {state}: {gotos}")


if __name__ == "__main__":
    lr = LRParserGenerator("./data/kanon_gramatika.txt")
    lr.build_tables()
    lr.print_tables()
