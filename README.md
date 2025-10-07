# DCF Biotech Valuation (Read Note Below)
This is a dash app which lets you to analyze biotech assets and compute their financial viablity through discounted cash flow (DCF) analysis.

**Note: Loading the web app for the first time may take 2-3 minutes due to Render's free tier limitations.**

## Agent Runner

The repository includes `agent_runner.py`, a small utility that helps long-running
Codex-style agents operate with local models managed by [Ollama](https://ollama.ai/).
Provide a prompt and a list of models and the script will attempt each model in
sequence, moving to the next if a timeout occurs.

Example:

```bash
python agent_runner.py --prompt "Write a short poem" --models llama2,codellama --timeout 120
```

The command above feeds the prompt to `llama2` first. If the model exceeds the
specified timeout, the runner switches to `codellama` and continues the task. The
`ollama` CLI must be installed and the referenced models available locally.

