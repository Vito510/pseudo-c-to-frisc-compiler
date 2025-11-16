import unittest
import os
import threading
import functools
from LRParserGenerator import LRParserGenerator
from LRParser import LRParser, parse_uniform_sequence


# Windows sranje
def timeout(seconds=5):
    """Decorator to time out a function after `seconds` seconds (cross-platform)."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = [TimeoutError(f"Function timed out after {seconds} seconds")]
            
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    result[0] = e
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(seconds)
            
            if thread.is_alive():
                raise TimeoutError(f"Function timed out after {seconds} seconds")
            
            if isinstance(result[0], Exception):
                raise result[0]
            return result[0]
        
        return wrapper
    return decorator


class SyntaxTests(unittest.TestCase):
    
    @timeout(20)
    def run_parser_test(self, folder_path):
        san_file = os.path.join(folder_path, "test.san")
        in_file = os.path.join(folder_path, "test.in")
        out_file = os.path.join(folder_path, "test.out")
        tree_file = os.path.join(folder_path, "tree.txt")
        
        # Build parser tables
        lrgen = LRParserGenerator(san_file)
        lrgen.build_tables()
        
        # Parse input
        lr = LRParser(
            productions=lrgen.productions,
            action_table=lrgen.action_table,
            goto_table=lrgen.goto_table,
            uniform_sequence=parse_uniform_sequence(in_file),
            sync_symbols=lrgen.syn
        )
        
        result = lr.parse()
        
        # Write result to file
        if result:
            result.write_to_file(tree_file)
        else:
            # If parsing failed, create empty file or handle error
            with open(tree_file, "w", encoding="utf-8") as f:
                f.write("")
        
        # Compare output
        with open(out_file, "r", encoding="utf-8") as f:
            expected_lines = f.readlines()
        
        with open(tree_file, "r", encoding="utf-8") as f:
            actual_lines = f.readlines()
        
        # Use assertListEqual for better diff output
        self.assertListEqual(
            actual_lines,
            expected_lines,
            msg=f"Parse tree mismatch for {folder_path}"
        )


def generate_test(folder_path):
    def test(self):
        self.run_parser_test(folder_path)
    return test


test_root = "tests/lab2_teza"

if os.path.exists(test_root):
    for folder in sorted(os.listdir(test_root)):
        folder_path = os.path.join(test_root, folder)
        if os.path.isdir(folder_path):
            san_file = os.path.join(folder_path, "test.san")
            in_file = os.path.join(folder_path, "test.in")
            out_file = os.path.join(folder_path, "test.out")
            
            if all(os.path.exists(f) for f in [san_file, in_file, out_file]):
                test_name = f"test_{folder}"
                setattr(SyntaxTests, test_name, generate_test(folder_path))


if __name__ == "__main__":
    unittest.main()