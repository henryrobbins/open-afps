#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["google-genai", "openai"]
# ///
"""Discuss proof strategies, math problems, or Lean code with Gemini/GPT."""
import argparse
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(Path(os.environ.get("CLI_LOG_PATH", Path(__file__).parents[2] / "cli.log")))],
)
logger = logging.getLogger(__name__)


def discuss(question: str, backend: str = "gemini", model: str | None = None) -> None:
    logger.info("discuss called: backend=%s model=%s question_len=%d", backend, model, len(question))
    if not question.strip():
        logger.error("No question provided")
        print("Error: No question provided.", file=sys.stderr)
        sys.exit(1)

    if backend == "gemini":
        model = model or "gemini-3.1-pro-preview"
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY not set")
            print("Error: Please set GEMINI_API_KEY", file=sys.stderr)
            sys.exit(1)
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=model,
                contents=question,
                config=types.GenerateContentConfig(temperature=0.7),
            )
            if response.text:
                usage = response.usage_metadata
                in_tok = getattr(usage, "prompt_token_count", 0) or 0
                out_tok = getattr(usage, "candidates_token_count", 0) or 0
                logger.info("discuss (gemini) succeeded: response_len=%d in_tokens=%d out_tokens=%d", len(response.text), in_tok, out_tok)
                print(response.text)
            else:
                logger.error("Gemini returned empty response")
                print("Error: Gemini returned empty response.", file=sys.stderr)
                sys.exit(1)
        except Exception as e:
            logger.exception("discuss (gemini) failed: %s", e)
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif backend == "gpt":
        model = model or "gpt-5.4-pro"
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY not set")
            print("Error: Please set OPENAI_API_KEY", file=sys.stderr)
            sys.exit(1)
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            response = client.responses.create(
                model=model,
                input=question,
                reasoning={"effort": "high"},
                text={"verbosity": "high"},
            )
            if response.output:
                usage = response.usage
                in_tok = getattr(usage, "input_tokens", 0) or 0
                out_tok = getattr(usage, "output_tokens", 0) or 0
                logger.info("discuss (gpt) succeeded: in_tokens=%d out_tokens=%d", in_tok, out_tok)
                print(response.output[-1].content[0].text)
            else:
                logger.error("GPT returned empty response")
                print("Error: GPT returned empty response.", file=sys.stderr)
                sys.exit(1)
        except Exception as e:
            logger.exception("discuss (gpt) failed: %s", e)
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        logger.error("Invalid backend: %s", backend)
        print(f"Error: backend must be 'gemini' or 'gpt', got '{backend}'", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Discuss with Gemini/GPT")
    parser.add_argument("question", nargs="?", default=None,
                        help="Question text, '-' or omit to read from stdin")
    parser.add_argument("--file", "-f", default=None, metavar="PATH",
                        help="Read question from a file (avoids shell escaping issues)")
    parser.add_argument("--backend", choices=["gemini", "gpt"], default="gemini", help="LLM backend")
    parser.add_argument("--model", default=None, help="Override model name")
    args = parser.parse_args()

    if args.file:
        question = Path(args.file).read_text(encoding="utf-8")
    elif args.question is None or args.question == "-":
        question = sys.stdin.read()
    else:
        question = args.question
    discuss(question, args.backend, args.model)
