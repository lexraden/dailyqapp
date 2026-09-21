import unittest
import sys
from io import StringIO
from src.dailyq import main

class TestDailyQApp(unittest.TestCase):
    def test_main_runs(self):
        # Just ensure main can be called without error
        try:
            main()
        except Exception as e:
            self.fail(f"main() raised {e}!")

    def test_main_with_name(self):
        # Test that main outputs the provided name
        captured_output = StringIO()
        sys.stdout = captured_output
        try:
            main("Alice")
        finally:
            sys.stdout = sys.__stdout__
        self.assertIn("Welcome to DailyQ, Alice!", captured_output.getvalue())

    def test_main_default_name(self):
        # Test default name when no argument provided
        captured_output = StringIO()
        sys.stdout = captured_output
        try:
            main()
        finally:
            sys.stdout = sys.__stdout__
        self.assertIn("Welcome to DailyQ, Traveler!", captured_output.getvalue())

if __name__ == '__main__':
    unittest.main()
