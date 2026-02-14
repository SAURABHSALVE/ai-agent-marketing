from typing import TypedDict, Optional

class AgentState(TypedDict):
    """
    Represents the state of our agent.
    
    Attributes:
        original_request (str): The user's original input/prompt.
        generated_content (str): The current draft of the Instagram post.
        is_safe (bool): Result of the safety check. True if safe, False otherwise.
        evaluation_score (int): Quality score (0-10).
        evaluation_feedback (str): Feedback on how to improve the post.
        revision_count (int): Number of revisions made so far. Used to stop infinite loops.
    """
    original_request: str
    generated_content: str
    is_safe: Optional[bool]
    evaluation_score: Optional[int]
    evaluation_feedback: Optional[str]
    revision_count: int
