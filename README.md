# Red Teaming Large Language Models

This repository contains scripts and configurations to run a comprehensive red teaming assessment against foundational LLMs (OpenAI, Google Gemini, and Anthropic). The red teaming process is powered by [DeepTeam](https://github.com/confident-ai/deepteam), an LLM red teaming framework.

## Overview

The setup allows you to evaluate your chosen LLM against up to **23 distinct vulnerabilities** (e.g., Bias, Toxicity, PII Leakage, SQL Injection, Intellectual Property theft) using adversarial attack methods such as Prompt Injection.

## Files Provided

*   **`red_team_setup.py`**: A complete Python script that wraps API calls to your chosen model provider and runs the DeepTeam evaluation suite automatically.
*   **`deepteam_config.yaml`**: A pre-configured YAML file you can use if you prefer using the DeepTeam CLI directly.
*   **`Redteam_risk_assessment_report.json`**: An example result report generated after running the script against a model.

## Prerequisites

1.  Python 3.9+
2.  An API Key for the model provider you want to test (OpenAI, Gemini, or Anthropic).

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
pip install -U deepteam google-genai openai anthropic
```

### 2. Configuration

Open `red_team_setup.py`.

1.  **Set your API Keys**: Locate lines 37-39 and replace the placeholder API keys with your actual, active API keys.
    ```python
    os.environ["OPENAI_API_KEY"] = "sk-proj-your-openai-api-key"
    os.environ["GEMINI_API_KEY"] = "AIza-your-gemini-api-key"
    os.environ["ANTHROPIC_API_KEY"] = "sk-ant-your-anthropic-api-key"
    ```
2.  **Choose your Target**: Locate line 42 and set `TARGET_PROVIDER` to the model you wish to evaluate (`"openai"`, `"gemini"`, or `"anthropic"`).

### 3. Run the Assessment

Execute the script:

```bash
python red_team_setup.py
```

*Note: Generating adversarial attacks and evaluating the responses for 23 vulnerabilities requires significant compute time and will likely take several minutes to complete.*

### 4. View Results

Once the red teaming run finishes, the script will automatically save a detailed report of the vulnerabilities and passed/failed results locally as a JSON file (`deepteam_risk_assessment_report.json`). 

## Using the CLI (Alternative)

Instead of the Python script, you can use the deepteam CLI with the provided `deepteam_config.yaml`:

```bash
# Set your keys
deepteam set-api-key "your-openai-api-key" # Assessor model
deepteam set-gemini --google-api-key "your-gemini-api-key" # Target Model

# Run tests
deepteam run deepteam_config.yaml
```
