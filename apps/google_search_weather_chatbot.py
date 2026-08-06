from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_community.utilities import GoogleSerperAPIWrapper
from langgraph.checkpoint.memory import InMemorySaver
import streamlit as st
load_dotenv()
llm = ChatGroq(model="openai/gpt-oss-20b", streaming = True)
search = GoogleSerperAPIWrapper()

if "memory" not in st.session_state:
    st.session_state.memory =  InMemorySaver()
    st.session_state.history = []
    

agent = create_agent(model =llm, tools = [search.run], system_prompt="you are a weatherman who gives weather info based on the location using tools", checkpointer=st.session_state.memory)

st.title("AI Weather App")
st.markdown("this chatbot is made using langchain and grok and can tell weather based on the location using google search")

for message in st.session_state.history:
    role = message['role']
    content = message['content']
    st.chat_message(role).markdown(content)
    
 
query = st.chat_input("Ask Anything")
if query:
    
    st.chat_message("user").markdown(query)
    # if query.lower() in ["bye","tata","goodbye"]:
    #    st.chat_message("ai").markdown("tata")
    st.session_state.history.append({"role":"user","content":query})
   
    res = agent.stream({"messages":[{"role":"user", "content":query}]},
                         {"configurable": {"thread_id": "1"}},
                         stream_mode="messages"
                       )
    ai_container = st.chat_message("ai")
    with ai_container:
        space = st.empty()
        message=""
        for chunk in res:
            message = message + chunk[0].content
            space.write(message)
       
        st.session_state.history.append({"role":"ai","content":message})
    
