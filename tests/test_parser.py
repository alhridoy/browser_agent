import unittest
from src.nlp.parser import CommandParser

class TestCommandParser(unittest.TestCase):
    """
    Test the CommandParser class.
    """
    
    def setUp(self):
        self.parser = CommandParser()
    
    def test_navigate_command(self):
        """
        Test parsing a navigate command.
        """
        command = "Go to google.com"
        actions = self.parser._rule_based_parse(command)
        
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["type"], "navigate")
        self.assertEqual(actions[0]["url"], "https://google.com")
    
    def test_click_command(self):
        """
        Test parsing a click command.
        """
        command = "Click on the search button"
        actions = self.parser._rule_based_parse(command)
        
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["type"], "click")
        self.assertEqual(actions[0]["element"], "search button")
    
    def test_type_command(self):
        """
        Test parsing a type command.
        """
        command = "Type 'hello world' in the search box"
        actions = self.parser._rule_based_parse(command)
        
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["type"], "type")
        self.assertEqual(actions[0]["element"], "search box")
        self.assertEqual(actions[0]["text"], "hello world")
    
    def test_search_command(self):
        """
        Test parsing a search command.
        """
        command = "Search for 'browser automation' on Google"
        actions = self.parser._rule_based_parse(command)
        
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["type"], "search")
        self.assertEqual(actions[0]["site"], "Google")
        self.assertEqual(actions[0]["query"], "browser automation")
    
    def test_login_command(self):
        """
        Test parsing a login command.
        """
        command = "Log into github.com with username 'user' and password 'pass'"
        actions = self.parser._rule_based_parse(command)
        
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["type"], "login")
        self.assertEqual(actions[0]["site"], "https://github.com")
        self.assertEqual(actions[0]["username"], "user")
        self.assertEqual(actions[0]["password"], "pass")

if __name__ == "__main__":
    unittest.main()
