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

# 1. Provide your chosen models here:
OPENAI_MODEL = "gpt-5"
GEMINI_MODEL = "gemini-3-pro-preview" 
ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"

# Set API keys using your environment context
os.environ["OPENAI_API_KEY"] = "sk-proj-your-openai-api-key"
os.environ["GEMINI_API_KEY"] = "AIza-your-gemini-api-key"
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-your-anthropic-api-key"

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
        PIILeakage(),
        Bias(types=["race", "gender"]), # Bias requires types
        ChildProtection(),
        Ethics(),
        Fairness(),
        Toxicity(types=["profanity", "insults"]), # Toxicity requires types
        SQLInjection(),
        SSRF(),
        ToolMetadataPoisoning(),
        IllegalActivity(),
        PersonalSafety(),
        UnexpectedCodeExecution(),
        Misinformation(),
        IntellectualProperty(),
        Competition(),
        GoalTheft(),
        RecursiveHijacking(),
        ExcessiveAgency(),
        Robustness(),
        IndirectInstruction(),
        ToolOrchestrationAbuse(),
        AgentIdentityAbuse(),
        InsecureInterAgentCommunication()
    ]
    
    # Choose the attack method
    prompt_injection = PromptInjection()

    print(f"Starting Red Team assessment on {TARGET_PROVIDER} using {ANTHROPIC_MODEL if TARGET_PROVIDER == 'anthropic' else (GEMINI_MODEL if TARGET_PROVIDER == 'gemini' else OPENAI_MODEL)}...")
    print(f"Testing {len(vulnerabilities_to_test)} vulnerabilities...")
    
    # Run the assessment
    risk_assessment = red_team(
        model_callback=model_callback, 
        vulnerabilities=vulnerabilities_to_test, 
        attacks=[prompt_injection]
    )
    
    # Save the report locally
    report_path = "deepteam_risk_assessment_report.json"
    risk_assessment.save(report_path)
    print(f"✅ Assessment complete! Report saved to {report_path}")
