import streamlit as st
import logging
from graph import app
from memory_manager import load_memory

# Custom handler to capture logs for the UI
class StreamlitLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.log_buffer = []
        self.log_area = st.empty()

    def emit(self, record):
        msg = self.format(record)
        self.log_buffer.append(msg)
        self.log_area.code("\n".join(self.log_buffer))

def run_agent(business, category, tone, offer):
    """Wraps the graph execution."""
    prompt = f"""
    Business: {business} ({category})
    Tone: {tone}
    Offer: {offer}
    """
    
    initial_state = {
        "original_request": prompt.strip(),
        "revision_count": 0
    }
    
    return app.invoke(initial_state, {"recursion_limit": 10})

# --- UI Layout ---

st.title("AI Marketing Agent")

# Sidebar / Memory Stats
memory = load_memory()
with st.sidebar:
    st.header("Brand Memory")
    st.write(f"**Tone:** {memory.get('brand_tone')}")
    st.write(f"**Learned Hashtags:** {len(memory.get('hashtags', []))}")
    with st.expander("Show Hashtags"):
        st.write(", ".join(memory.get('hashtags', [])))

# Input Form
with st.form("marketing_form"):
    col1, col2 = st.columns(2)
    with col1:
        business_name = st.text_input("Business Name", value="My Coffee Shop")
        category = st.text_input("Category", value="Cafe")
    with col2:
        tone = st.selectbox("Tone", ["Friendly", "Professional", "Witty", "Direct", "Urgent"])
        
    offer_desc = st.text_area("Offer Description", value="Buy 1 Get 1 Free on all iced drinks this weekend.")
    
    submitted = st.form_submit_button("Generate Post")

# Execution & Results
if submitted:
    st.divider()
    
    # Setup Logging Display
    st.subheader("Agent Execution Logs")
    with st.expander("Show Execution Details", expanded=True):
        log_handler = StreamlitLogHandler()
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        logger = logging.getLogger()
        logger.handlers = [] # Clear existing handlers
        logger.addHandler(log_handler)
        logger.setLevel(logging.INFO)
        
        # Run Agent
        with st.spinner("Agent is active..."):
            try:
                # Wrap execution to ensure logs are captured
                result = run_agent(business_name, category, tone, offer_desc)
            
                st.success("Generation Complete!")
                
                # Display Results
                st.subheader("Final Instagram Post")
                st.text_area("Caption", value=result.get("generated_content"), height=150)
                
                col_metrics1, col_metrics2, col_metrics3 = st.columns(3)
                with col_metrics1:
                    st.metric("Quality Score", f"{result.get('evaluation_score', 0)}/10")
                with col_metrics2:
                    safe = result.get('is_safe', False)
                    st.metric("Safety Check", "Passed" if safe else "Failed", delta="Safe" if safe else "-Unsafe")
                with col_metrics3:
                    st.metric("Revisions Needed", result.get('revision_count', 0))
                    
                if result.get('evaluation_feedback'):
                    with st.expander("See Evaluation Feedback"):
                        st.write(result['evaluation_feedback'])
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
