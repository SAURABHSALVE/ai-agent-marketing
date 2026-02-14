import json
import logging
import os
from typing import List, TypedDict

MEMORY_FILE = "memory.json"

class Memory(TypedDict):
    brand_tone: str
    hashtags: List[str]

def load_memory() -> Memory:
    """Loads memory from JSON file. Creates default if not exists."""
    if not os.path.exists(MEMORY_FILE):
        default_memory: Memory = {
            "brand_tone": "friendly, professional, and community-focused",
            "hashtags": ["#smallbusiness", "#supportlocal"]
        }
        save_memory(default_memory)
        return default_memory
        
    try:
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        logging.error("Memory file corrupted. Returning default.")
        return {"brand_tone": "friendly", "hashtags": []}

def save_memory(memory: Memory):
    """Saves memory to JSON file."""
    try:
        with open(MEMORY_FILE, 'w') as f:
            json.dump(memory, f, indent=4)
    except Exception as e:
        logging.error(f"Failed to save memory: {e}")

def update_hashtags(new_hashtags: List[str]):
    """Updates global hashtag list with new unique tags."""
    memory = load_memory()
    current_tags = set(memory.get("hashtags", []))
    
    # Add only new valid hashtags (simple validation)
    updated = False
    for tag in new_hashtags:
        tag = tag.strip().lower()
        if tag.startswith('#') and tag not in current_tags:
            current_tags.add(tag)
            updated = True
    
    if updated:
        memory["hashtags"] = list(current_tags)
        save_memory(memory)
        logging.info("Memory updated with new hashtags.")
