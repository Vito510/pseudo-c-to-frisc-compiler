import unittest
from parserLeksickogAnalizatora import parse, _convert_2_pattern,_reg_definicije
# from regex import match
from SimEnka import match

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
        

if __name__ == "__main_":
    unittest.main()