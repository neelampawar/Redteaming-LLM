import os
import sys
import asyncio

# Add the ADK agent repository path so python can resolve its internal imports
ADK_AGENT_PATH = "/tmp/adk-samples/python/agents/customer-service"
if ADK_AGENT_PATH not in sys.path:
    sys.path.insert(0, ADK_AGENT_PATH)

from google.adk import Runner
from customer_service.agent import root_agent

from deepteam import red_team
from deepteam.vulnerabilities import (
    GoalTheft,
    RecursiveHijacking,
    ExcessiveAgency,
    Robustness,
    IndirectInstruction,
    ToolOrchestrationAbuse,
    AgentIdentityAbuse,
    InsecureInterAgentCommunication,
    AutonomousAgentDrift
)
from deepteam.attacks.single_turn import PromptInjection

# Mock setting Gemini api key for the ADK agent to use (you should replace this with a real key)
if "GEMINI_API_KEY" not in os.environ:
    os.environ["GEMINI_API_KEY"] = "AIzaSy-replace-with-real-gemini-api-key"

# DeepTeam requires an OPENAI_API_KEY for its assessment/evaluator models by default
if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = "sk-proj-replace-with-real-openai-api-key"

# deepteam expects a generator or a direct string return
async def adk_model_callback(input: str) -> str:
    """
    This callback routes the adversarial input from DeepTeam into the ADK Customer Service agent.
    We instantiate a Runner and execute the agent, collecting its text response.
    """
    # Create the runner mapped to our ADK customer_service agent
    runner = Runner(root_agent=root_agent)
    
    # We collect all text yielded by the agent since it streams responses
    full_response = ""
    
    # We use a static dummy session to avoid maintaining contextual state across different attacks
    async for event in runner.run_async(input, session_id="deepteam_assessment_session"):
        # The ADK runner yields various Event types. We only want the final 'model_response' or similar text outputs.
        if hasattr(event, "message") and isinstance(event.message, str):
            full_response += event.message
            
        # In newer ADK versions, events can contain content blocks
        elif hasattr(event, "content") and isinstance(event.content, str):
            full_response += event.content
            
    # DeepTeam evaluators require a string response back representing the model's behavior
    return full_response.strip() if full_response else "No response generated."


if __name__ == "__main__":
    # Choose a targeted subset of vulnerabilities to evaluate on the ADK Agent
    # Testing for the specific 9 agent-centric vulnerabilities requested
    vulnerabilities_to_test = [
        GoalTheft(),
        RecursiveHijacking(),
        ExcessiveAgency(),
        Robustness(),
        IndirectInstruction(),
        ToolOrchestrationAbuse(),
        AgentIdentityAbuse(),
        InsecureInterAgentCommunication(),
        AutonomousAgentDrift()
    ]
    
    prompt_injection = PromptInjection()

    print(f"Starting Red Team assessment on the ADK Customer Service Agent...")
    print(f"Testing {len(vulnerabilities_to_test)} vulnerabilities using Prompt Injection...")
    
    # Run the assessment
    try:
        risk_assessment = red_team(
            model_callback=adk_model_callback, 
            vulnerabilities=vulnerabilities_to_test, 
            attacks=[prompt_injection],
            async_mode=True
        )
        
        # Save the report locally
        report_path = "adk_deepteam_risk_assessment_report.json"
        risk_assessment.save(report_path)
        print(f"✅ Assessment complete! Report saved to {report_path}")
        
    except Exception as e:
        print(f"❌ Failed to run deepteam assessment: {e}")
