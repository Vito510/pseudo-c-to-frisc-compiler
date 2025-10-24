import unittest
from parserLeksickogAnalizatora import parse, _convert_2_pattern,_reg_definicije
from leksickiAnalizator import LexicalAnalyzer
import os
import signal
from SimEnka import match

def timeout(seconds=5):
    """Decorator to time out a test after `seconds` seconds."""
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(f"Test timed out after {seconds} seconds")

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                return func(*args, **kwargs)
            finally:
                signal.alarm(0)  # disable alarm
        return wrapper
    return decorator

class Test(unittest.TestCase):
    def test_list_int(self):
        """
        Parse test
        """
        result = parse("data/lexing-rules/c-leksik-pravila.txt")
        self.assertIsNotNone(result)
        
    def test_regex_creator(self):
        """
        Tests patern convertsion
        """
        
        test = ["{znamenka}",
                "(e|E)($|+|-){znamenka}{znamenka}*",
                "(_|{znak})(_|{znak}|{znamenka})*",
                "{znamenka}{znamenka}*",
                '"({sveOsimDvostrukogNavodnikaINovogReda}|\\")*"']
        
        correct = [
                "(0|1|2|3|4|5|6|7|8|9)",
                "(e|E)($|+|-)(0|1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*",
                "(_|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z)(_|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|0|1|2|3|4|5|6|7|8|9)*",
                "(0|1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*",
                '"(\(|\)|\{|\}|\||\*|\\\\|\$|\\t| |!|#|%|&|\'|+|,|-|.|/|0|1|2|3|4|5|6|7|8|9|:|;|<|=|>|?|@|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|[|]|^|_|`|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|~|\\")*"']
        

        for t, c in zip(test, correct):
            result = _convert_2_pattern(t,_reg_definicije)
            self.assertEqual(result,c)
            
    def test_regex_match(self):
        """
        Tests pattern matching
        """
        test = [("a","(a|b|c)"),
                ("512];","(0|1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*"),
                ("e+1005abc","(e|E)($|+|-)(1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*"),
                ("v+1002","(e|E)($|+|-)(1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*"),
                ("aabbabbc","(a|b)*bc")]
        
        correct = ["a","512","e+1005",None,"aabbabbc"]
        

        for t, c in zip(test, correct):
            result = match(t[1],t[0])
            self.assertEqual(result,c)

    @timeout(3)
    def run_lexer_test(self, folder_path):
        # path = os.path.join("tests", folder_path)
        path = folder_path
        data = parse(os.path.join(path, "test.lan"))
        lexer = LexicalAnalyzer(data)

        with open(os.path.join(path, "test.in"), "r", encoding="utf-8") as f:
            input_data = f.read()

        result = lexer.tokenize(input_data)

        with open(os.path.join(path, "test.out"), "r", encoding="utf-8") as f:
            expected_output = f.read().strip()

        self.assertEqual(result.strip(), expected_output.strip())

# Dynamically create a test for each subfolder in tests/lab1_teza
def generate_test(folder_name):
    def test(self):
        self.run_lexer_test(folder_name)
    return test

test_root = "tests/lab1_teza"
for folder in os.listdir(test_root):
    folder_path = os.path.join(test_root, folder)
    if os.path.isdir(folder_path):
        test_name = f"test_{folder}"
        setattr(Test, test_name, generate_test(folder_path))


if __name__ == "__main_":
    unittest.main()