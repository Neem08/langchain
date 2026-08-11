from dotenv import load_dotenv

load_dotenv()


from graph.workflow import graph
from langgraph.types import Command


def main():

    print("=" * 70)
    print("        MULTI-AGENT BLOG GENERATOR")
    print("=" * 70)

    topic = input(
        "\nEnter your blog topic: "
    )

    config = {
        "configurable": {
            "thread_id": "blog-session-1"
        }
    }

    initial_state = {
        "topic": topic,
        "research": [],
        "draft": "",
        "feedback": "",
        "approved": False,
        "final_blog": "",
        "revision_count": 0
    }

    print("\n🚀 Starting workflow...\n")

    result = graph.invoke(
        initial_state,
        config=config
    )

    while "__interrupt__" in result:

        interrupt_data = result["__interrupt__"][0]

        payload = interrupt_data.value

        print("\n" + "=" * 70)
        print("GENERATED BLOG")
        print("=" * 70)

        print(payload["draft"])

        print("\n" + "=" * 70)
        print("HUMAN REVIEW")
        print("=" * 70)

        print("\nOptions:")
        print("1. Approve")
        print("2. Request revision")

        choice = input(
            "\nYour choice: "
        ).strip()

        if choice == "1":

            resume_value = {
                "approved": True,
                "feedback": ""
            }

        else:

            feedback = input(
                "\nWhat should the writer improve?\n> "
            )

            resume_value = {
                "approved": False,
                "feedback": feedback
            }

        result = graph.invoke(
            Command(
                resume=resume_value
            ),
            config=config
        )

    print("\n" + "=" * 70)
    print("FINAL BLOG")
    print("=" * 70)

    print(
        result["final_blog"]
    )

    print("\n" + "=" * 70)
    print(
        f"Revisions: {result.get('revision_count', 0)}"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()