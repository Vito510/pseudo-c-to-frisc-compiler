from parserLeksickogAnalizatora import ParserData, parse
from SimEnka import match

class LexicalAnalyzer:
    def __init__(self, data: ParserData):
        self.states = data.stanja
        self.tokens = data.jedinke
        self.transitions: dict = data.prijelazi

        self.current_state = data.stanja[0]
        self.symbol_table = []
        self.uniform_sequence = []

        self.line_number = 1
            

    def get_symbol_index(self, token_type, token_text):
        for i, (_, t, text) in enumerate(self.symbol_table):
            if t == token_type and text == token_text:
                return i
        return None

    def tokenize(self, input) -> str:
        r = []
        input_length = len(input)

        l = 0

        while l < input_length:
            part = input[l:]
            # print(part)

            results = []

            # Accepts the longest match
            # print(input[l])

            for regex, action in self.transitions[self.current_state].items():
                re = match(regex, part)
                results.append(re if re else '')

            longest_match = max(results, key=lambda x: len(x))

            
            return_to = None
            actions = None
            if sum([len(r) for r in results]) > 0:
                idx = results.index(longest_match)
                _, actions = list(self.transitions[self.current_state].items())[idx]

                # Execute actions
                for action in actions:
                    parts = action.split()

                    if parts[0] == "UDJI_U_STANJE":
                        self.current_state = parts[1]
                    elif parts[0] == "VRATI_SE":
                        return_to = int(parts[1])
                    elif parts[0] == "NOVI_REDAK":
                        self.line_number += 1


            
            if return_to is not None:
                longest_match = longest_match[:return_to]
                l += len(longest_match)
            elif len(longest_match):
                l += len(longest_match)
            else:
                l += 1

            # if actions: print(f'{actions} {self.line_number} {longest_match.strip()}')

            if actions:
                akt = actions[0]
                if akt not in ["NOVI_REDAK"] and " " not in akt:
                    self.uniform_sequence.append((akt, int(self.line_number), longest_match))
                    r.append(f'{akt} {self.line_number} {longest_match}')



        return "\n".join(r)

if __name__ == "__main__":
    # data = parse("./data/lexing-rules/c-leksik-pravila.txt")
    # lexer = LexicalAnalyzer(data)

    # c_file = open("./data/code-input/c-test.c", "r", encoding="utf-8").read()

    # print(lexer.tokenize(c_file))

    data = parse("./tests/lab1_teza/09_poredak/test.lan")
    lexer = LexicalAnalyzer(data)
    c_file = open("./tests/lab1_teza/09_poredak/test.in", "r", encoding="utf-8").read()

    print(lexer.tokenize(c_file))
