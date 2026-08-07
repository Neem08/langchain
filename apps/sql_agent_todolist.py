from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.checkpoint.memory import InMemorySaver
import streamlit as st

load_dotenv()
llm = ChatGroq(model ="openai/gpt-oss-20b")
print(llm)
db= SQLDatabase.from_uri("sqlite:///my_tasks.db")
db.run("""
       CREATE TABLE IF NOT EXISTS tasks(
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           title TEXT NOT NULL,
           description TEXT,
           urgency TEXT CHECK (URGENCY IN ('HIGH','LOW','MODERATE')),
           category TEXT CHECK(category IN ('STUDY','HEALTH','OTHER')),
           status TEXT CHECK(status IN('pending','in_progress','completed')) DEFAULT 'pending',
           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
           
       );
       """)


 
toolkit = SQLDatabaseToolkit(db=db, llm =llm)
tools = toolkit.get_tools()

for tool in tools :
    print(tool.name)
    

print(llm.invoke("Hi who is the PM of australia?"))

system_prompt="""
You are a task management assistant that interacts with a SQL database containing a 'tasks' table. 

TASK RULES:
1. Limit SELECT queries to 10 results max with ORDER BY created_at DESC
2. After CREATE/UPDATE/DELETE, confirm with SELECT query
3. If the user requests a list of tasks, present the output in a structured table format to ensure a clean and organized display in the browser."

CRUD OPERATIONS:
    CREATE: INSERT INTO tasks(title, description, status)
    READ: SELECT * FROM tasks WHERE ... LIMIT 10
    UPDATE: UPDATE tasks SET status=? WHERE id=? OR title=?
    DELETE: DELETE FROM tasks WHERE id=? OR title=?

Table schema: id, title, description, status(pending/in_progress/completed), created_at.
"""

@st.cache_resource
def get_agent():
    agent = create_agent(
        model =llm,
        tools= tools,
        checkpointer = InMemorySaver(),
        system_prompt = system_prompt
    )
    return agent

agent = get_agent()

st.subheader("📜 TaskGPT - your task checker")

if "messages" not in st.session_state:
    st.session_state.messages = []
    
for message in st.session_state.messages:
    st.chat_message(message['role']).markdown(message['content'])
    


query = st.chat_input("what are your tasks for today")

if query:
    st.chat_message("user").markdown(query)
    st.session_state.messages.append({"role":"user","content":query})
    response = agent.invoke(
    {"messages":[{"role":"user","content":query}]},
    {"configurable":{"thread_id":"1"}}
                            )
    answer = response['messages'][-1].text
    st.markdown(answer)
    st.session_state.messages.append({"role":"ai","content":answer})
    





