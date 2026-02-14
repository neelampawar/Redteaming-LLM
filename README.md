# Red Teaming Large Language Models and Agents(ADK)

This repository contains scripts and configurations to run a comprehensive red teaming assessment against foundational LLMs (OpenAI, Google Gemini, Anthropic) as well as integrated Google ADK Agents. The red teaming process is powered by [DeepTeam](https://github.com/confident-ai/deepteam), an LLM red teaming framework.

## Overview

The setup allows you to evaluate your chosen LLM against up to **23 distinct vulnerabilities** (e.g., Bias, Toxicity, Goal Theft, SQL Injection) using adversarial attack methods such as Prompt Injection.

To facilitate testing without requiring an OpenAI setup, **both evaluators** have been customized to execute prompts using `gemini-3-pro-preview`. 

## Files Provided

*   **`red_team_setup.py`**: A pure python script that tests standard Model Providers directly (OpenAI/Anthropic/Gemini SDKs).
*   **`red_team_adk_setup.py`**: A specialized Python script that tests a complete Google ADK Agent (`customer_service_agent`). It yields context-rich results by interacting with the `Runner` API.
*   **`deepteam_config.yaml`**: A pre-configured YAML file you can use if you prefer using the DeepTeam CLI.

## Prerequisites

1.  Python 3.9+
2.  A [Google Gemini API Key](https://aistudio.google.com/app/apikey) to build the DeepTeam Evaluator model.
3.  Target Model Keys: Anthropic or OpenAI API Keys if testing those via `red_team_setup.py`.

## Quickstart Guide

### 1. Installation

First, clone this repository and set up a virtual environment:

```bash
git clone https://github.com/neelampawar/Redteaming-llm.git
cd Redteaming-llm

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate
```

Install the required dependencies:

```bash
pip install -U deepteam google-genai openai anthropic google-adk
```

### 2. Configuration

1.  **Set your API Keys**: Locate the top configuration block within either of the Python scripts and replace the placeholder API keys with your actual keys.
    ```python
    os.environ["GEMINI_API_KEY"] = "AIza-your-gemini-api-key"
    os.environ["ANTHROPIC_API_KEY"] = "sk-ant-your-anthropic-api-key"
    ```
2.  **Target Provider (`red_team_setup.py` only)**: If testing raw models, set `TARGET_PROVIDER` inside `red_team_setup.py` to your desired model (`"openai"`, `"gemini"`, or `"anthropic"`).

### 3. Run the Assessments

You can execute either script independently:

**To test standard LLM APIs:**
```bash
python red_team_setup.py
```

**To test an ADK Agent:**
```bash
# Make sure your ADK app is available in PYTHONPATH
PYTHONPATH="/path/to/adk-app:$PYTHONPATH" python red_team_adk_setup.py
```

*Note: Generating adversarial attacks takes significant compute time based on the number of vulnerabilities tested.*

### 4. View Results

Once the red teaming run finishes, the scripts will automatically save a detailed report of the vulnerabilities to files locally (`deepteam_risk_assessment_report.json` or `adk_deepteam_risk_assessment_report.json`).
