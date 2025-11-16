import re
from collections import defaultdict, deque
import pickle


class LRParserGenerator:    
    def __init__(self, inputPath):
        self.non_terminals = []
        self.terminals = []
        self.syn = []
        self.__rules = {}
        self.productions = []
        self.__parse_grammar(inputPath)

        self.action_table = defaultdict(dict)
        self.goto_table = defaultdict(dict)

        self._first_cache = {}
        self._computing = set()
       
    def __parse_grammar(self, inputPath):
        lines = open(inputPath, "r", encoding="utf-8").readlines()
        
        current_nonterminal = None

        for line in lines:
            line = line.strip("\n")
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
                if line.strip() == "$":
                    self.__rules[current_nonterminal].append([])
                else:
                    self.__rules[current_nonterminal].append(line.split())
        
        for l, r_list in self.__rules.items():
            for r in r_list:
                self.productions.append((l, tuple(r)))

    def __compute_first(self, symbols):  
        result = set()
        
        for symbol in symbols:
            if symbol in self.terminals or symbol == "$":
                result.add(symbol)
                return result
            
            if symbol in self.non_terminals:
                symbol_first = self.__first_of_nonterminal(symbol)
                result.update(symbol_first - {"$"})
                
                if "$" not in symbol_first:
                    return result
        
        result.add("$")
        return result
    
    def __first_of_nonterminal(self, nonterminal):        
        if nonterminal in self._first_cache:
            return self._first_cache[nonterminal]
        if nonterminal in self._computing:
            return set()
        
        self._computing.add(nonterminal)
        first_set = set()
        
        if nonterminal not in self.__rules:
            self._computing.remove(nonterminal)
            return set()
        for production in self.__rules[nonterminal]:
            if not production:
                first_set.add("$")
            else:
                prod_first = self.__compute_first(production)
                first_set.update(prod_first)
        
        self._computing.remove(nonterminal)
        self._first_cache[nonterminal] = first_set
        return first_set

    def __compute_closure(self, items):
        closure_list = list(items)
        seen = set(items)
        
        idx = 0
        while idx < len(closure_list):
            nt, left, right, lookahead = closure_list[idx]
            
            if right and right[0] in self.non_terminals:
                a = right[0]

                beta_a = list(right[1:]) + [lookahead]
                first_beta_a = self.__compute_first(beta_a)
                
                if a in self.__rules:
                    for production in self.__rules[a]:
                        for b in sorted(first_beta_a):
                            new_item = (a, tuple(), tuple(production), b)
                            if new_item not in seen:
                                closure_list.append(new_item)
                                seen.add(new_item)
            idx += 1
        
        return frozenset(closure_list)

    def __goto(self, items, symbol):
        moved = []
        for item in sorted(items):
            nt, left, right, lookahead = item
            if right and right[0] == symbol:
                new_left = left + (symbol,)
                new_right = right[1:]
                moved.append((nt, new_left, new_right, lookahead))
        
        if not moved:
            return frozenset()
        
        return self.__compute_closure(moved)

    def __compute_canonical_collection(self):
        start_symbol = self.non_terminals[0]
        augmented_start = "<%>"
        self.__rules[augmented_start] = [[start_symbol]]
        self.non_terminals.insert(0, augmented_start)
        
        initial_item = (augmented_start, tuple(), (start_symbol,), "$")
        initial_state = self.__compute_closure([initial_item])
        
        states = [initial_state]
        transitions = {}
        queue = deque([initial_state])
        
        while queue:
            current_state = queue.popleft()
            current_idx = states.index(current_state)
            
            for symbol in self.non_terminals + self.terminals:
                next_state = self.__goto(current_state, symbol)
                
                if not next_state:
                    continue
                
                if next_state not in states:
                    states.append(next_state)
                    queue.append(next_state)
                
                next_idx = states.index(next_state)
                transitions[(current_idx, symbol)] = next_idx
        
        return states, transitions

    def build_tables(self):
        states, transitions = self.__compute_canonical_collection()
        
        for state_idx, state in enumerate(states):
            for item in sorted(state):
                nt, left, right, lookahead = item
                
                if right:
                    symbol = right[0]
                    
                    if symbol in self.terminals:
                        # Shift
                        if (state_idx, symbol) in transitions:
                            next_state = transitions[(state_idx, symbol)]
                            self.action_table[state_idx][symbol] = f"S{next_state}"
                    
                    elif symbol in self.non_terminals:
                        # Goto
                        if (state_idx, symbol) in transitions:
                            next_state = transitions[(state_idx, symbol)]
                            self.goto_table[state_idx][symbol] = next_state
                
                else:
                    if nt == "<%>":
                        # Accept
                        self.action_table[state_idx]["$"] = "acc"
                    else:
                        # Reduce
                        production = (nt, left)
                        if production in self.productions:
                            prod_idx = self.productions.index(production)
                            self.action_table[state_idx][lookahead] = f"R{prod_idx}"

    def save_tables(self, action_path, goto_path):
        with open(action_path, 'wb') as f:
            pickle.dump(dict(self.action_table), f)
        with open(goto_path, 'wb') as f:
            pickle.dump(dict(self.goto_table), f)

    def load_tables(self, action_path, goto_path):
        with open(action_path, 'rb') as f:
            self.action_table = pickle.load(f)
        with open(goto_path, 'rb') as f:
            self.goto_table = pickle.load(f)


if __name__ == "__main__":
    lr = LRParserGenerator("./data/syntax-rules/c-sintaksa-pravila.txt")
    # lr = LRParserGenerator("./data/syntax-rules/kanon-sintaksa-pravila.txt")
    # lr = LRParserGenerator("./data/syntax-rules/minuslang-sintaksa-pravila.txt")

    lr.build_tables()
    lr.print_productions()
    lr.print_tables()
    lr.save_tables("./data/tables/action_table.pkl", "./data/tables/goto_table.pkl")