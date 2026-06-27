import os
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from langchain_groq import ChatGroq
# pyrefly: ignore [missing-import]
from langchain_core.prompts import ChatPromptTemplate
# pyrefly: ignore [missing-import]
from langchain_core.output_parsers import StrOutputParser
# pyrefly: ignore [missing-import]
from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent
# pyrefly: ignore [missing-import]
from langchain_classic.agents import AgentExecutor
# pyrefly: ignore [missing-import]
from langchain_community.utilities import SQLDatabase

# Load environment variables
load_dotenv()


def is_safe_prompt(prompt: str) -> bool:
    """Scans the user's natural language question for explicitly destructive

    intent or keywords (e.g. delete, drop, truncate, alter, insert, remove) to
    block them before executing the LLM.
    Uses difflib close matches to catch spelling mistakes and typos (like 'delet', 'drp').
    """
    import re
    import difflib

    cleaned_prompt = prompt.lower().strip()

    # 1. Split into individual alphanumeric word tokens
    words = set(re.findall(r"[a-z0-9_]+", cleaned_prompt))

    # Standalone keywords that are 100% associated with database writes/deletes
    forbidden_keywords = [
        "drop",
        "delete",
        "truncate",
        "alter",
        "insert",
        "remove",
    ]

    # For each word token, run fuzzy string matching against the blacklist
    for word in words:
        # Ignore words shorter than 3 characters to avoid false positive triggers (like 'do', 'in')
        if len(word) >= 3:
            close_matches = difflib.get_close_matches(
                word, forbidden_keywords, cutoff=0.7
            )
            if close_matches:
                return False

    # 2. Check for multi-word phrases that indicate database creation/modification
    forbidden_phrases = [
        "create table",
        "create database",
        "create schema",
        "drop schema",
        "remove table",
        "clear database",
        "wipe database",
        "destroy table",
    ]

    for phrase in forbidden_phrases:
        if phrase in cleaned_prompt:
            return False

    return True


def ask_llm(question: str) -> str:
    """Takes a user question, formats it through a prompt template,

    runs it through the ChatGroq model, and parses the response to a string.
    Using LangChain Expression Language (LCEL).
    """
    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",
        temperature=0.0,
    )

    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful and polite database assistant. Answer the user's question directly.",
            ),
            ("human", "{question}"),
        ]
    )

    output_parser = StrOutputParser()
    chain = prompt_template | llm | output_parser
    response_text = chain.invoke({"question": question})
    return response_text


def create_database_agent(db: SQLDatabase) -> AgentExecutor:
    """Creates a LangChain SQL Agent Executor bound to a specific SQLDatabase instance."""
    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",
        temperature=0.0,
    )

    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        agent_type="tool-calling",
        verbose=True,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )
    return agent_executor


def ask_database(agent_executor: AgentExecutor, question: str) -> dict:
    """Invokes the provided agent executor on the user question and returns

    a dict containing the final output and generated SQL query.
    """
    print(f"\n--- [Agent Invocation Started] Query: '{question}' ---")
    response = agent_executor.invoke({"input": question})
    print(f"\n--- [Agent Invocation Completed] ---")

    # Extract intermediate steps to capture executed SQL query
    intermediate_steps = response.get("intermediate_steps", [])
    executed_sql = None

    for action, observation in intermediate_steps:
        # Check if the tool executed was the SQL query tool
        if action.tool == "sql_db_query":
            # Extract query (could be string or dictionary key)
            if isinstance(action.tool_input, dict):
                executed_sql = action.tool_input.get("query")
            else:
                executed_sql = action.tool_input

    # Return output and SQL query
    return {
        "output": response.get("output", "No response generated."),
        "sql": executed_sql,
    }


def inspect_database_tools(db: SQLDatabase) -> None:
    """Initializes the SQLDatabaseToolkit for the provided DB, lists all available database tools."""
    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",
        temperature=0.0,
    )

    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()
    print(f"Total tools loaded from toolkit: {len(tools)}\n")

    for idx, tool in enumerate(tools, 1):
        print(f"Tool {idx}:")
        print(f"  Name:        {tool.name}")
        print(f"  Description: {tool.description}")
        print(f"  Args Schema: {tool.args}")
        print("-" * 50)
