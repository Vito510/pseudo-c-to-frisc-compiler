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
            line = line.strip()
            if line.startswith("%V"):
                self.non_terminals = re.findall(r"<[^>]+>", line)
            elif line.startswith("%T"):
                self.terminals = line.split()[1:]
            elif line.startswith("%Syn"):
                self.syn = line.split()[1]
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

        for terminal in self.terminals:
            first[terminal].add(terminal)

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

        while changed:
            changed = False
            new_items = set()
            for (nonTerminal, left, right, lookahead) in closure_set: # npr. [A -> a•Bb, a] lijevo i desno od točke
                if right and right[0] in self.non_terminals:  # prvi iza točke je neterminal
                    B = right[0]
                    rest = list(right[1:]) + [lookahead]
                    first_rest = set()
                    for symbol in rest:
                        first_rest.update(self.__first_table[symbol] if self.__first_table[symbol] else set("$"))

                    for prod in self.__rules[B]:
                        for b in first_rest:
                            new_item = (B, tuple(), tuple(prod), b)
                            if new_item not in closure_set:
                                new_items.add(new_item)
            if new_items:
                closure_set.update(new_items)
                changed = True

        return closure_set


    def __goto(self, items, symbol):
        moved = set()
        for (nonTerminal, left, right, lookahead) in items:
            if right and right[0] == symbol:
                moved.add((nonTerminal, tuple(left) + (symbol,), tuple(right[1:]), lookahead))
        return self.__compute_clousure(moved)


    def __compute_states_transitions(self):
        start = self.non_terminals[0]
        augmented_start = "<%>"
        self.__rules[augmented_start] = [[start]]
        self.non_terminals.insert(0, augmented_start)

        I0 = self.__compute_clousure({(augmented_start, tuple(), (start,), "$")})

        states = [I0]
        transitions = {}

        state_queue = deque([I0])

        while state_queue:
            state = state_queue.popleft()
            for symbol in self.non_terminals + self.terminals:
                computed_state = self.__goto(state, symbol)
                if not computed_state:
                    continue
                if computed_state not in states:
                    states.append(computed_state)
                    state_queue.append(computed_state)
                transitions[(states.index(state), symbol)] = states.index(computed_state)
        return states, transitions


    def build_tables(self):
        states, transitions = self.__compute_states_transitions()

        for i, state in enumerate(states):
            for (nonTerminal, left, right, lookahead) in state:
                if right:
                    symbol = right[0]
                    if symbol in self.terminals:
                        current_transition = transitions.get((i, symbol))
                        if current_transition is not None:
                            self.action_table[i][symbol] = f"S{current_transition}"
                            
                    elif symbol in self.non_terminals:
                        current_transition = transitions.get((i, symbol))
                        if current_transition is not None:
                            self.goto_table[i][symbol] = current_transition
                else:
                    if nonTerminal == "<%>":
                        self.action_table[i]["$"] = "acc"
                    else:
                        prod_index = self.productions.index((nonTerminal, list(left)))
                        # prod = f"{nonTerminal} | {' '.join(left) if left else '$'}"
                        self.action_table[i][lookahead] = f"R{prod_index}"

    def print_tables(self):
        print("ACTION TABLE:")
        for state, actions in self.action_table.items():
            print(f"State {state}: {actions}")
        print("\nGOTO TABLE:")
        for state, gotos in self.goto_table.items():
            print(f"State {state}: {gotos}")



if __name__ == "__main__":
    lr = LRParserGenerator("./data/kanon_gramatika.txt")
    lr.build_tables()
    lr.print_tables()