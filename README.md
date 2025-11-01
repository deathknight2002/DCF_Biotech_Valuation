# DCF Biotech Valuation

This repository contains two main components:

1. **DCF Analysis Web App** - A Dash application for analyzing biotech assets and computing financial viability through discounted cash flow (DCF) analysis.

2. **BT Platform v2** - Advanced prediction API for biotech catalyst analysis with timing prediction, outcome probabilities, momentum scoring, and alpha calculation.

**Note: Loading the web app for the first time may take 2-3 minutes due to Render's free tier limitations.**

## BT Platform - Prediction API v2

A sophisticated prediction system for biotech catalysts featuring:

- **Timing Prediction**: Weibull distributions with hazard spikes for FDA meetings, conferences (ASCO, ESMO, AHA)
- **Outcome Prediction**: Bayesian inference in odds space with PAV isotonic calibration
- **Momentum Scoring**: Peer-neutral company momentum with streak detection
- **Alpha Calculation**: Expected value with downside risk penalty

### Quick Start

```bash
# Run interactive demo
./bt_platform.sh demo

# Start API server
./bt_platform.sh server

# Test endpoints (in another terminal)
./bt_platform.sh test
```

### API Endpoints

The v2 API runs on port 8081 and provides:

- `GET /v2/predict/timing/{id}` - Quarterly timing distribution
- `GET /v2/predict/outcome/{id}` - Success probability with evidence
- `GET /v2/momentum/company/{name}` - Company momentum score (0-100)
- `GET /v2/momentum/therapeutic-areas` - TA momentum map
- `GET /v2/upcoming?limit=20&min_confidence=0.6` - Upcoming catalysts
- `GET /v2/alpha/top?limit=20` - Top catalysts by edge score

### Documentation

See [`bt_platform/README.md`](bt_platform/README.md) for complete documentation including:
- Detailed API reference
- Module usage examples
- Configuration guide
- Development workflow

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

