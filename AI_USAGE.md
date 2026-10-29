# AI usage and debugging notes

## AI tools used
- ChatGPT was used to help plan the architecture, draft code, and prepare test cases. Edit this section to accurately reflect the tools you actually used.
- Optional runtime LLM: OpenAI API via the `openai` Python package when `OPENAI_API_KEY` is configured. Without a key or if the API is unavailable, the app uses a local rule-based intent parser.

## How AI is used
The optional LLM classifies the user's question into one of five fixed intents. It is not allowed to generate SQL. The application validates the intent and calculates the answer using fixed, parameterized SQLite queries. If no API key is configured, a simple rule-based parser handles the supported question patterns.

## Data decisions
- Dates are parsed explicitly as day-month-year and stored as ISO `YYYY-MM-DD` strings.
- Revenue is defined as `(quantity * unit_price) - discount_amount`.
- Only `Completed` transactions with positive quantity and nonmissing price/discount and valid dates are included in analytics.
- Returned transactions are excluded from completed-sales revenue.
- The row with missing unit price and the row with zero quantity are retained in the database for auditability but excluded from analytics.
- “Highest sales by region” is interpreted as highest net revenue. State this assumption if asked.

## Debugging notes
Before submission, replace or expand this section with real issues you encountered, the exact error messages, and how you fixed them. Do not claim an issue happened if it did not.

## Limitations
- Dataset covers January through June 2026 only.
- The local fallback supports common phrasing, not every possible natural-language question.
- Month comparison assumes the dataset year is 2026 and accepts January through June.
- This is a demo app; do not expose it publicly without authentication, production configuration, and additional security review.
