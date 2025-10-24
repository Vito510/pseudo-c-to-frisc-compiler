import parserLeksickogAnalizatora
from SimEnka import match

class LexicalAnalyzer:
    def __init__(self, data):
        self.states = data.stanja
        self.tokens = data.jedinke
        self.transitions: dict = data.prijelazi

        self.current_state = 'S_pocetno'
        self.symbol_table = []
        self.uniform_sequence = []

        self.line_number = 1
            

        # print("States:", self.transitions["S_string"])


    def get_symbol_index(self, token_type, token_text):
        for i, (_, t, text) in enumerate(self.symbol_table):
            if t == token_type and text == token_text:
                return i
        return None

    def tokenize(self, input):
        # input = "/* test"
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
                
                # if re: match(regex, part, 0)




            longest = max(results, key=lambda x: len(x))
            mx = len(longest)

            
            return_to = None
            if sum([len(r) for r in results]) > 0:
                idx = results.index(longest)
                _, actions = list(self.transitions[self.current_state].items())[idx]
                # if actions: print(f'{longest.strip():10}\t{actions}')

                if actions:
                    akt = actions[0]
                    if akt not in ["NOVI_REDAK"] and " " not in akt:
                        print(akt)

                



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
                l -= return_to
            elif mx:
                l += mx
            else:
                l += 1



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

if __name__ == "__main__":
    data = parserLeksickogAnalizatora.parse("./data/c-leksik-pravila.txt")
    lexer = LexicalAnalyzer(data)

    c_file = open("./data/c-program.c", "r", encoding="utf-8").read()
    # c_file = """ \"tes\"t2\" """

    lexer.tokenize(c_file)
    # lexer.print_tables()

    # r = re.match("""(\n|\(|\)|\{|\}|\||\*|\\|\\$|\t| |!|#|%|&|'|\+|,|\-|\.|/|0|1|2|3|4|5|6|7|8|9|:|;|<|=|>|\?|@|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|\[|\]|\^|_|`|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|~|\")*""", c_file)
    # print(r)