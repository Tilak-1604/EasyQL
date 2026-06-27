# pyrefly: ignore [missing-import]
import streamlit as st
from db_connector import (
    get_engine_for_server,
    test_connection,
    get_databases_from_server,
    get_sql_database,
)
from agent_engine import create_database_agent, ask_database, is_safe_prompt

# Page configuration
st.set_page_config(
    page_title="EasyQL - Universal AI SQL Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Premium CSS Inject
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700&display=swap');
    
    /* Global Typography & Font Family */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Title Styling with Indigo/Teal Gradient */
    .title-brand {
        background: linear-gradient(95deg, #6366f1 0%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 2.8rem;
        margin-bottom: 0.2rem;
    }
    
    /* Subtitle Styling */
    .subtitle-brand {
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }
    
    /* Sidebar styling overrides */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important; /* Dark Slate */
        border-right: 1px solid #1e293b;
    }
    
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #f8fafc;
        font-family: 'Outfit', sans-serif;
    }

    /* Card Panels */
    .status-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1.5rem;
    }

    /* Buttons override to custom styled gradient */
    div.stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.8rem !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    div.stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
        background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%) !important;
    }

    /* Custom divider line */
    .nav-divider {
        height: 1px;
        background: linear-gradient(90deg, #334155, transparent);
        margin: 1.5rem 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Header Section
st.markdown('<div class="title-brand">EasyQL</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle-brand">The Universal Autonomous AI SQL Assistant</div>',
    unsafe_allow_html=True,
)

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
    st.subheader("🔑 Server Authentication")
    st.write(
        "Securely authenticate to your target MySQL or PostgreSQL database server."
    )

    # Wrap inputs in a clean card container
    with st.container(border=True):
        col1, col2 = st.columns(2)

        with col1:
            db_type = st.selectbox(
                "Database Engine Type",
                ["MySQL", "PostgreSQL"],
                index=0 if st.session_state.db_type == "MySQL" else 1,
            )
            host = st.text_input("Host Address / Endpoint", value=st.session_state.host)
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

        st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
        if st.button("Establish Server Connection", use_container_width=True):
            st.session_state.db_type = db_type
            st.session_state.host = host
            st.session_state.port = port
            st.session_state.username = username
            st.session_state.password = password

            with st.spinner("Initiating connection handshake..."):
                try:
                    server_engine = get_engine_for_server(
                        db_type=db_type,
                        host=host,
                        port=port,
                        username=username,
                        password=password,
                    )

                    if test_connection(server_engine):
                        db_list = get_databases_from_server(server_engine, db_type)
                        st.session_state.databases = db_list
                        st.session_state.server_connected = True
                        st.success("Handshake successful! Connected to server.")
                        st.rerun()
                    else:
                        st.error(
                            "Authentication failed. Check your network endpoint and server credentials."
                        )
                except Exception as e:
                    st.error(f"Network Connection Error: {e}")

# --- FLOW 2: DATABASE SELECTION SCREEN ---
elif st.session_state.server_connected and not st.session_state.database_loaded:
    st.subheader("📂 Schema Explorer & Selection")
    
    # Connection metadata card
    st.markdown(
        f"""
        <div class="status-card">
            🟢 <b>Connected Server</b>: {st.session_state.host}:{st.session_state.port} | 
            <b>Type</b>: {st.session_state.db_type} | 
            <b>User</b>: {st.session_state.username}
        </div>
        """, 
        unsafe_allow_html=True
    )

    if not st.session_state.databases:
        st.warning("Connection succeeded but no database schemas are accessible to this account.")
        if st.button("Return to Authentication"):
            disconnect_server()
    else:
        with st.container(border=True):
            selected_database = st.selectbox(
                "Select Target Database Schema:", st.session_state.databases
            )

            st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("Build AI Agent", use_container_width=True):
                    with st.spinner("Running schema reflection & compiling SQL Agent..."):
                        try:
                            db_engine = get_engine_for_server(
                                db_type=st.session_state.db_type,
                                host=st.session_state.host,
                                port=st.session_state.port,
                                username=st.session_state.username,
                                password=st.session_state.password,
                                database=selected_database,
                            )

                            db = get_sql_database(db_engine)
                            agent_executor = create_database_agent(db)

                            st.session_state.selected_database = selected_database
                            st.session_state.db = db
                            st.session_state.agent_executor = agent_executor
                            st.session_state.database_loaded = True
                            st.rerun()
                        except Exception as e:
                            st.error(f"Reflection compilation failed: {e}")
            with col2:
                if st.button("Switch Server Endpoint"):
                    disconnect_server()

# --- FLOW 3: ACTIVE PLAYGROUND SCREEN (CHAT & SIDEBAR SCHEMA) ---
else:
    # 1. SIDEBAR SCHEMA EXPLORER
    with st.sidebar:
        st.markdown('<div style="font-size: 1.6rem; font-weight: 700; font-family: \'Outfit\'; color: #ffffff;">EasyQL Config</div>', unsafe_allow_html=True)
        st.markdown(f"🟢 **Endpoint**: `{st.session_state.host}`")
        st.markdown(f"📂 **Active Schema**: `{st.session_state.selected_database}`")
        st.markdown(f"⚙️ **Dialect**: `{st.session_state.db_type}`")

        st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)

        if st.button("Disconnect Session", use_container_width=True):
            disconnect_server()

        st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)
        st.subheader("📚 Database Schema")

        try:
            tables = st.session_state.db.get_usable_table_names()
            if not tables:
                st.info("No tables discovered in this schema.")
            else:
                st.write(f"Total Tables: **{len(tables)}**")
                from sqlalchemy import inspect

                inspector = inspect(st.session_state.db._engine)
                for table in tables:
                    with st.expander(f"📋 {table}"):
                        columns = inspector.get_columns(table)
                        for col in columns:
                            col_name = col["name"]
                            col_type = str(col["type"]).lower()
                            st.write(f"🔹 **{col_name}** `({col_type})`")
        except Exception as e:
            st.error(f"Reflection error: {e}")

    # 2. MAIN CHAT INTERFACE
    st.subheader(f"💬 Active Agent Sandbox: {st.session_state.selected_database}")
    st.write("Submit natural language requests. The agent will formulate target queries, validate them, and explain the outputs.")

    question = st.text_input(
        "Enter question about your database:",
        placeholder="e.g., list top 5 student details...",
    )

    if st.button("Analyze & Run Query", use_container_width=True):
        if not question.strip():
            st.warning("Please provide a prompt.")
        elif not is_safe_prompt(question):
            st.error(
                "⚠️ Security Exception: Your prompt contains commands or keywords "
                "associated with modifying data or schema. Mutating commands (DROP, CREATE, "
                "DELETE, ALTER, INSERT, UPDATE, REMOVE) are restricted. "
                "Please submit a read-only request."
            )
        else:
            with st.spinner("Analyzing schema & executing reasoning loop..."):
                try:
                    result = ask_database(
                        st.session_state.agent_executor, question
                    )

                    if result.get("sql"):
                        st.subheader("📋 Executed SQL Query:")
                        st.code(result["sql"], language="sql")
                    else:
                        st.info("The agent completed the run without executing SQL.")

                    st.subheader("💡 Final Answer:")
                    st.write(result["output"])

                except Exception as e:
                    st.error(f"Execution failed: {e}")
