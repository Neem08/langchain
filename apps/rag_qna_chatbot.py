from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import  GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.tools import tool
from langchain.agents import create_agent
# from langchain_community.memory import InMemorySaver

# data load - > data split ->data embed (using db) -> feed to agentic ai 

# loader = PyPDFLoader("C:/Users/rpaul/Downloads/gen_ai_handbook.pdf")
loader = PyPDFLoader("C:/Users/rpaul/Downloads/Neemisha_Paul_Capgemini.pdf")
pdf = loader.load()

print("Pages:", len(pdf))

#split the data
splitters = RecursiveCharacterTextSplitter(chunk_size= 100, chunk_overlap = 20)
splits = splitters.split_documents(pdf)

print("\nFirst chunk:")
print(splits[0].page_content[:50])

#embedding
embeddings = GoogleGenerativeAIEmbeddings(model = "gemini-embedding-001")
test_embedding = embeddings.embed_query("Hello world")

print("Embedding length:", len(test_embedding))
print("First 5 values:", test_embedding[:5])
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

llm = ChatGoogleGenerativeAI(model = "gemini-3.6-flash")
system_prompt = """
 You are a helpful assistant that answers questions using retrieved context.
	ALWAYS use the `get_tool` tool for questions requiring external knowledge.
"""
agent = create_agent(
    model = llm,
    tools = [get_tool],
    system_prompt = system_prompt
)

query = "what is the job genie project made of and what all are the experience skill sets"
ans = agent.invoke(
    {"messages":[{"role":"user", "content": query}]}
)
print(ans["messages"][-1].content)
