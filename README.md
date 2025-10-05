# Daily Bible Reading Email with AI Summary

A Python application that sends daily Bible reading emails on weekdays with AI-generated summaries and takeaways. The app fetches scripture passages from the ESV Bible API, generates insightful summaries using a local LLM (via Ollama), and sends formatted HTML emails to a distribution list.

## Features

- **Automated Daily Emails**: Sends readings Monday-Friday based on an Excel reading plan
- **Scripture Fetching**: Retrieves formatted passages from api.scripture.api.bible (ESV translation)
- **AI-Powered Summaries**: Generates contextual summaries and key takeaways using Ollama with markdown formatting support
- **Church of Christ Focus**: AI summaries align with Church of Christ theological perspectives
- **Rich HTML Formatting**: Converts markdown bold (`**text**`) to HTML for beautiful email presentation
- **Test Mode**: Safe testing with alternate recipients and flexible date selection

## Prerequisites

- **Python 3.11** or higher
- **uv** (modern Python package manager)
- **Ollama** (for local LLM inference)
- **Bible API Key** from [api.scripture.api.bible](https://scripture.api.bible/)

## Installation

### 1. Install uv

If you don't have `uv` installed:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

### 2. Install Ollama

Download and install Ollama from [ollama.com](https://ollama.com/)

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:** Download installer from [ollama.com/download](https://ollama.com/download)

### 3. Pull the Required LLM Model

```bash
ollama pull gpt-oss:20b
```

This downloads the GPT-OSS 20B model used for generating summaries.

### 4. Clone the Repository

```bash
git clone <repository-url>
cd dbr-ai-summary
```

### 5. Install Python Dependencies

```bash
uv sync
```

This will install all required dependencies:
- `pandas` - Excel file reading
- `openpyxl` - .xlsx file support
- `requests` - API calls
- `ollama` - LLM integration
- `python-dotenv` - Environment variable loading from .env file

## Configuration

### 1. Set Environment Variables

**Recommended:** Create a `.env` file in the project root:

```bash
BIBLE_API_KEY=your-api-key-here
```

**Alternative:** Export environment variables directly:

```bash
export BIBLE_API_KEY="your-api-key-here"
```

To get a Bible API key:
1. Visit [api.scripture.api.bible](https://scripture.api.bible/)
2. Sign up for a free account
3. Create an API key

**Important:** The `BIBLE_API_KEY` is required. The app will fail to start if it's not set.

### 2. Prepare Reading Plan

Ensure `bible_reading_2025.xlsx` exists in the project root with columns:
- `date` (format: YYYY-MM-DD)
- `reading` (comma-separated passages, e.g., "John 3:16, Psalm 23")

### 3. Configure Email Recipients

Edit `app.py` to set your recipients:
- **Production recipients** (line 204): Full distribution list
- **Test recipients** (line 201): Testing addresses

## Usage

### Normal Mode (Production)

Sends email to production recipients if today is a weekday:

```bash
python app.py
```

### Test Mode

Sends email to test recipients using today's date or the nearest future weekday:

```bash
TEST_MODE=true python app.py
```

Test mode behavior:
- Uses test recipient list instead of production
- Finds today's reading (or next weekday reading if today is weekend)
- Prints debug information to console

### Running with uv

```bash
# Normal mode
uv run app.py

# Test mode
TEST_MODE=true uv run app.py
```

## How It Works

1. **Date Selection**: Determines today's date (or finds nearest weekday in test mode)
2. **Weekend Check**: Exits if Saturday/Sunday (unless test mode finds a weekday)
3. **Excel Lookup**: Finds reading for selected date in `bible_reading_2025.xlsx`
4. **Scripture Fetch**: Retrieves passage text from Bible API
5. **AI Summary**: Generates summary and takeaways using Ollama
6. **Email Send**: Formats and sends HTML email via Gmail SMTP

## Scheduling (Optional)

To run daily automatically:

### macOS/Linux (cron)

```bash
crontab -e
```

Add (runs at 6 AM weekdays):
```
0 6 * * 1-5 cd /path/to/dbr-ai-summary && /usr/local/bin/python app.py
```

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily, Monday-Friday, 6:00 AM
4. Action: Start a program
5. Program: `python`
6. Arguments: `app.py`
7. Start in: `C:\path\to\dbr-ai-summary`

## Troubleshooting

### "Import 'ollama' could not be resolved"

Ensure Ollama is installed and the Python package is available:
```bash
uv add ollama
```

### "No module named 'pandas'"

Install dependencies:
```bash
uv sync
```

### Ollama Connection Error

Make sure Ollama is running:
```bash
ollama serve
```

### "BIBLE_API_KEY environment variable is required"

This error means the API key is not set. Create a `.env` file:
```bash
echo "BIBLE_API_KEY=your-api-key-here" > .env
```

Or export it:
```bash
export BIBLE_API_KEY="your-api-key-here"
```

### Bible API 401 Unauthorized

Check that `BIBLE_API_KEY` is set correctly:
```bash
# If using .env file
cat .env

# If using export
echo $BIBLE_API_KEY
```

### Email Not Sending

- Verify Gmail app password is correct (app.py:98)
- Check that Gmail allows "Less secure app access" or use App Password
- Ensure SMTP port 587 is not blocked by firewall

## Project Structure

```
dbr-ai-summary/
├── app.py                    # Main application
├── bible_reading_2025.xlsx   # Reading plan (date + reading columns)
├── pyproject.toml            # uv dependency configuration
├── uv.lock                   # Locked dependency versions
├── CLAUDE.md                 # AI assistant context
└── README.md                 # This file
```

## Development

### Adding Dependencies

```bash
uv add package-name
```

### Updating Dependencies

```bash
uv lock --upgrade
```

## License

[Add your license here]

## Support

For issues or questions, contact the repository maintainer.
