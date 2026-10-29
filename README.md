# Mini AI Business Intelligence Assistant

A small Flask app that answers sales questions using SQLite calculations. It supports total revenue, top product, monthly trend, top region, and revenue comparison between two months.

## Requirements
- Python 3.10 or newer
- Internet access only if you want to use the optional OpenAI API

## 1. Open the project folder
Open a terminal in this folder (`ai-business-intelligence-assistant`).

## 2. Create and activate a virtual environment

Windows PowerShell:
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```
If PowerShell blocks activation, use Command Prompt:
```bat
py -m venv .venv
.venv\Scripts\activate.bat
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. (Optional) Configure the LLM
Without an API key, the app uses its local question interpreter. To enable the OpenAI LLM, set your own API key in the terminal before starting the app. Never commit the key to GitHub.

Windows PowerShell:
```powershell
$env:OPENAI_API_KEY="paste-your-own-key-here"
$env:OPENAI_MODEL="gpt-4o-mini"
```

Windows Command Prompt:
```bat
set OPENAI_API_KEY=paste-your-own-key-here
set OPENAI_MODEL=gpt-4o-mini
```

macOS/Linux:
```bash
export OPENAI_API_KEY="paste-your-own-key-here"
export OPENAI_MODEL="gpt-4o-mini"
```

## 5. Run the application
```bash
python app.py
```
Open `http://127.0.0.1:5000` in your browser. Stop the server with Ctrl+C.

The SQLite database `sales.db` is created automatically from `data/sales_data.csv` on first run. To rebuild it from the CSV, stop the server, delete `sales.db`, and start the app again.

## 6. Run tests
In a second terminal (with the virtual environment activated):
```bash
python -m unittest -v
```

## Example questions
- What is the total revenue?
- Which product generated the highest revenue?
- Show the monthly revenue trend.
- Which region generated the highest sales?
- Compare revenue between January and February.

## Data quality and revenue definition
Revenue = `(quantity * unit_price) - discount_amount`. Analytics include only completed transactions with a valid date, positive quantity, nonmissing unit price and nonnegative discount. Returned transactions and rows with invalid quantity or missing price are retained in SQLite for auditability but excluded from analytics. The supplied CSV uses day-month-year dates, parsed explicitly to avoid date ambiguity. The zero-quantity row is excluded rather than silently counted as a sale.

## Architecture
Browser UI → Flask `/api/ask` endpoint → question interpreter → fixed analytics functions → SQLite `sales` table → JSON answer with supporting data. The optional LLM chooses only a predefined intent; it does not generate SQL. Queries are fixed and parameterized, and unsupported intents are rejected.

## Known limitations
This is a selection assessment prototype, not a production system. Natural-language coverage is limited, the data spans January–June 2026, and there is no authentication. Do not deploy it publicly without additional security work.
