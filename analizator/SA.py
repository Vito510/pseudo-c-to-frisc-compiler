import sys
import pickle


class ParseTreeNode:
    def __init__(self, label, is_terminal=False, line=None, lexeme=None):
        self.label = label
        self.is_terminal = is_terminal
        self.line = line
        self.lexeme = lexeme
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def pretty_print(self, indent=0, file=None):
        prefix = " " * indent
        if self.is_terminal:
            if self.line is not None:
                line = f"{prefix}{self.label} {self.line} {self.lexeme}\n"
            else:
                line = f"{prefix}{self.label}\n"
        else:
            line = f"{prefix}{self.label}\n"

        if file:
            file.write(line)
        else:
            print(line, end='')

        for child in self.children:
            child.pretty_print(indent + 1, file=file)

    def write_to_file(self, filename):
        with open(filename, "w", encoding="utf-8") as f:
            self.pretty_print(file=f)
        print(f"Tree written to file: {filename}", file=sys.stderr)
    
    def print_to_stdout(self):
        """Print the parse tree to stdout"""
        self.pretty_print(file=sys.stdout)


class LRParser:
    def __init__(self, productions, action_table, goto_table, uniform_sequence, sync_symbols, start_state=0):
        self.productions = productions
        self.action_table = action_table
        self.goto_table = goto_table
        self.uniform_sequence = list(uniform_sequence)
        self.sync_symbols = set(sync_symbols)
        self.start_state = start_state

        if not self.uniform_sequence or self.uniform_sequence[-1][0] != "$":
            self.uniform_sequence.append(("$", None, "$"))

    def report_error(self, state, symbol, line, lexeme):
        expected = sorted(self.action_table.get(state, {}).keys())
        expected_str = ", ".join(expected) if expected else "(nema očekivanih znakova)"
        line_str = str(line) if line is not None else "?"
        print(f"Linija {line_str}: sintaksna pogreška; očekivano: {expected_str}; pronađeno: {symbol} {lexeme}", file=sys.stderr)

    def recover_from_error(self, states, nodes, input_idx):
        n = len(self.uniform_sequence)

        while input_idx < n:
            sym, line, lexeme = self.uniform_sequence[input_idx]

            if sym == "$":
                raise SyntaxError("Dosegnut kraj datoteke bez oporavka")

            if sym in self.sync_symbols:
                temp_states = list(states)
                temp_nodes = list(nodes)
                
                while temp_states:
                    state = temp_states[-1]
                    if sym in self.action_table.get(state, {}):
                        return input_idx, temp_states, temp_nodes
                    temp_states.pop()
                    if temp_nodes:
                        temp_nodes.pop()
                
                input_idx += 1
            else:
                input_idx += 1

        raise SyntaxError("Nema sinkronizacijskog znaka")

    def parse(self):
        states = [self.start_state]
        nodes = []
        input_idx = 0

        while True:
            if input_idx >= len(self.uniform_sequence):
                return None

            symbol, line, lexeme = self.uniform_sequence[input_idx]
            state = states[-1]
            action = self.action_table.get(state, {}).get(symbol)

            if action is None:
                self.report_error(state, symbol, line, lexeme)
                try:
                    input_idx, states, nodes = self.recover_from_error(states, nodes, input_idx)
                    continue
                except SyntaxError as e:
                    print(f"Prekid parsiranja: {e}", file=sys.stderr)
                    return None

            if action == "acc":
                return nodes[0] if nodes else None

            if action.startswith("S"):
                new_state = int(action[1:])
                leaf = ParseTreeNode(symbol, is_terminal=True, line=line, lexeme=lexeme)
                
                nodes.append(leaf)
                states.append(new_state)
                input_idx += 1
                continue

            if action.startswith("R"):
                prod_idx = int(action[1:])
                lhs, rhs = self.productions[prod_idx]
                rhs_len = len(rhs)

                children = []
                if rhs_len == 0:
                    eps_leaf = ParseTreeNode("$", is_terminal=True)
                    children.append(eps_leaf)
                else:
                    for _ in range(rhs_len):
                        if not states or len(states) <= 1:
                            return None
                        states.pop()
                        if nodes:
                            children.append(nodes.pop())
                    children.reverse()

                new_node = ParseTreeNode(lhs, is_terminal=False)
                for c in children:
                    new_node.add_child(c)

                goto_state = self.goto_table.get(states[-1], {}).get(lhs)
                if goto_state is None:
                    self.report_error(states[-1], lhs, line, lexeme)
                    try:
                        input_idx, states, nodes = self.recover_from_error(states, nodes, input_idx)
                        continue
                    except SyntaxError as e:
                        print(f"Prekid parsiranja: {e}", file=sys.stderr)
                        return None

                nodes.append(new_node)
                states.append(goto_state)
                continue

            return None


def parse_uniform_sequence(input_source=None):
    lines = [line + "\n" for line in sys.stdin.read().split("\n")[:-1]]
    
    data = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 1:
            symbol = parts[0]
            line_num = int(parts[1]) if len(parts) >= 2 else None
            lexeme = parts[2] if len(parts) >= 3 else ""
            data.append((symbol, line_num, lexeme))
    
    return data


def load_tables(action_path, goto_path):
    with open(action_path, 'rb') as f:
        action_table = pickle.load(f)
    with open(goto_path, 'rb') as f:
        goto_table = pickle.load(f)
    return action_table, goto_table

def load_grammar(grammar_path):
    with open(grammar_path, 'rb') as f:
        productions, syn = pickle.load(f)
    return productions, syn


if __name__ == "__main__":    
    action_table, goto_table = load_tables("action_table.pkl", "goto_table.pkl")
    productions, syn = load_grammar("grammar.pkl")
    uniform_seq = parse_uniform_sequence()

    lr = LRParser(
        productions=productions,
        action_table=action_table,
        goto_table=goto_table,
        uniform_sequence=uniform_seq,
        sync_symbols=syn
    )

    root = lr.parse()
    root.print_to_stdout()