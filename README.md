# AI SQL Agent Playground

## Overview
An interactive playground built with Streamlit and LangChain to query databases using natural language. This project serves as an educational path to master LangChain design patterns, including custom tool execution, runnable chains, and reasoning loops.

## Features (Planned)
- Natural language to SQL query translation.
- SQL query execution and raw data rendering.
- Detailed step-by-step agent reasoning visualization.
- Configurable LLM API options.

## Tech Stack
- **Language**: Python
- **UI Framework**: Streamlit
- **AI Agent Orchestration**: LangChain & LangChain Community
- **LLM Engine**: Groq (Llama-3)
- **Database Engine**: SQLAlchemy (MySQL driver)
- **Settings Manager**: python-dotenv

## Folder Structure
```text
AI-SQL-Agent-Playground/
├── app.py                # Streamlit Dashboard (UI & orchestration)
├── agent_engine.py       # LangChain Agent & LLM configurations
├── db_connector.py       # Database utility wrapper & connection test
├── requirements.txt      # Python dependencies list
├── .env.example          # Environment variables template
├── .gitignore            # Files to ignore in Git
└── README.md             # Project documentation
```
