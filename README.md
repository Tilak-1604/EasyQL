# 🚀 EasyQL – AI SQL Agent Playground

> Query MySQL & PostgreSQL databases using natural language with an autonomous LangChain SQL Agent.

EasyQL is an AI-powered SQL Agent Playground that enables users to interact with relational databases through natural language. Built using **LangChain**, **Groq LLM**, **SQLAlchemy**, and **Streamlit**, it demonstrates modern Agentic AI concepts such as **ReAct reasoning**, **tool calling**, **schema discovery**, and **dynamic SQL generation**.

---

## ✨ Features

- 🤖 Natural Language → SQL using a LangChain SQL Agent
- 🧠 Autonomous **ReAct** reasoning with multi-step tool execution
- 🛠️ Dynamic schema discovery using **SQLDatabaseToolkit**
- 🗄️ Supports both **MySQL** and **PostgreSQL**
- 🔍 Generated SQL visualization for transparency
- 📊 Automatic schema inspection and metadata discovery
- 🛡️ Read-only SQL guardrails for safe database interactions
- 💬 Interactive Streamlit-based chat interface
- ⚡ Dynamic database connection and selection

---

## 🏗️ Architecture

```text
                  User
                    │
                    ▼
            Streamlit Interface
                    │
                    ▼
          LangChain SQL Agent
                    │
            (ReAct Reasoning)
                    │
                    ▼
          SQLDatabaseToolkit
                    │
      ┌─────────────┼─────────────┐
      ▼             ▼             ▼
 List Tables    Read Schema   Execute SQL
                    │
                    ▼
              SQLDatabase
                    │
                    ▼
             SQLAlchemy Engine
                    │
                    ▼
        MySQL / PostgreSQL Database
```

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|--------------|
| **Language** | Python |
| **LLM** | Groq (Llama 3.3) |
| **AI Framework** | LangChain |
| **Agent Pattern** | ReAct + AgentExecutor |
| **Database** | MySQL, PostgreSQL |
| **Database Toolkit** | SQLAlchemy, SQLDatabaseToolkit |
| **Frontend** | Streamlit |
| **Configuration** | python-dotenv |

---

## 📂 Project Structure

```text
EasyQL/
│
├── app.py                 # Streamlit UI
├── agent_engine.py        # LangChain SQL Agent
├── db_connector.py        # Database connection & SQLDatabase
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## ⚙️ Key LangChain Concepts Demonstrated

- ✅ Chat Models
- ✅ ChatPromptTemplate
- ✅ LCEL (LangChain Expression Language)
- ✅ SQLDatabase
- ✅ SQLDatabaseToolkit
- ✅ Tool Calling
- ✅ AgentExecutor
- ✅ ReAct Reasoning
- ✅ Autonomous SQL Generation
- ✅ Intermediate Execution Tracing

---

## 🚀 Getting Started

### Clone Repository

```bash
git clone https://github.com/your-username/EasyQL.git
cd EasyQL
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key
```

### Run the Application

```bash
streamlit run app.py
```

---

## 📸 Demo

<img width="500" height="200" alt="image" src="https://github.com/user-attachments/assets/a4679cae-4f50-4d81-9542-0a2ce677b7a0" />
<img width="500" height="200" alt="image" src="https://github.com/user-attachments/assets/00e22ade-9c06-4fc6-a192-c067a99cb9a4" />
<img width="500" height="200" alt="image" src="https://github.com/user-attachments/assets/06538c0a-3f68-4c54-b05f-f2a6b77a1fd6" />

---

## 🌟 Future Improvements

- 📈 Automatic chart generation from SQL results
- 📥 Export query results to CSV/Excel
- 🔐 Bring Your Own Groq API Key (BYOK)
- 🌍 Universal cloud database connectivity
- 📚 Query history and saved sessions
- ⚡ Streaming LLM responses

---

## 👨‍💻 Author

**Tilak Vaghasiya**

If you found this project helpful, consider giving it a ⭐ on GitHub!
