import os
from typing import Any, List
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
# pyrefly: ignore [missing-import]
from langchain_community.utilities import SQLDatabase

# Load environment variables
load_dotenv()


def is_safe_query(sql: str) -> bool:
    """Strips comments and inspects the first command token of the SQL query

    to ensure it belongs to a read-only action (SELECT, SHOW, DESCRIBE, EXPLAIN, WITH).
    """
    # Remove single-line comments
    lines = sql.split("\n")
    cleaned_lines = []
    for line in lines:
        if "--" in line:
            line = line.split("--")[0]
        cleaned_lines.append(line)
    cleaned_sql = "\n".join(cleaned_lines)

    # Remove block comments /* ... */
    while "/*" in cleaned_sql and "*/" in cleaned_sql:
        start = cleaned_sql.find("/*")
        end = cleaned_sql.find("*/") + 2
        cleaned_sql = cleaned_sql[:start] + cleaned_sql[end:]

    cleaned_sql = cleaned_sql.strip().lower()
    if not cleaned_sql:
        return False

    # Grab the first word token
    tokens = cleaned_sql.split()
    if not tokens:
        return False

    first_token = "".join(c for c in tokens[0] if c.isalnum())
    safe_commands = ["select", "show", "describe", "explain", "with","DESC"]
    return first_token in safe_commands


class SafeSQLDatabase(SQLDatabase):
    """Subclass of SQLDatabase that intercepts executes and blocks mutating commands."""

    def run(
        self,
        command: str,
        fetch: str = "all",
        include_columns: bool = False,
        **kwargs: Any,
    ) -> str:
        # Validate query safety before running
        if not is_safe_query(command):
            # Return error as string observation so the LLM agent learns the query is blocked,
            # rather than crashing python execution flow.
            return (
                f"Error: SQL execution blocked. Mutating queries are restricted. "
                f"Only read-only commands (SELECT, SHOW, DESCRIBE, EXPLAIN, WITH) are permitted. "
                f"Your query attempted: {command.strip()}"
            )

        return super().run(
            command, fetch=fetch, include_columns=include_columns, **kwargs
        )


def get_engine_for_server(
    db_type: str,
    host: str,
    port: int,
    username: str,
    password: str,
    database: str = None,
) -> Engine:
    """Creates a SQLAlchemy engine dynamically for MySQL or PostgreSQL.

    If database is None:
      - MySQL connects to "/" (server root).
      - PostgreSQL connects to "/postgres" (default postgres system DB).
    """
    db_type = db_type.lower().strip()

    if db_type == "mysql":
        db_path = f"/{database}" if database else "/"
        connection_url = (
            f"mysql+pymysql://{username}:{password}@{host}:{port}{db_path}"
        )
    elif db_type == "postgresql":
        # PostgreSQL does not allow connecting without a database target,
        # so we fall back to the default 'postgres' database.
        db_path = f"/{database}" if database else "/postgres"
        connection_url = f"postgresql+psycopg2://{username}:{password}@{host}:{port}{db_path}"
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

    # Create engine with pool_pre_ping to check socket status dynamically
    engine = create_engine(connection_url, pool_pre_ping=True)
    return engine


def test_connection(engine: Engine) -> bool:
    """Validates the connection by running a simple SELECT 1 command."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            return True
    except Exception as e:
        print(f"SQLAlchemy Test Connection Failed: {e}")
        return False


def get_databases_from_server(engine: Engine, db_type: str) -> List[str]:
    """Queries the database server system tables to list all user schemas."""
    db_type = db_type.lower().strip()
    databases = []

    try:
        with engine.connect() as conn:
            if db_type == "mysql":
                result = conn.execute(text("SHOW DATABASES;"))
                # Extract first column of every row
                databases = [row[0] for row in result.fetchall()]
            elif db_type == "postgresql":
                # Query pg_database catalog, filtering out templates and default system databases
                query = text(
                    "SELECT datname FROM pg_database WHERE datistemplate = false;"
                )
                result = conn.execute(query)
                databases = [row[0] for row in result.fetchall()]
    except Exception as e:
        print(f"Database list retrieval failed: {e}")
        raise RuntimeError(f"Could not discover databases: {e}")

    return databases


def get_sql_database(engine: Engine) -> SQLDatabase:
    """Wraps a SQLAlchemy engine in our SafeSQLDatabase wrapper."""
    return SafeSQLDatabase(engine)
