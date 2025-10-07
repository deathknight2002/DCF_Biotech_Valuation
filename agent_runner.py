"""Utility to cycle through models for a long-running agent task.

This script uses the `ollama` command line interface to run a prompt
against one or more local models.  If a model exceeds the specified
runtime, the script gracefully moves on to the next model in the list.

Example usage:
    python agent_runner.py --prompt "Write a poem" --models llama2,codellama
"""

from __future__ import annotations

import argparse
import itertools
import subprocess
import sys
from pathlib import Path


def read_prompt(source: str) -> str:
    """Return the prompt text.

    ``source`` may be a direct string or a path to a file containing the
    prompt text.  If a file exists at ``source`` it will be read; otherwise
    the value is treated as the literal prompt.
    """
    path = Path(source)
    if path.exists():
        return path.read_text(encoding="utf-8")
    return source


def run_cycle(prompt: str, models: list[str], timeout: int) -> None:
    """Attempt to run ``prompt`` against each model in ``models``.

    Each model is executed through ``ollama run``.  If a model does not
    finish within ``timeout`` seconds, the next model in the list is tried.
    The cycle repeats until one model completes successfully.
    """
    for model in itertools.cycle(models):
        try:
            print(f"[agent] running model: {model}")
            result = subprocess.run(
                ["ollama", "run", model],
                input=prompt,
                text=True,
                capture_output=True,
                timeout=timeout,
            )
            sys.stdout.write(result.stdout)
            if result.stderr:
                sys.stderr.write(result.stderr)
            break
        except subprocess.TimeoutExpired:
            print(f"[agent] model {model} exceeded {timeout}s, trying next model...",
                  file=sys.stderr)
        except FileNotFoundError:
            print("[agent] 'ollama' command not found. Please install ollama to use this script.",
                  file=sys.stderr)
            break


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Cycle through models using ollama")
    parser.add_argument("--prompt", required=True, help="Prompt text or path to prompt file")
    parser.add_argument("--models", required=True, help="Comma-separated model names")
    parser.add_argument("--timeout", type=int, default=300,
                        help="Maximum time in seconds for each model run (default: 300)")
    args = parser.parse_args(argv)

    prompt_text = read_prompt(args.prompt)
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    if not models:
        parser.error("at least one model must be provided")

    run_cycle(prompt_text, models, args.timeout)


if __name__ == "__main__":
    main()
