---
name: redteam-adk
description: Use this skill to execute comprehensive red teaming vulnerability assessments against LLM Model Providers (OpenAI, Gemini, Anthropic) and specialized Google ADK Agents using the deepteam framework. This skill provides the scripts needed to execute these adversarial evaluations and parse their resulting JSON risk reports.

---

# Red Teaming with DeepTeam

This skill provides ready-to-run Python evaluation scripts that wrap the [DeepTeam](https://github.com/confident-ai/deepteam) adversarial benchmarking framework. Use this skill when a user requests to "red team", "evaluate", or "check security vulnerabilities" on either a raw foundation model or an integrated Google ADK application.

## 1. Quick Start 

The skill bundles two execution scripts inside `scripts/`:

### Standard Model Providers (`red_team_setup.py`)
Executes an assessment directly against standard LLM foundational models via SDK integration.
- Target Providers Supported: `openai`, `gemini`, `anthropic`.

### Google ADK Agents (`red_team_adk_setup.py`)
Designed specifically for agents built on `google-adk`. It interacts with the `runner.run_async` object directly, allowing it to extract responses from internal parts hierarchies seamlessly. The target agent path must be appended to `PYTHONPATH`.

## 2. API Key Configuration

Both scripts utilize a custom `gemini` LLM instance to simulate attacks and grade outputs natively. No matter which script you run, you must inject the following API Keys as environment variables or export them in bash before running the scripts:

```python
# Required for DeepTeam Test Evaluation:
os.environ["GEMINI_API_KEY"] = "your-gemini-key"

# Required for 'red_team_setup.py' if evaluating OpenAI or Anthropic targets
os.environ["OPENAI_API_KEY"] = "your-openai-key" 
os.environ["ANTHROPIC_API_KEY"] = "your-anthropic-key"
```

If these keys are not explicitly set or replaced from their placeholder values inside the python scripts, DeepTeam will return `401 Unauthorized` errors inside the test case reports.

## 3. Running an Assessment

Never `cd` into the test application directory. Always execute the assessment script from the root application directory so DeepTeam can map absolute paths!

Execute standard tests:
```bash
python scripts/red_team_setup.py
```

Execute ADK tests (ensure the ADK Agent application is mapped in `PYTHONPATH` prior to this command):
```bash
PYTHONPATH="/path/to/adk-app:$PYTHONPATH" python scripts/red_team_adk_setup.py
```

## 4. Understanding Results

Once execution completes, DeepTeam will automatically write a JSON report object detailing the passed/failed results of each applied vulnerability to the local working directory (e.g. `deepteam_risk_assessment_report.json`). 

If a test passed with a high mitigation rate, the LLM successfully deflected prompt injections!
If you need to analyze *why* a test failed, look at the nested array inside `"test_cases": []`. It contains the adversarial string injected (`input`) and exactly what the LLM responded with (`actual_output`).
