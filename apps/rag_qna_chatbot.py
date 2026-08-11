from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import  GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, PyPDFDirectoryLoader
from langchain_community.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
import streamlit as st

# data load - > data split ->data embed (using db) -> feed to agentic ai 
 
if "document_uploaded" not in st.session_state:
    st.session_state.document_uploaded = False
    
if "agent" not in st.session_state:
    st.session_state.agent = False
    
if "vector_store" not in st.session_state:
    st.session_state.vector_store = False
    
if "messages" not in st.session_state:
    st.session_state.messages = []

def process_document(path):
    # loader = PyPDFLoader("C:/Users/rpaul/Downloads/gen_ai_handbook.pdf")
    #loader = PyPDFLoader("C:/Users/rpaul/Downloads/Neemisha_Paul_Capgemini.pdf")
    loader = PyPDFDirectoryLoader(path)
    pdf = loader.load()




    #split the data
    splitters = RecursiveCharacterTextSplitter(chunk_size= 100, chunk_overlap = 20)
    splits = splitters.split_documents(pdf)



    #embedding
    embeddings = GoogleGenerativeAIEmbeddings(model = "gemini-embedding-001")

    vector_store = Chroma.from_documents(
        documents=splits,
        embedding=embeddings
    )

    print("\nChroma created successfully!")

    #agentic ai ( tool -> ,model -> system_prompt )
    @tool
    def get_tool(query:str):
        """
        you are A AGENTIC rag ai who asnwer question related to resume questions and use the pdf to answer all question"""
        print("tool called", query)
        data = vector_store.similarity_search(query = query, k=4)
        context = ""
        for doc in data:
            context+= doc.page_content + "\n"
            
        return context

    llm = ChatGroq(model="openai/gpt-oss-20b")
    system_prompt = """
    You are a helpful assistant that answers questions using retrieved context.
        ALWAYS use the `get_tool` tool for questions requiring external knowledge.
    """
    memory = InMemorySaver()
    agent = create_agent(
        model = llm,
        tools = [get_tool],
        system_prompt = system_prompt,
        checkpointer = memory
    )

    st.session_state.agent = agent
    st.session_state.document_uploaded = True


    if not st.session_state.document_uploaded:
        uploaded = st.file_uploader(label="Select PDF files", type =["pdf"], accept_multiple_files=True)
        if uploaded:
            with st.spinner("processing...."):
                path = "./doc_files"
                for file in uploaded:
                    with open(path+file.name,"wb") as m:
                        m.write(file.getvalue())
            
            process_document(path)
            st.rerun()
        

    if st.session_state.document_uploaded and st.session_state.agent:
        for message in st.session_state.messages:
            role = message.get("role")
            content = message.get("content")
            st.chat_message(role).markdown(content)


        query = st.chat_input("Ask anything related to uploaded documents....")
        if query:
            st.session_state.messages.append({"role":"user", "content":query})

            st.chat_message("user").markdown(query)
            response = st.session_state.agent.invoke(
                {"messages":[{"role":"user", "content":query}]},
                {"configurable":{"thread_id":1}}
            )

            answer = response["messages"][-1].content
            st.chat_message("ai").markdown(answer)
            st.session_state.messages.append({"role":"ai", "content":answer})