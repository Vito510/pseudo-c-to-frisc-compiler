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
            line = f"{prefix}{self.label} {self.line if self.line else ""} {self.lexeme if self.lexeme else ""}\n"
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
        print(f"Tree written to file: {filename}")


class LRParser:
    def __init__(self, productions, action_table, goto_table, uniform_sequence, symbol_table, sync_symbols, start_state=0):
        self.productions = productions
        self.action_table = action_table
        self.goto_table = goto_table
        self.uniform_sequence = list(uniform_sequence)
        self.symbol_table = symbol_table
        self.sync_symbols = set(sync_symbols)
        self.start_state = start_state

        if not self.uniform_sequence or self.uniform_sequence[-1][0] != "$":
            self.uniform_sequence.append(("$", None, "$"))

    def report_error(self, state, symbol, line, lexeme):
        expected = list(self.action_table.get(state, {}).keys())
        expected_str = ", ".join(expected) if expected else "(nema očekivanih znakova)"
        print(f"Linija {line}: sintaksna pogreška; očekivano: {expected_str}; pronađeno: {symbol} {lexeme}")

    def recover_from_error(self, states, nodes, input_idx):
        while input_idx < len(self.uniform_sequence):
            sym, line, _ = self.uniform_sequence[input_idx]
            if sym in self.sync_symbols or sym == "$":
                break
            input_idx += 1

        if input_idx >= len(self.uniform_sequence):
            raise SyntaxError("Nema sinkronizacijskog znaka")

        sync_symbol = self.uniform_sequence[input_idx][0]

        while states:
            state = states[-1]
            if sync_symbol in self.action_table.get(state, {}):
                return input_idx, states, nodes
            states.pop()
            if nodes:
                nodes.pop()

        raise SyntaxError("R.I.P")

    def parse(self):
        states = [self.start_state]
        nodes = []
        input_idx = 0

        while True:
            symbol, line, lexeme = self.uniform_sequence[input_idx]
            state = states[-1]
            action = self.action_table.get(state, {}).get(symbol)
            # print(f"Stanje: {states[-1]}, simbol: {symbol}, akcija: {action} --- stog: {states}")

            # Error
            if action is None:
                self.report_error(state, symbol, line, lexeme)
                try:
                    input_idx, states, nodes = self.recover_from_error(states, nodes, input_idx)
                except SyntaxError as e:
                    print(f"Prekid parsiranja: {e}")
                    return None
                continue

            # Accept
            if action == "acc":
                return nodes[0] if nodes else None

            # Shift
            if action.startswith("S"):
                new_state = int(action[1:])
                leaf = ParseTreeNode(symbol, is_terminal=True, line=line, lexeme=lexeme)
                
                nodes.append(leaf)
                states.append(new_state)

                input_idx += 1
                continue

            # Reduce
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
                        states.pop()
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
                    except SyntaxError as e:
                        print(f"Prekid parsiranja: {e}")
                        return None
                    continue

                nodes.append(new_node)
                states.append(goto_state)
                continue

if __name__ == "__main__":
    from LRParserGenerator import LRParserGenerator

    uniform_sequence = [
        ('a', 1, "x x x"),
        ('b', 2, "y y"),
        ('a', 3, "xx xx"),
        ('a', 4, "xx xx xx"),
        ('b', 4, "y"),
    ]

    lrgen = LRParserGenerator("./data/syntax-rules/kanon-sintaksa-pravila.txt")
    lrgen.build_tables()

    lr = LRParser(
        productions=lrgen.productions,
        action_table=lrgen.action_table,
        goto_table=lrgen.goto_table,
        uniform_sequence=uniform_sequence,
        sync_symbols=lrgen.syn,
        symbol_table=[],
    )

    root = lr.parse()
    if root:
        root.write_to_file("output/lrparser-tree.txt")
    else:
        print("Parsiranje nije završilo uspješno.")
