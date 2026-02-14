# AI Marketing Agent for Small Business

A minimal, production-ready AI agent that generates, evaluates, and revises Instagram posts. It features safety guardrails, quality control, and long-term memory.

## Features

- **Automated Workflow**: Generates -> Checks Safety -> Evaluates -> Revises.
- **Safety Guardrails**: Blocks hate speech, medical claims, and financial scams.
- **Quality Control**: Ensures posts are under 150 words and use < 10 hashtags.
- **Long-Term Memory**: Learns your brand tone and hashtags over time (stored in `memory.json`).
- **Robustness**: Auto-retries on API failures.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Key**:
   - Rename `.env.example` to `.env`.
   - Open `.env` and paste your OpenAI API Key:
     ```text
     OPENAI_API_KEY=sk-proj-xyz...
     ```

3. **(Optional) Customize Memory**:
   - Open `memory.json`.
   - Edit `"brand_tone"` to match your business (e.g., "witty and bold" or "professional and calm").

## Usage

Run the agent from the terminal:

```bash
python main.py
```

### Example Interaction

```text
Enter your post request: Promote our new matcha latte with a summer vibe.

--- Generating Post ---
--- Checking Safety ---
--- Evaluating Post ---
--- Revising Post (if needed) ...

=== FINAL RESULT ===
Content: Cool down this summer with our new Iced Matcha Latte! 🍵🌿 Refreshing, creamy, and perfect for the heat. Grab yours today! #SummerVibes #MatchaLovers #CoffeeShop
Quality Score: 9/10
```

## File Structure

- `main.py`: Entry point. Runs the agent.
- `graph.py`: The brain. Defines the workflow nodes and logic.
- `prompts.py`: strict instructions for the AI.
- `memory_manager.py`: Handles reading/writing to `memory.json`.
- `state.py`: Data structure passed between nodes.
