from typing import TypedDict, List


class BlogState(TypedDict, total=False):
    topic: str

    research: List[dict]

    draft: str

    feedback: str

    approved: bool

    final_blog: str

    revision_count: int