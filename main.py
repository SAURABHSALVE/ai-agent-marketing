from graph import app
import os

def main():
    # Ensure invalid or missing keys don't crash without a message
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment variables.")
        print("Please create a .env file with your API key.")
        return

    print("--- AI Marketing Agent ---")
    user_input = input("Enter your post request (e.g., 'Promotion for new summer coffee menu'): ")
    
    initial_state = {
        "original_request": user_input,
        "revision_count": 0
    }
    
    # Run the graph
    # We use invoke to run the entire flow. Logging shows progress.
    final_output = app.invoke(initial_state, {"recursion_limit": 10})
    
    print("\n=== FINAL RESULT ===")
    print(f"Content: {final_output['generated_content']}")
    if final_output.get('is_safe') is False:
        print("Status: BLOCKED by Safety Guardrails")
    elif final_output.get('evaluation_score'):
        print(f"Quality Score: {final_output['evaluation_score']}/10")
        print(f"Notes: {final_output.get('evaluation_feedback')}")

if __name__ == "__main__":
    main()
