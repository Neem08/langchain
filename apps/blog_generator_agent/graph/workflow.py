from langchain_google_genai import ChatGoogleGenerativeAI

from prompts.prompts import REVIEW_PROMPT


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2,
)


def reviewer_agent(state):

    print("\n🧐 Reviewer Agent")

    response = llm.invoke(
        REVIEW_PROMPT.format(
            topic=state["topic"],
            draft=state["draft"]
        )
    )

    return {
        "feedback": response.content
    }