import os
import re
import json
from typing import List, Dict, Any
import openai
from dotenv import load_dotenv
from src.utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Setup logger
logger = setup_logger()

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

class CommandParser:
    """
    Parse natural language commands into structured browser automation actions.
    """

    def __init__(self):
        self.action_patterns = {
            "navigate": r"(?:go to|navigate to|open|visit) (?:the )?(?:website |site |page )?(?:at )?(?:https?://)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?)",
            "click": r"click (?:on )?(?:the )?([^\n.]+)",
            "type": r"(?:type|enter|input|fill in|write) (?:the )?(?:text |value |string )?[\"']?([^\"']+)[\"']? (?:in(?:to)?|on) (?:the )?([^\n.]+)",
            "search": r"search (?:for )?[\"']?([^\"']+)[\"']? (?:on|in|at) (?:the )?([^\n.]+)",
            "google_search": r"(?:go to|navigate to|open|visit) (?:the )?(?:website |site |page )?(?:at )?(?:https?://)?(?:www\.)?google\.com(?: and| then)? search (?:for )?[\"']?([^\"']+)[\"']?",
            "login": r"log(?:in)?(?: to| into)? (?:the )?(?:website |site |page )?(?:at )?(?:https?://)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?)?(?: with)?(?: username| user| email)? [\"']?([^\"']+)[\"']?(?: and)?(?: password| pass)? [\"']?([^\"']+)[\"']?",
            "scroll": r"scroll (?:to )?(?:the )?([^\n.]+)",
            "wait": r"wait (?:for )?(?:the )?([^\n.]+)(?: to)?(?: appear| load| be visible| be clickable)?",
        }

    def parse(self, command: str) -> List[Dict[str, Any]]:
        """
        Parse a natural language command into a list of structured actions.

        Args:
            command: The natural language command to parse.

        Returns:
            A list of structured actions.
        """
        # Use rule-based parsing only
        actions = self._rule_based_parse(command)

        # If no actions were found, create a default navigate action
        if not actions and "go to" in command.lower():
            # Try to extract a URL from the command
            url_match = re.search(r'(?:go to|navigate to|open|visit) (?:the )?(?:website |site |page )?(?:at )?(?:https?://)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?)', command, re.IGNORECASE)
            if url_match:
                url = url_match.group(1)
                if not url.startswith("http"):
                    url = "https://" + url
                actions.append({
                    "type": "navigate",
                    "url": url
                })

        return actions

    def _rule_based_parse(self, command: str) -> List[Dict[str, Any]]:
        """
        Parse a command using rule-based patterns.
        """
        actions = []

        # Check each pattern
        for action_type, pattern in self.action_patterns.items():
            matches = re.search(pattern, command, re.IGNORECASE)
            if matches:
                if action_type == "navigate":
                    url = matches.group(1)
                    if not url.startswith("http"):
                        url = "https://" + url
                    actions.append({
                        "type": "navigate",
                        "url": url
                    })
                elif action_type == "click":
                    element = matches.group(1)
                    actions.append({
                        "type": "click",
                        "element": element
                    })
                elif action_type == "type":
                    text = matches.group(1)
                    element = matches.group(2)
                    actions.append({
                        "type": "type",
                        "element": element,
                        "text": text
                    })
                elif action_type == "search":
                    query = matches.group(1)
                    site = matches.group(2)
                    actions.append({
                        "type": "search",
                        "site": site,
                        "query": query
                    })
                elif action_type == "google_search":
                    query = matches.group(1)
                    actions.append({
                        "type": "navigate",
                        "url": "https://www.google.com"
                    })
                    actions.append({
                        "type": "search",
                        "site": "Google",
                        "query": query
                    })
                elif action_type == "login":
                    site = matches.group(1) if matches.group(1) else ""
                    username = matches.group(2)
                    password = matches.group(3)
                    if site and not site.startswith("http"):
                        site = "https://" + site
                    actions.append({
                        "type": "login",
                        "site": site,
                        "username": username,
                        "password": password
                    })
                elif action_type == "scroll":
                    element = matches.group(1)
                    actions.append({
                        "type": "scroll",
                        "element": element
                    })
                elif action_type == "wait":
                    element = matches.group(1)
                    actions.append({
                        "type": "wait",
                        "element": element
                    })

        return actions

    def _llm_based_parse(self, command: str) -> List[Dict[str, Any]]:
        """
        Parse a command using a language model.
        """
        try:
            prompt = f"""
            Parse the following natural language command into a structured JSON format for browser automation.
            The output should be a list of actions, where each action has a 'type' and additional parameters.

            Supported action types:
            - navigate: Go to a URL (parameters: url)
            - click: Click on an element (parameters: element)
            - type: Type text into an input field (parameters: element, text)
            - search: Search for something on a site (parameters: site, query)
            - login: Log into a site (parameters: site, username, password)
            - scroll: Scroll to an element (parameters: element)
            - wait: Wait for an element to appear (parameters: element)

            Command: {command}

            Output JSON:
            """

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a browser automation assistant that parses natural language commands into structured actions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )

            content = response.choices[0].message.content

            # Extract JSON from the response
            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = content

            # Clean up the JSON string
            json_str = json_str.strip()
            if json_str.startswith('```') and json_str.endswith('```'):
                json_str = json_str[3:-3].strip()

            actions = json.loads(json_str)

            # Ensure the result is a list
            if not isinstance(actions, list):
                actions = [actions]

            return actions
        except Exception as e:
            logger.error(f"Error in LLM parsing: {str(e)}")
            # Return a default action if LLM parsing fails
            return [{
                "type": "error",
                "message": f"Failed to parse command: {str(e)}"
            }]
