from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch

from prompts.prompts import RESEARCH_PROMPT


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2,
)


search_tool = TavilySearch(
    max_results=5,
    topic="general",
)


def researcher_agent(state):

    topic = state["topic"]

    print("\n🔎 Research Agent")
    print(f"Researching: {topic}")

    search_results = search_tool.invoke(
        {
            "query": topic
        }
    )

    response = llm.invoke(
        RESEARCH_PROMPT.format(
            topic=topic,
            search_results=search_results
        )
    )

    research = response.content

    return {
        "research": [
            {
                "content": research,
                "search_results": search_results
            }
        ]
    }