# pyrefly: ignore [missing-import]
import streamlit as st
from db_connector import (
    get_engine_for_server,
    test_connection,
    get_databases_from_server,
    get_sql_database,
)
from agent_engine import create_database_agent, ask_database, is_safe_prompt

st.set_page_config(
    page_title="AI SQL Agent Playground",
    layout="wide",
)

st.title("🤖 AI SQL Agent Playground")
st.caption("Phase 8: Universal Database Assistant")

# Initialize session state variables if not present
if "server_connected" not in st.session_state:
    st.session_state.server_connected = False
if "database_loaded" not in st.session_state:
    st.session_state.database_loaded = False
if "db_type" not in st.session_state:
    st.session_state.db_type = "MySQL"
if "host" not in st.session_state:
    st.session_state.host = "localhost"
if "port" not in st.session_state:
    st.session_state.port = 3306
if "username" not in st.session_state:
    st.session_state.username = "root"
if "password" not in st.session_state:
    st.session_state.password = ""
if "databases" not in st.session_state:
    st.session_state.databases = []
if "selected_database" not in st.session_state:
    st.session_state.selected_database = None
if "db" not in st.session_state:
    st.session_state.db = None
if "agent_executor" not in st.session_state:
    st.session_state.agent_executor = None


# Disconnect utility
def disconnect_server():
    st.session_state.server_connected = False
    st.session_state.database_loaded = False
    st.session_state.databases = []
    st.session_state.selected_database = None
    st.session_state.db = None
    st.session_state.agent_executor = None
    st.rerun()


# --- FLOW 1: SERVER CONNECTION SCREEN ---
if not st.session_state.server_connected:
    st.subheader("Connect to Database Server")
    st.write(
        "Enter your database server credentials to discover available database schemas."
    )

    col1, col2 = st.columns(2)

    with col1:
        db_type = st.selectbox(
            "Database Type",
            ["MySQL", "PostgreSQL"],
            index=0 if st.session_state.db_type == "MySQL" else 1,
        )
        host = st.text_input("Host Server", value=st.session_state.host)
        # Auto-adjust default ports based on selection
        default_port = 3306 if db_type == "MySQL" else 5432
        port = st.number_input(
            "Port Number",
            value=default_port
            if host != st.session_state.host
            else st.session_state.port,
        )

    with col2:
        username = st.text_input(
            "Username",
            value="root"
            if db_type == "MySQL" and st.session_state.username == "postgres"
            else "postgres"
            if db_type == "PostgreSQL" and st.session_state.username == "root"
            else st.session_state.username,
        )
        password = st.text_input(
            "Password", value=st.session_state.password, type="password"
        )

    if st.button("Connect & Fetch Databases"):
        # Save connection details to session state
        st.session_state.db_type = db_type
        st.session_state.host = host
        st.session_state.port = port
        st.session_state.username = username
        st.session_state.password = password

        with st.spinner("Connecting to server..."):
            try:
                # Create root connection engine
                server_engine = get_engine_for_server(
                    db_type=db_type,
                    host=host,
                    port=port,
                    username=username,
                    password=password,
                )

                # Validate server response
                if test_connection(server_engine):
                    # Query server to discover active schemas
                    db_list = get_databases_from_server(server_engine, db_type)
                    st.session_state.databases = db_list
                    st.session_state.server_connected = True
                    st.success("Successfully connected to the server!")
                    st.rerun()
                else:
                    st.error(
                        "Failed to connect. Please verify server status and credentials."
                    )
            except Exception as e:
                st.error(f"Connection error: {e}")

# --- FLOW 2: DATABASE SELECTION SCREEN ---
elif st.session_state.server_connected and not st.session_state.database_loaded:
    st.subheader("Select Target Database")
    st.write(
        f"Connected to: **{st.session_state.host}:{st.session_state.port}** ({st.session_state.db_type})"
    )

    if not st.session_state.databases:
        st.warning("No databases found on this server or user lacks permissions.")
        if st.button("Go Back"):
            disconnect_server()
    else:
        selected_database = st.selectbox(
            "Available Database Schemas:", st.session_state.databases
        )

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Load SQL Agent"):
                with st.spinner(
                    "Analyzing schema & building LangChain Agent..."
                ):
                    try:
                        # 1. Create engine for specific database schema
                        db_engine = get_engine_for_server(
                            db_type=st.session_state.db_type,
                            host=st.session_state.host,
                            port=st.session_state.port,
                            username=st.session_state.username,
                            password=st.session_state.password,
                            database=selected_database,
                        )

                        # 2. Wrap engine in SQLDatabase
                        db = get_sql_database(db_engine)

                        # 3. Compile SQL Agent Executor
                        agent_executor = create_database_agent(db)

                        # 4. Save state parameters
                        st.session_state.selected_database = selected_database
                        st.session_state.db = db
                        st.session_state.agent_executor = agent_executor
                        st.session_state.database_loaded = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to load agent: {e}")
        with col2:
            if st.button("Change Server Credentials"):
                disconnect_server()

# --- FLOW 3: ACTIVE PLAYGROUND SCREEN (CHAT & SIDEBAR SCHEMA) ---
else:
    # 1. SIDEBAR SCHEMA EXPLORER
    with st.sidebar:
        st.header("⚙️ EasyQL Panel")
        st.write(f"**Database**: `{st.session_state.selected_database}`")
        st.write(f"**Type**: `{st.session_state.db_type}`")

        # Disconnect/Reset button
        if st.button("Change Database/Server", use_container_width=True):
            disconnect_server()

        st.divider()
        st.subheader("📚 Database Schema")

        # Fetch usable tables using LangChain database metadata wrapper
        try:
            tables = st.session_state.db.get_usable_table_names()
            if not tables:
                st.info("No tables found in this database.")
            else:
                st.write(f"Total tables: **{len(tables)}**")
                from sqlalchemy import inspect

                # Create engine inspector
                inspector = inspect(st.session_state.db._engine)
                for table in tables:
                    with st.expander(f"📋 {table}"):
                        columns = inspector.get_columns(table)
                        for col in columns:
                            col_name = col["name"]
                            col_type = str(col["type"]).lower()
                            st.write(f"🔹 **{col_name}** `({col_type})`")
        except Exception as e:
            st.error(f"Error loading tables: {e}")

    # 2. MAIN CHAT INTERFACE
    st.subheader(f"Chatting with: **{st.session_state.selected_database}**")

    question = st.text_input(
        "Ask a question about the active database:",
        placeholder="e.g., Get top 5 rows from the table...",
    )

    if st.button("Submit Query"):
        if not question.strip():
            st.warning("Please enter a question.")
        elif not is_safe_prompt(question):
            st.error(
                "⚠️ Security Exception: Your question contains keywords or actions "
                "associated with modifying data or structure. Commands like DROP, CREATE, "
                "DELETE, ALTER, INSERT, and UPDATE are strictly restricted. "
                "Please submit a read-only request."
            )
        else:
            with st.spinner("AI Agent is reasoning & running query..."):
                try:
                    # Invoke database query against the stored AgentExecutor
                    result = ask_database(
                        st.session_state.agent_executor, question
                    )

                    # Show generated SQL if present
                    if result.get("sql"):
                        st.subheader("Generated SQL Query:")
                        st.code(result["sql"], language="sql")
                    else:
                        st.info("No SQL query was executed for this request.")

                    # Show final text response
                    st.subheader("Final Answer:")
                    st.write(result["output"])

                except Exception as e:
                    st.error(f"Error during execution: {e}")
