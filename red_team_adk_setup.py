import os
import sys
import asyncio

# Add the ADK agent repository path so python can resolve its internal imports
ADK_AGENT_PATH = "/tmp/adk-samples/python/agents/customer-service"
if ADK_AGENT_PATH not in sys.path:
    sys.path.insert(0, ADK_AGENT_PATH)

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from customer_service.agent import root_agent

from deepteam import red_team
from deepteam.vulnerabilities import GoalTheft
from deepteam.attacks.single_turn import PromptInjection

from deepeval.models import DeepEvalBaseLLM
from google import genai
from pydantic import BaseModel

# Inject provided API keys 
os.environ["GEMINI_API_KEY"] = "AIzaSyAeiiWi76kQmbiepBikAAHcDpBwLvTTZNA"
os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "0"

os.environ["OPENAI_API_KEY"] = "sk-proj-your-openai-api-key"

# Custom wrapper to allow DeepTeam to use Gemini as an evaluator instead of OpenAI
class GeminiEvalModel(DeepEvalBaseLLM):
    def __init__(self, model_name="gemini-3-pro-preview"):
        self.model_name = model_name
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    def load_model(self):
        return self.client

    def generate(self, prompt: str, schema: BaseModel = None) -> BaseModel:
        # We enforce structured outputs using the requested DeepEval schema if supplied
        config = {"temperature": 0.0}
        if schema is not None:
             config["response_mime_type"] = "application/json"
             config["response_schema"] = schema
             
        res = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=config
        )
        if schema is not None:
            # If a strict schema is expected by DeepTeam, we map the json result directly into the BaseModel 
            return schema.model_validate_json(res.text)
        return res.text

    async def a_generate(self, prompt: str, schema: BaseModel = None) -> BaseModel:
        # Simple async wrapper falling back to sync since DeepEval executes many background tasks
        return self.generate(prompt, schema)

    def get_model_name(self):
        return self.model_name


# deepteam expects a generator or a direct string return
async def adk_model_callback(input: str) -> str:
    """
    This callback routes the adversarial input from DeepTeam into the ADK Customer Service agent.
    We instantiate a Runner and execute the agent, collecting its text response.
    """
    # Set the targeted model directly onto the agent 
    root_agent.model = "gemini-3-pro-preview"

    try:
        # Create an explicit SessionService and an actual Session block
        session_service = InMemorySessionService()
        await session_service.create_session(session_id="deepteam_assessment_session", user_id="deepteam", app_name="customer_service_eval")
        
        # Create the runner mapped to our ADK customer_service agent
        runner = Runner(agent=root_agent, session_service=session_service, app_name="customer_service_eval")
        
        # We collect all text yielded by the agent since it streams responses
        full_response = ""
        
        # We use a static dummy session to avoid maintaining contextual state across different attacks
        message = types.Content(role="user", parts=[types.Part.from_text(text=input)])
        async for event in runner.run_async(user_id="deepteam", session_id="deepteam_assessment_session", new_message=message):
            # The ADK runner yields various Event types. We only want the final 'model_response' or similar text outputs.
            
            # Direct string parsing fallback 
            if hasattr(event, "message") and isinstance(event.message, str):
                full_response += event.message
            elif hasattr(event, "content") and isinstance(event.content, str):
                full_response += event.content
                
            # GenAI message schema parsing
            if hasattr(event, "message") and hasattr(event.message, "parts"):
                for part in event.message.parts:
                    if hasattr(part, "text") and part.text:
                        full_response += part.text
                        
            if hasattr(event, "content") and hasattr(event.content, "parts"):
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        full_response += part.text
                
        # DeepTeam evaluators require a string response back representing the model's behavior
        return full_response.strip() if full_response else "No response generated."
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error occurred during generation: {e}"


if __name__ == "__main__":
    # Ensure ONLY the GoalTheft vulnerability evaluates using the explicitly requested subtypes
    vulnerabilities_to_test = [
        GoalTheft(types=["escalating_probing", "cooperative_dialogue", "social_engineering"])
    ]
    
    prompt_injection = PromptInjection()
    
    # Instantiate Custom Gemini Model for DeepTeam simulating and grading
    gemini_evaluator = GeminiEvalModel(model_name="gemini-3-pro-preview")

    print(f"Starting Red Team assessment on the ADK Customer Service Agent...")
    print(f"Testing {len(vulnerabilities_to_test)} vulnerabilities using Prompt Injection...")
    
    # Run the assessment
    try:
        risk_assessment = red_team(
            model_callback=adk_model_callback, 
            vulnerabilities=vulnerabilities_to_test, 
            attacks=[prompt_injection],
            simulator_model=gemini_evaluator,
            evaluation_model=gemini_evaluator,
            async_mode=True
        )
        
        # Save the report locally
        report_path = "adk_deepteam_risk_assessment_report.json"
        risk_assessment.save(report_path)
        print(f"✅ Assessment complete! Report saved to {report_path}")
        
    except Exception as e:
        print(f"❌ Failed to run deepteam assessment: {e}")
