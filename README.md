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

### 1. Install Python 3.11+

**macOS:**
```bash
# Using Homebrew
brew install python@3.11

# Or download from python.org
# Visit https://www.python.org/downloads/macos/
```

**Windows:**
```bash
# Download from python.org
# Visit https://www.python.org/downloads/windows/
# Make sure to check "Add Python to PATH" during installation
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv
```

**Linux (CentOS/RHEL/Fedora):**
```bash
sudo dnf install python3.11 python3.11-pip
# Or for older versions:
# sudo yum install python3.11 python3.11-pip
```

### 2. Install uv (Python Package Manager)

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Alternative (any platform):**
```bash
pip install uv
```

### 3. Install Ollama

**macOS:**
```bash
# Using Homebrew
brew install ollama

# Or download installer from https://ollama.com/download
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
1. Download the installer from [ollama.com/download](https://ollama.com/download)
2. Run the installer as administrator
3. Restart your terminal after installation

### 4. Start Ollama and Pull the Required LLM Model

**Start Ollama service:**

```bash
# macOS/Linux
ollama serve

# Windows (run in a separate terminal)
ollama serve
```

**Pull the model (in a new terminal):**

```bash
ollama pull gpt-oss:20b
```

This downloads the GPT-OSS 20B model used for generating summaries.

### 5. Clone the Repository

```bash
git clone <repository-url>
cd dbr-ai-summary
```

### 6. Install Python Dependencies

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
EMAIL_PASSWORD=your-gmail-app-password
```

**Alternative:** Export environment variables directly:

**macOS/Linux:**
```bash
export BIBLE_API_KEY="your-api-key-here"
export EMAIL_PASSWORD="your-gmail-app-password"
```

**Windows (Command Prompt):**
```cmd
set BIBLE_API_KEY=your-api-key-here
set EMAIL_PASSWORD=your-gmail-app-password
```

**Windows (PowerShell):**
```powershell
$env:BIBLE_API_KEY="your-api-key-here"
$env:EMAIL_PASSWORD="your-gmail-app-password"
```

**Getting API Keys:**

**Bible API Key:**
1. Visit [api.scripture.api.bible](https://scripture.api.bible/)
2. Sign up for a free account
3. Create an API key

**Gmail App Password:**
1. Enable 2-factor authentication on your Gmail account
2. Go to Google Account settings > Security > App passwords
3. Generate a new app password for "Mail"
4. Use this 16-character password (not your regular Gmail password)

**Important:** Both `BIBLE_API_KEY` and `EMAIL_PASSWORD` are required. The app will fail to start if either is not set.

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

**macOS/Linux:**
```bash
python app.py
# or
uv run app.py
```

**Windows:**
```cmd
python app.py
# or
uv run app.py
```

### Test Mode

Sends email to test recipients using today's date or the nearest future weekday:

**macOS/Linux:**
```bash
python app.py --test
# or with environment variable
TEST_MODE=true python app.py
# or with uv
uv run app.py --test
```

**Windows (Command Prompt):**
```cmd
python app.py --test
# or with environment variable
set TEST_MODE=true && python app.py
# or with uv
uv run app.py --test
```

**Windows (PowerShell):**
```powershell
python app.py --test
# or with environment variable
$env:TEST_MODE="true"; python app.py
# or with uv
uv run app.py --test
```

**Test mode behavior:**
- Uses test recipient list instead of production
- Finds today's reading (or next weekday reading if today is weekend)
- Prints debug information to console

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

1. Open terminal and edit crontab:
```bash
crontab -e
```

2. Add this line (runs at 6 AM weekdays):
```
0 6 * * 1-5 cd /path/to/dbr-ai-summary && /usr/local/bin/python app.py
```

3. Save and exit (Ctrl+X, then Y, then Enter in nano)

### Windows (Task Scheduler)

1. Press `Win + R`, type `taskschd.msc`, press Enter
2. Click "Create Basic Task" in the right panel
3. **Name:** "Daily Bible Reading"
4. **Trigger:** Daily
5. **Start date:** Today, **Time:** 6:00 AM
6. **Recur every:** 1 day
7. **Action:** Start a program
8. **Program/script:** `python` (or full path like `C:\Python311\python.exe`)
9. **Arguments:** `app.py`
10. **Start in:** `C:\path\to\dbr-ai-summary`
11. Click Finish

**To run only on weekdays:**
- After creating, right-click the task > Properties
- Go to Triggers tab > Edit
- Check "Weekly" and select Mon-Fri only

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

**macOS/Linux:**
```bash
echo "BIBLE_API_KEY=your-api-key-here" > .env
echo "EMAIL_PASSWORD=your-gmail-app-password" >> .env
```

**Windows:**
```cmd
echo BIBLE_API_KEY=your-api-key-here > .env
echo EMAIL_PASSWORD=your-gmail-app-password >> .env
```

Or export them directly:

**macOS/Linux:**
```bash
export BIBLE_API_KEY="your-api-key-here"
export EMAIL_PASSWORD="your-gmail-app-password"
```

**Windows:**
```cmd
set BIBLE_API_KEY=your-api-key-here
set EMAIL_PASSWORD=your-gmail-app-password
```

### Bible API 401 Unauthorized

Check that `BIBLE_API_KEY` is set correctly:

**macOS/Linux:**
```bash
# If using .env file
cat .env

# If using export
echo $BIBLE_API_KEY
```

**Windows:**
```cmd
# If using .env file
type .env

# If using set command
echo %BIBLE_API_KEY%
```

### Email Not Sending

- Verify `EMAIL_PASSWORD` environment variable is set with your Gmail app password
- Ensure you're using a Gmail app password (not your regular password)
- Check that 2-factor authentication is enabled on your Gmail account
- Ensure SMTP port 587 is not blocked by firewall
- Verify the sender email address is correct in the code

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
