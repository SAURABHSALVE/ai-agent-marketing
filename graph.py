import logging
import os
import re
from typing import Literal
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from memory_manager import load_memory, update_hashtags

from state import AgentState
from prompts import (
    GENERATE_POST_PROMPT,
    EVALUATE_POST_PROMPT,
    SAFETY_CHECK_PROMPT,
    REVISE_POST_PROMPT
)

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables (API keys)
load_dotenv()

# Initialize the LLM with Max Retries for robustness
# Using gpt-3.5-turbo with max_retries=3 to handle transient API errors
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    max_retries=3
)

# --- Nodes ---

def generate_post_node(state: AgentState):
    """Generates the initial Instagram post."""
    logging.info("Generating Post...")
    request = state['original_request']
    
    # Load Memory
    memory_data = load_memory()
    tone = memory_data.get("brand_tone", "neutral")
    hashtags = ", ".join(memory_data.get("hashtags", []))
    
    # Construct Context-Aware Prompt
    context_str = f"Brand Tone: {tone}\nUsed Hashtags: {hashtags}"
    # Append context to original prompt (simple string concatenation)
    full_prompt = f"{GENERATE_POST_PROMPT.format(request=request)}\n\nContext:\n{context_str}"
    
    response = llm.invoke(full_prompt)
    
    return {
        "generated_content": response.content,
        "revision_count": 0
    }

def safety_check_node(state: AgentState):
    """Checks if the content is safe (including medical/financial guardrails)."""
    logging.info("Checking Safety...")
    content = state['generated_content']
    
    response = llm.invoke(SAFETY_CHECK_PROMPT.format(content=content))
    content_upper = response.content.upper()
    is_safe = "SAFE" in content_upper and "UNSAFE" not in content_upper
    
    # If unsafe, blocked immediately
    if not is_safe:
        logging.warning("Safety Check FAILED: Content flagged as UNSAFE.")
        return {
            "generated_content": "This content was flagged as unsafe (e.g., medical claims, financial advice, or prohibited topics) and cannot be generated.",
            "is_safe": False,
            "evaluation_score": 0
        }
        
    logging.info("Safety Check PASSED.")
    return {"is_safe": True}

def evaluate_post_node(state: AgentState):
    """Evaluates the post quality and checks hard constraints."""
    logging.info("Evaluating Post...")
    content = state['generated_content']
    
    response = llm.invoke(EVALUATE_POST_PROMPT.format(content=content))
    output = response.content
    
    try:
        score_line = [line for line in output.split('\n') if "Score:" in line][0]
        score = int(score_line.split("Score:")[1].strip())
    except Exception:
        logging.error("Failed to parse evaluation score, defaulting to 5.")
        score = 5 
        
    feedback = output.replace(f"Score: {score}", "").replace("Feedback:", "").strip()
    
    # Hard constraint: Check word count roughly (approx 150 words)
    word_count = len(content.split())
    if word_count > 150:
        score = min(score, 6) # Force revision
        feedback += f" [System Note: Word count is too high ({word_count} words). Reduce to < 150.]"
        logging.info(f"Constraint Violation: Word count {word_count} > 150.")

    # Hard constraint: Check hashtag count
    hashtag_count = content.count('#')
    if hashtag_count > 10:
        score = min(score, 6)
        feedback += f" [System Note: Too many hashtags ({hashtag_count}). Reduce to <= 10.]"
        logging.info(f"Constraint Violation: Hashtag count {hashtag_count} > 10.")

    return {
        "evaluation_score": score,
        "evaluation_feedback": feedback
    }

def revise_post_node(state: AgentState):
    """Revises the post based on feedback."""
    logging.info(f"Revising Post (Revision #{state['revision_count'] + 1})...")
    content = state['generated_content']
    feedback = state['evaluation_feedback']
    
    response = llm.invoke(REVISE_POST_PROMPT.format(content=content, feedback=feedback))
    
    return {
        "generated_content": response.content,
        "revision_count": state["revision_count"] + 1
    }

def final_output_node(state: AgentState):
    """Final Output node: Extracts hashtags and updates memory."""
    logging.info("Workflow Completed. Updating memory...")
    
    content = state['generated_content']
    
    # Extract hashtags using regex
    found_hashtags = re.findall(r"#\w+", content)
    
    # Update memory
    if found_hashtags:
        update_hashtags(found_hashtags)
        logging.info(f"Learned {len(found_hashtags)} hashtags.")
        
    return {}

# --- Conditional Logic (Edges) ---

def decide_after_safety(state: AgentState) -> Literal["evaluate_post", "final_output"]:
    if state.get("is_safe"):
        return "evaluate_post"
    return "final_output"

def decide_after_evaluation(state: AgentState) -> Literal["revise_post", "final_output"]:
    score = state.get("evaluation_score", 0)
    revision_count = state.get("revision_count", 0)
    
    if score >= 7 or revision_count >= 2:
        return "final_output"
    
    return "revise_post"

# --- Graph Construction ---

workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("generate_post", generate_post_node)
workflow.add_node("safety_check", safety_check_node)
workflow.add_node("evaluate_post", evaluate_post_node)
workflow.add_node("revise_post", revise_post_node)
workflow.add_node("final_output", final_output_node)

# Set Entry Point
workflow.set_entry_point("generate_post")

# Add Edges
workflow.add_edge("generate_post", "safety_check")

workflow.add_conditional_edges("safety_check", decide_after_safety)
workflow.add_conditional_edges("evaluate_post", decide_after_evaluation)

workflow.add_edge("revise_post", "safety_check")
workflow.add_edge("final_output", END)

# Compile
app = workflow.compile()
