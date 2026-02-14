import os
import asyncio
from deepteam import red_team
from deepteam.vulnerabilities import (
    Bias,
    Toxicity,
    PIILeakage,
    ChildProtection,
    Ethics,
    Fairness,
    SQLInjection,
    SSRF,
    ToolMetadataPoisoning,
    IllegalActivity,
    PersonalSafety,
    UnexpectedCodeExecution,
    Misinformation,
    IntellectualProperty,
    Competition,
    GoalTheft,
    RecursiveHijacking,
    ExcessiveAgency,
    Robustness,
    IndirectInstruction,
    ToolOrchestrationAbuse,
    AgentIdentityAbuse,
    InsecureInterAgentCommunication,
)
from deepteam.attacks.single_turn import PromptInjection
from deepeval.models import DeepEvalBaseLLM
from pydantic import BaseModel
from google import genai

# Custom wrapper to allow DeepTeam to use Gemini as an evaluator instead of OpenAI
class GeminiEvalModel(DeepEvalBaseLLM):
    def __init__(self, model_name="gemini-3-pro-preview"):
        self.model_name = model_name
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    def load_model(self):
        return self.client

    def generate(self, prompt: str, schema: BaseModel = None) -> BaseModel:
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
            return schema.model_validate_json(res.text)
        return res.text

    async def a_generate(self, prompt: str, schema: BaseModel = None) -> BaseModel:
        return self.generate(prompt, schema)

    def get_model_name(self):
        return self.model_name

# 1. Provide your chosen models here:
OPENAI_MODEL = "gpt-5"
GEMINI_MODEL = "gemini-3-pro-preview" 
ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"

# Set API keys using your environment context
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "sk-proj-your-openai-api-key")
os.environ["GEMINI_API_KEY"] = os.environ.get("GEMINI_API_KEY", "your-gemini-api-key")
os.environ["ANTHROPIC_API_KEY"] = os.environ.get("ANTHROPIC_API_KEY", "sk-ant-your-anthropic-api-key")

# Choose which model to test in this run ("openai", "gemini", or "anthropic")
TARGET_PROVIDER = "anthropic" 

async def model_callback(input: str) -> str:
    """
    This callback routes the adversarial input to the chosen LLM.
    deepteam will use this to generate responses and evaluate them.
    """
    if TARGET_PROVIDER == "openai":
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": input}]
        )
        return response.choices[0].message.content

    elif TARGET_PROVIDER == "gemini":
        from google import genai
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
        # Using LiteLLM or google-genai standard client format
        # deepteam might also have built-in support for target models via yaml as seen in docs.
        # Here we manually wrap it in the callback.
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=input,
        )
        return response.text
        
    elif TARGET_PROVIDER == "anthropic":
        from anthropic import AsyncAnthropic
        client = AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        
        response = await client.messages.create(
            max_tokens=1024,
            model=ANTHROPIC_MODEL,
            messages=[{"role": "user", "content": input}]
        )
        return response.content[0].text
        
    else:
        return "Unknown provider"


if __name__ == "__main__":
    # Choose the vulnerabilities to test
    vulnerabilities_to_test = [
        GoalTheft(types=["escalating_probing", "cooperative_dialogue", "social_engineering"]),
    ]
    
    # Choose the attack method
    prompt_injection = PromptInjection()

    print(f"Starting Red Team assessment on {TARGET_PROVIDER} using {ANTHROPIC_MODEL if TARGET_PROVIDER == 'anthropic' else (GEMINI_MODEL if TARGET_PROVIDER == 'gemini' else OPENAI_MODEL)}...")
    print(f"Testing {len(vulnerabilities_to_test)} vulnerabilities...")
    
    # Instantiate Custom Gemini Model for DeepTeam simulating and grading
    gemini_evaluator = GeminiEvalModel(model_name="gemini-3-pro-preview")
    
    # Run the assessment
    risk_assessment = red_team(
        model_callback=model_callback, 
        vulnerabilities=vulnerabilities_to_test, 
        attacks=[prompt_injection],
        simulator_model=gemini_evaluator,
        evaluation_model=gemini_evaluator
    )
    
    # Save the report locally
    report_path = "deepteam_risk_assessment_report.json"
    risk_assessment.save(report_path)
    print(f"✅ Assessment complete! Report saved to {report_path}")
