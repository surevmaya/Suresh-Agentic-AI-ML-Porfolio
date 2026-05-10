02-customer-sentiment-agent/README.md
# 02 Customer Sentiment Agent

## What this agent does
Analyses movie sentiment across IMDB and News
sources and recommends Watch or Skip.

## Scoring rule
- Over 75% positive reviews → WATCH ✅
- Under 75% positive reviews → SKIP ❌

## Data sources
- OMDB/IMDB → critic and audience ratings
- News API → press coverage and reviews
- Reddit → coming soon

## Tech stack
- Python
- Anthropic Claude (claude-sonnet-4-6)
- OMDB API
- News API

## How to run
1. Install: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add keys
3. Run: `python agent.py`

## Example use
```python
python agent.py --movie "Citadel"
```

## Real world use case
Help viewers decide what to watch based on
real sentiment analysis across multiple sources.
