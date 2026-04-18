#!/usr/bin/env python3
"""
Daily AI Model Releases briefing.
Uses Perplexity API (sonar-pro) to research, saves a markdown file,
and posts a summary to Discord via webhook.
"""

import os
import json
import datetime
import requests

PERPLEXITY_API_KEY = os.environ["PERPLEXITY_API_KEY"]
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

TODAY = datetime.date.today()
DATE_LABEL = TODAY.strftime("%B %d, %Y")
FILE_DATE = TODAY.strftime("%Y-%m-%d")
OUTPUT_FILE = f"ai-releases-{FILE_DATE}.md"


def perplexity_search(query: str) -> str:
    """Call Perplexity sonar-pro and return the assistant reply."""
    resp = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a concise AI industry analyst. "
                        "Report only factual, confirmed releases and announcements. "
                        "Include model name, company, key capabilities, specs, and availability."
                    ),
                },
                {"role": "user", "content": query},
            ],
            "max_tokens": 1024,
            "temperature": 0.2,
            "return_citations": True,
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def build_briefing() -> tuple[str, list[str]]:
    """Run three searches and compile the full markdown briefing."""
    queries = [
        f"What new AI models were released or announced on {DATE_LABEL}? Include model name, company, capabilities, specs, and availability.",
        f"What are the latest large language model (LLM), image, video, or multimodal AI announcements in the past 24 hours as of {DATE_LABEL}?",
        f"Any major open-source AI model releases, significant AI benchmarks, or AI hardware announcements today {DATE_LABEL}?",
    ]

    print("Querying Perplexity API...")
    results = []
    for i, q in enumerate(queries, 1):
        print(f"  Query {i}/3...")
        results.append(perplexity_search(q))

    # Combine into a single synthesis prompt
    combined = "\n\n---\n\n".join(results)
    synthesis_query = f"""
Based on these three research summaries about AI releases on {DATE_LABEL}:

{combined}

Produce a concise daily briefing in exactly this markdown format:

## AI Model Releases - {DATE_LABEL}

### Top Updates

For each significant release (aim for 5-8 bullets), use this format:
- **Model name and company** (bold) | What it does / key capabilities (1-2 sentences). Key specs if available. *Status: Released/Beta/Announced*

### Notable Industry Developments
(2-4 bullet points on funding, partnerships, infrastructure news)

### Sources
(list source URLs as markdown links)

Deduplicate entries. Prioritize: new LLM/image/video/multimodal launches, major version updates, open-source releases, hardware announcements.
"""

    print("  Synthesizing final briefing...")
    markdown = perplexity_search(synthesis_query)

    # Extract any URLs mentioned in the raw results for the sources section
    return markdown


def save_markdown(markdown: str) -> str:
    path = os.path.join(os.path.dirname(__file__), OUTPUT_FILE)
    with open(path, "w") as f:
        f.write(markdown + "\n")
    print(f"Saved: {OUTPUT_FILE}")
    return path


def post_to_discord(markdown: str) -> None:
    """Post the briefing to Discord, splitting into chunks under 2000 chars."""
    header = f":robot: **Daily AI Model Briefing — {DATE_LABEL}**\n\n"
    body = markdown

    # Split into chunks ≤ 1900 chars to leave room for header on first chunk
    chunks = []
    current = header
    for line in body.splitlines(keepends=True):
        if len(current) + len(line) > 1900:
            chunks.append(current)
            current = line
        else:
            current += line
    if current:
        chunks.append(current)

    print(f"Posting {len(chunks)} message(s) to Discord...")
    for i, chunk in enumerate(chunks, 1):
        resp = requests.post(
            DISCORD_WEBHOOK_URL,
            json={"content": chunk},
            timeout=15,
        )
        resp.raise_for_status()
        print(f"  Posted chunk {i}/{len(chunks)}")


def main():
    print(f"=== Daily AI Brief: {DATE_LABEL} ===")
    markdown = build_briefing()
    save_markdown(markdown)
    post_to_discord(markdown)
    print("Done.")


if __name__ == "__main__":
    main()
