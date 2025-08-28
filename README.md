# 🤖 AI Code Interpreter

An intelligent FastAPI web application that executes Python code and analyzes CSV data through natural language conversations. Built with modern async architecture and features a smart router agent that automatically selects between Python execution and data analysis tools.

## Features

* **Intelligent Agent Routing** - Router agent automatically chooses between Python REPL and CSV analysis tools
* **Python Code Execution** - Write and run Python code through PythonREPLTool for math, algorithms, and programming
* **CSV Data Analysis** - Upload CSV files and query them using pandas through create_csv_agent
* **Conversation Memory** - Dual memory system maintains context in both AI agent and web interface
* **Modern FastAPI Backend** - Web API with Pydantic validation and automatic API documentation
* **File Management** - Secure CSV upload, removal, and automatic cleanup on exit

## Try it Live

**https://huggingface.co/spaces/uygaraydin/code-interpreter**

*"Write a function to calculate prime numbers up to 100"* → Python code execution  
*"What's the correlation between columns in my CSV?"* → Data analysis results

## Installation

```bash
git clone https://github.com/uygaraydin/code-interpreter.git
cd code-interpreter
pipenv install
pipenv shell
```

## Environment Setup

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_openai_api_key
LANGCHAIN_API_KEY=your_langchain_api_key
```

**Get your API keys:**
* **OpenAI API**: https://platform.openai.com/
* **LangChain API**: https://smith.langchain.com/ (for agent monitoring and tracing)

## Usage

**Run the application:**

```bash
python app.py
```

Then open your browser and go to `http://localhost:8000`

**How to use:**
1. **For Python tasks:** Ask programming questions, request calculations, or algorithm help
2. **For data analysis:** Upload a CSV file first, then ask questions about your data  
3. **Smart routing:** The router agent automatically picks the right tool for your question

## How It Works

Router agent analyzes queries and selects appropriate tools. Uses LangChain for AI orchestration and FastAPI for modern async web architecture.

## Project Structure

```
code-interpreter/
├── app.py                          # FastAPI main application
├── config/
│   └── settings.py                 # Configuration settings
├── models/
│   └── schemas.py                  # Data validation models
├── services/
│   ├── agent_service.py           # AI agents & LangChain logic
│   └── file_service.py            # File upload handling
├── templates/
│   └── index.html                 # Web interface
├── Dockerfile                     # Docker containerization
├── Pipfile                        # Pipenv dependencies
└── README.md                      # This file
```

## Dependencies

```
fastapi
uvicorn
langchain
langchain-openai
langchain-experimental
pandas
tabulate
itsdangerous
pydantic
python-dotenv
jinja2
python-multipart
```

## Contributing

Feel free to submit issues and pull requests to improve the application!