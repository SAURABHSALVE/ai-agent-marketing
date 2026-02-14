# Prompt for generating the initial post
GENERATE_POST_PROMPT = """You are a social media expert for a small business.
Write an engaging Instagram post based on this request:
{request}

Constraints:
- Keep the caption under 150 words.
- Use maximum 10 hashtags.
- Do NOT make any medical claims or financial promises.
"""

# Prompt for evaluating the post quality
EVALUATE_POST_PROMPT = """Evaluate this Instagram post for a small business:
{content}

Check for:
1. Engagement potential, clarity, and tone.
2. Word count (must be < 150 words).
3. Hashtag count (must be <= 10).
4. Any medical or financial claims (strictly forbidden).

Rate it from 0 to 10.
- Deduct points significantly if constraints are violated.
- If medical/financial claims are present, score must be 0 and feedback must flag it as unsafe.

Return your response in this format:
Score: [score]
Feedback: [feedback]
"""

# Prompt for safety check
SAFETY_CHECK_PROMPT = """Check if the following content is safe for a business social media account.
Content:
{content}

Violations to look for:
- Hate speech or harassment
- Explicit or adult content
- Dangerous or illegal instructions
- Medical advice or cures (e.g., "cures cancer", "treats anxiety")
- Financial advice or "get rich quick" schemes

If it contains ANY of these, reply with "UNSAFE".
Otherwise, reply with "SAFE".
"""

# Prompt for revising the post
REVISE_POST_PROMPT = """Rewrite the following Instagram post to address the feedback.
Original Post:
{content}

Feedback:
{feedback}

Constraints:
- Keep the caption under 150 words.
- Use maximum 10 hashtags.
- Ensure NO medical or financial claims remain.
"""
