from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st

llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash")


st.title("AI CHATBOT 🤖")
st.markdown("This is a chatbot made using Gemini AI and LangChain")

if "messages" not in st.session_state:
    st.session_state.messages = []
    
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    st.chat_message(role).markdown(content)
    
    
query = st.chat_input("ask anything")
if query:
      st.session_state.messages.append({"role":"user","content":query})
      st.chat_message("user:").markdown(query)
      if query.lower in ["bye","end","quit"]:
        st.chat_message("ai").markdown("tata")
      res = llm.invoke(query)
      st.chat_message("ai:").markdown(res.text)
      st.session_state.messages.append({"role":"ai","content":res.text})
   
#    if query.lower in ["bye","end","quit"]:
#        st.chat_message("ai").markdown("tata")
#        break
   
 