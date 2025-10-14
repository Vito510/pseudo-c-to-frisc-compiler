import LRParserGenerator
import LexicalAnalyzer

class LRParser:
    def __init__(self, input_file, lexic_rules_file, grammar_file):
        lexical_analyzer = LexicalAnalyzer(lexic_rules_file)
        lexical_analyzer.tokenize(input_file)
        lr_parser_generator = LRParserGenerator(grammar_file)
        lr_parser_generator.build_tables()

        self.symbol_table = lexical_analyzer.symbol_table
        self.uniform_sequence = lexical_analyzer.uniform_sequence
        
        self.productions = lr_parser_generator.productions
        self.action_table = lr_parser_generator.action_table
        self.goto_table = lr_parser_generator.goto_table
