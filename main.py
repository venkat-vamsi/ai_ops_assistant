import streamlit as st
import time
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.verifier import VerifierAgent
from llm.llm_client import LLMClient

st.set_page_config(page_title="AI Ops Assistant", page_icon="🤖", layout="wide")

with st.sidebar:
    st.header("System Status")
    st.metric("Available Tools", "2")
    st.metric("Active Agents", "3")
    st.divider()
    st.markdown("### Tools")
    st.markdown("- GitHub Search")
    st.markdown("- Weather API")
    st.divider()
    if st.button("Clear History", use_container_width=True):
        st.session_state.history = []
        st.rerun()

def main():
    st.title(" AI Operations Assistant")
    st.markdown("*Natural language task automation with multi-agent reasoning*")
    
    if "history" not in st.session_state:
        st.session_state.history = []
    
    try:
        llm = LLMClient()
        planner = PlannerAgent(llm)
        executor = ExecutorAgent()
        verifier = VerifierAgent(llm)
        
        st.markdown("###  Enter Your Task")
        user_input = st.text_input(
            "Task:",
            placeholder="e.g., Find top 5 Python machine learning repos and check weather in San Francisco",
            help="Describe what you want the AI to do using natural language"
        )
        
        col1, col2 = st.columns([1, 5])
        with col1:
            execute_button = st.button("Execute", type="primary", use_container_width=True)
        
        if execute_button and user_input:
            st.session_state.history.append({"task": user_input, "timestamp": time.time()})
            
            st.markdown("---")
            st.markdown("### Processing Your Request")
            
            try:
                st.write(" Planning steps...")
                plan = planner.create_plan(user_input)
                
                st.markdown("####Generated Plan")
                st.json(plan)
                
                time.sleep(1)
                
                st.write("Executing plan...")
                exec_results = executor.execute_plan(plan)
                
                st.markdown("####Execution Results")
                for step in exec_results.get("steps", []):
                    step_status = "✅" if step["status"] == "success" else "❌"
                    st.markdown(f"{step_status} **Step {step['step_number']}**: {step['description']}")
                
                time.sleep(1)
                
                st.write("✓ Verifying results...")
                verification = verifier.verify_results(user_input, plan, exec_results)
                
                st.success("✅ Task completed!")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                return
            
            output = verification.get("formatted_output", {})
            
            st.divider()
            st.markdown("### Results")
            
            summary = output.get("summary", "Task completed")
            if verification.get("is_complete", False):
                st.success(f"{summary}")
            else:
                st.warning(f"{summary}")
            
            if "data" in output and output["data"]:
                st.markdown("###  Detailed Data")
                
                for item in output["data"]:
                    item_type = item.get("type", "unknown")
                    
                    if item_type == "repo":
                        with st.expander(f" {item.get('name', 'Repository')}", expanded=True):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"** Stars:** {item.get('stars', 'N/A')}")
                            with col2:
                                st.markdown(f"** URL:** [{item.get('name')}]({item.get('url')})")
                            if item.get('description'):
                                st.markdown(f"** Description:** {item.get('description')}")
                            if item.get('language'):
                                st.markdown(f"** Language:** {item.get('language')}")
                    
                    elif item_type == "weather":
                        with st.expander(f" {item.get('name', 'Weather')}", expanded=True):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"** Temperature:** {item.get('temperature', 'N/A')}")
                            with col2:
                                st.markdown(f"** Condition:** {item.get('condition', 'N/A')}")
                            if item.get('humidity'):
                                st.markdown(f"** Humidity:** {item.get('humidity')}")
            else:
                st.info("No data returned from execution")
        
        if st.session_state.history:
            st.divider()
            st.markdown("### Recent Tasks")
            for idx, task in enumerate(reversed(st.session_state.history[-5:])):
                st.text(f"{len(st.session_state.history) - idx}. {task['task']}")
    
    except ValueError as e:
        st.error(f"Configuration Error: {str(e)}")
        st.info("Please ensure your .env file is properly configured with all required API keys.")
    except Exception as e:
        st.error(f"Unexpected Error: {str(e)}")
        st.info("Please check your configuration and try again.")

if __name__ == "__main__":
    main()