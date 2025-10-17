# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python application that sends daily Bible reading emails on weekdays. It:
- Reads from an Excel file (`bible_reading_2025.xlsx`) containing a yearly reading plan
- Fetches scripture passages from api.scripture.api.bible (ESV translation)
- Generates AI-powered summaries and takeaways using Ollama (local LLM)
- Sends formatted HTML emails via Gmail SMTP to a Google Groups distribution list

## Environment Setup

Python version: 3.11

The project uses `uv` for dependency management (based on `pyproject.toml`).

Required dependencies:
- pandas (for Excel file reading)
- openpyxl (for .xlsx support)
- requests (for API calls)
- ollama (for AI summary generation)

Environment variables:
- `BIBLE_API_KEY`: **Required** - API key for api.scripture.api.bible
- `EMAIL_PASSWORD`: **Required** - Gmail app password for sending emails
- `TEST_MODE`: Optional - Set to "true" to enable test mode (uses test recipients and finds nearest weekday reading)

## Running the Application

**Normal mode:**
```bash
python app.py
```

**Test mode:**
```bash
TEST_MODE=true python app.py
```

The script runs once and:
- Only sends emails Monday-Friday
- Looks up today's date (or nearest future weekday in test mode) in the Excel reading plan
- Fetches passages from the Bible API
- Generates AI summary and takeaways via Ollama
- Sends email if a reading exists for the selected date

## Key Architecture

**Single-file application** (`app.py`):
- `get_passage(reference)`: Uses search API to find verse IDs, then fetches formatted passage content
- `format_reading_list(reading)`: Parses comma-separated passage references
- `generate_summary_and_takeaways(passages_text)`: Uses Ollama to generate AI summary and key takeaways aligned with Church of Christ doctrine
- `send_email(subject, html_body, recipients, sender_name)`: SMTP email via Gmail
- Main flow: Date check → Excel lookup → API fetch → AI summary generation → Email send

**Data Source**: `bible_reading_2025.xlsx` (in project root)
- Expected columns: `date` (YYYY-MM-DD format), `reading` (comma-separated passage references)

**API Configuration**:
- Bible API: Bible ID `de4e12af7f28f599-02` = English Standard Version (ESV)
- Ollama: Uses model `gpt-oss:20b` for summary generation

**Test Mode Behavior**:
- Uses test recipients: `bernardbenson.dl@gmail.com`, `jlselby231@gmail.com`
- Finds today's date or the nearest future weekday with a reading (instead of always selecting Jan 1)
- Prints debugging information to console

## Important Notes

- Recipients list is hardcoded in app.py:229 (production) and app.py:222-226 (test mode)
- Ollama must be running locally with the `gpt-oss:20b` model available
- No error handling for missing Excel file or API failures beyond basic checks
