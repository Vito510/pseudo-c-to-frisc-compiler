import re
import parserLeksickogAnalizatora

class LexicalAnalyzer:
    def __init__(self, data):
        self.states = data.stanja
        self.tokens = data.jedinke
        self.transitions = data.prijelazi

        self.current_state = 'S_pocetno'
        self.symbol_table = []
        self.uniform_sequence = []

        self.line_number = 1


    def get_symbol_index(self, token_type, token_text):
        for i, (_, t, text) in enumerate(self.symbol_table):
            if t == token_type and text == token_text:
                return i
        return None

    def tokenize(self, input):
        current_position = 0
        input_length = len(input)

        while current_position < input_length:
            part = input[current_position:]

            # Ignore whitespace and newlines
            m = re.match(r'[ \t\r]+', part)
            if m:
                current_position += len(m.group(0))
                continue
            
            m = re.match(r'\n', part)
            if m:
                self.line_number += 1
                current_position += len(m.group(0))
                continue

            longest_match = None
            longest_actions = None

            # Accepts the longest match
            for regex, action in self.transitions[self.current_state].items():
                if re.match(regex, part):
                    text = re.match(regex, part).group(0)
                    if longest_match is None or len(text) > len(longest_match):
                        longest_match = text
                        longest_actions = action

            if not longest_match:
                print("ERROR at line", self.line_number)
                print("\n")
                break

            offset = len(longest_match)
            return_to = 0

            # Execute actions
            for action in longest_actions:
                parts = action.split()

                if parts[0] == "UDJI_U_STANJE":
                    self.current_state = parts[1]
                elif parts[0] == "VRATI_SE":
                    return_to = int(parts[1])
                elif parts[0] == "NOVI_REDAK":
                    self.line_number += 1

                # Handle token
                else:
                    token_type = parts[0]
                    idx = self.get_symbol_index(token_type, longest_match)
                    if idx is None:
                        idx = len(self.symbol_table)
                        self.symbol_table.append((idx, token_type, longest_match))
                    self.uniform_sequence.append((token_type, self.line_number, idx))

            current_position = current_position + offset - return_to

    def print_tables(self):
        print("==================================")
        print("SYMBOL TABLE:")
        print("==================================")
        print("Index\t  Token\t\t      Text")
        print("==================================")
        for idx, token, text in self.symbol_table:
            print(f"{idx:<5}\t{token:^10}\t{text:>10}")
        print("==================================")

        print("\n\n==========================================")
        print("UNIFORM SEQUENCE:")
        print("==========================================")
        print("Token\t\t       Line\t     Index")
        print("==========================================")
        for token, line, idx in self.uniform_sequence:
            print(f"{token:<10}\t{line:10}\t{idx:>10}", sep="\t\t")
        print("==========================================")
        print("velika kontribucija od strane najgas programera ikad <3")



data = parserLeksickogAnalizatora.parse("./data/c-leksik-pravila.txt")
lexer = LexicalAnalyzer(data)

c_file = open("./data/c-program.c", "r", encoding="utf-8").read()
c_file = "void fun(int xYz)\nint x=5;\nx=20;"
lexer.tokenize(c_file)
lexer.print_tables()