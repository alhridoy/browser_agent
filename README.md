# Browser Automation Agent

An AI agent that automates browser workflows on your machine's native browser using natural language commands, inspired by OpenAI's Operator but works directly with your local browser.The Browser Automation Agent is an AI-powered system that enables users to control web browsers through natural language instructions. Inspired by OpenAI's Operator, this project works directly with local browsers to execute complex web tasks automatically.

The system is organized into three progressive levels of capability:

Basic browser control through Playwright
Advanced OS-level browser integration


## Features

### Level 1 - Basic Browser Control
- **Interact API**: Accepts natural language commands and translates them into browser automation actions
- **Error Handling**: Properly handles common error scenarios with clear error messages
- **Website Agnostic**: Works with any website, not specific to a particular one
- **Demo Capabilities**: Log into websites, perform searches, navigate through results

### Level 2 - Advanced Browser Integration
- **OS-level Browser Control**: Direct control of native browsers using PyAutoGUI and Pynput
- **Extract API**: Retrieve and parse structured data from web pages
- **Proxy & Extension Support**: Configure proxies and browser extensions
- **Complete Automation Flow**: End-to-end workflows combining multiple actions

### Level 3 - Contextual Intelligence & Advanced Workflows
- **Cross-platform Compatibility**: Identical functionality across Windows, macOS, and Linux
- **Automated Scheduling**: Run tasks at periodic intervals automatically
- **Conversational Interface**: Maintain context across multiple commands
- **Advanced Error Recovery**: Graceful handling of unexpected situations

## System Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  User Interface │────▶│  NLP Processing │────▶│ Browser Control │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Contextual Memory│◀───▶│  Task Scheduler │     │   Data Extract  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Installation

1. Clone the repository
   ```
   git clone https://github.com/alhridoy/browser_agent.git
   cd browser_agent
   ```

2. Create a virtual environment
   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```
   pip3 install -r requirements.txt
   ```

4. Install Playwright browsers (for Level 1)
   ```
   python3 -m playwright install
   ```

## Usage

### Level 1 - Basic Browser Control

Run the Level 1 demo:
```
python3 final_demo.py
```

Start the Level 1 API server:
```
uvicorn src.api.main:app --reload
```

Use the CLI:
```
python3 -m src.cli "Go to Google and search for browser automation"
```

### Level 2 - Advanced Browser Integration

Run the Level 2 demo:
```
python3 level2_pyautogui_demo.py
```

Extract data from web pages:
```
python3 level2_extract_demo.py
```

Start the Level 2 API server:
```
uvicorn src.api.level2_api:app --reload
```

### Level 3 - Contextual Intelligence

Run the Level 3 demo:
```
python3 level3_demo.py
```

Start the Level 3 API server:
```
uvicorn src.api.level3_api:app --reload
```

## Supported Actions

- **Navigate**: Go to a URL
  - Example: "Go to github.com"
- **Click**: Click on an element
  - Example: "Click on the login button"
- **Type**: Type text into an input field
  - Example: "Type 'hello world' in the search box"
- **Search**: Search for something on a site
  - Example: "Search for 'browser automation' on Google"
- **Login**: Log into a site
  - Example: "Log into github.com with username 'user' and password 'pass'"
- **Scroll**: Scroll to an element
  - Example: "Scroll to the footer"
- **Wait**: Wait for an element to appear
  - Example: "Wait for the search results"
- **Press**: Press a key on an element
  - Example: "Press Enter on the search box"
- **Extract**: Extract data from a web page
  - Example: "Extract the search results"
- **Schedule**: Schedule a task to run periodically
  - Example: "Schedule a task to check email every hour"
- **Remember/Recall**: Store and retrieve information
  - Example: "Remember this search query" / "What was the search query?"

## Project Structure

- `src/api`: API endpoints for all levels
- `src/browser`: Browser automation logic (Level 1)
- `src/native`: OS-level browser control (Level 2-3)
- `src/nlp`: Natural language processing
- `src/utils`: Utility functions
- `src/conversation`: Conversational interface (Level 3)
- `src/scheduler`: Task scheduling (Level 3)
- `src/level3`: Level 3 agent integration
- `tests`: Test cases

## API Endpoints

### Level 1 API
- `/interact`: Process natural language commands
- `/health`: Health check endpoint

### Level 2 API
- `/interact`: Process natural language commands
- `/extract`: Extract data from web pages
- `/config/*`: Configuration endpoints for proxy, extensions, etc.

### Level 3 API
- `/message`: Process messages with context
- `/task`: Schedule tasks
- `/tasks`: Manage scheduled tasks
- `/conversation/{user_id}`: Manage conversation history
- `/memory/{user_id}`: Manage user memory
- `/ws/{user_id}`: WebSocket for real-time communication

## Advantages Over Existing Frameworks

- **Multi-level architecture** with progressive capabilities
- **OS-level native browser control** without dependencies
- **Contextual intelligence** for complex multi-step instructions
- **Scheduled automation** for periodic tasks
- **Cross-platform consistency** across operating systems
- **Comprehensive error handling** with recovery mechanisms
- **Modular and extensible design** for easy customization

## Requirements

- Python 3.8+
- Chrome, Firefox, or Edge browser installed
- For OCR functionality: Tesseract OCR
- For Level 2-3: PyAutoGUI, Pynput
- For Level 3: Schedule

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
