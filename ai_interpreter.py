"""Safe question interpretation. Optional OpenAI LLM; deterministic fallback works offline."""
import json
import os
import re

ALLOWED_INTENTS = {'total_revenue', 'top_product', 'monthly_trend', 'top_region', 'compare_months'}
MONTHS = {
    'january': '2026-01', 'jan': '2026-01', 'february': '2026-02', 'feb': '2026-02',
    'march': '2026-03', 'mar': '2026-03', 'april': '2026-04', 'apr': '2026-04',
    'may': '2026-05', 'june': '2026-06', 'jun': '2026-06'
}

def _month_mentions(question):
    q = question.lower()
    found=[]
    for word, month in MONTHS.items():
        if re.search(r'\b' + re.escape(word) + r'\b', q) and month not in found:
            found.append(month)
    return found

def _rule_based(question):
    q = question.lower()
    months = _month_mentions(q)
    if any(k in q for k in ['compare', 'change between', 'difference between', 'how did revenue change']) and len(months) >= 2:
        return {'intent':'compare_months', 'month1':months[0], 'month2':months[1]}
    if any(k in q for k in ['monthly trend', 'month by month', 'revenue by month', 'monthly revenue', 'each month']):
        return {'intent':'monthly_trend'}
    if any(k in q for k in ['which product', 'top product', 'highest revenue product', 'product generated', 'product made']) or ('product' in q and any(k in q for k in ['highest', 'most revenue', 'most money', 'best'])):
        return {'intent':'top_product'}
    if any(k in q for k in ['which region', 'top region', 'highest sales region', 'region generated']) or ('region' in q and any(k in q for k in ['highest', 'most sales', 'best'])):
        return {'intent':'top_region'}
    if any(k in q for k in ['total revenue', 'total sales', 'how much money', 'overall revenue', 'overall sales', 'revenue']) and not months:
        return {'intent':'total_revenue'}
    if len(months) >= 2 and any(k in q for k in ['compare', 'change', 'difference', 'between']):
        return {'intent':'compare_months', 'month1':months[0], 'month2':months[1]}
    raise ValueError('I could not identify this question. Try total revenue, top product, monthly revenue trend, top region, or compare revenue between two months.')

def interpret_question(question):
    """Use an LLM when OPENAI_API_KEY is configured; otherwise use safe local rules.

    The LLM can choose only from a fixed list of intents. It cannot write or execute SQL.
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
                temperature=0,
                response_format={'type':'json_object'},
                messages=[
                    {'role':'system','content':(
                        'Classify the user question into exactly one intent: total_revenue, top_product, '
                        'monthly_trend, top_region, compare_months. Return JSON only with key intent. '
                        'For compare_months include month1 and month2 as YYYY-MM. Dataset dates are in 2026, '
                        'months available January through June. If unsupported return {"intent":"unsupported"}. '
                        'Never produce SQL.' )},
                    {'role':'user','content':question}
                ]
            )
            data = json.loads(response.choices[0].message.content)
            if data.get('intent') not in ALLOWED_INTENTS:
                raise ValueError('Unsupported question.')
            if data['intent'] == 'compare_months':
                # Validate month values before they reach analytics.
                valid_months = {f'2026-{m:02d}' for m in range(1,7)}
                if data.get('month1') not in valid_months or data.get('month2') not in valid_months or data['month1'] == data['month2']:
                    raise ValueError('Please name two different months from January to June 2026.')
            return data
        except ValueError:
            raise
        except Exception:
            # Keep the application usable if the LLM service is unavailable.
            return _rule_based(question)
    return _rule_based(question)
