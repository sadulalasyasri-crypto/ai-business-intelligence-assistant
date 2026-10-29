from database import get_connection

REVENUE_EXPR = '(quantity * unit_price - discount_amount)'
VALID_WHERE = "status = 'Completed' AND quantity > 0 AND unit_price IS NOT NULL AND discount_amount IS NOT NULL AND discount_amount >= 0 AND order_date IS NOT NULL"

def _money(value):
    return round(float(value or 0), 2)

def answer_question(intent_data, original_question=''):
    intent = intent_data.get('intent')
    with get_connection() as conn:
        if intent == 'total_revenue':
            row = conn.execute(f'SELECT SUM({REVENUE_EXPR}) AS revenue, COUNT(*) AS transactions FROM sales WHERE {VALID_WHERE}').fetchone()
            return {'question':original_question, 'intent':intent, 'answer':f"Total revenue is { _money(row['revenue']):,.2f}.", 'data':{'total_revenue':_money(row['revenue']), 'eligible_transactions':row['transactions']}, 'policy':'Completed transactions with positive quantity and valid price/discount are included. Returned and invalid rows are excluded.'}
        if intent == 'top_product':
            rows = conn.execute(f"""SELECT product, ROUND(SUM({REVENUE_EXPR}),2) AS revenue, SUM(quantity) AS units
                FROM sales WHERE {VALID_WHERE} GROUP BY product ORDER BY revenue DESC, product ASC""").fetchall()
            if not rows: raise ValueError('No valid completed transactions are available.')
            top=rows[0]
            return {'question':original_question, 'intent':intent, 'answer':f"{top['product']} generated the highest revenue: {top['revenue']:,.2f}.", 'data':[dict(r) for r in rows], 'policy':'Only valid completed transactions are included; returned and invalid rows are excluded.'}
        if intent == 'monthly_trend':
            rows=conn.execute(f"""SELECT substr(order_date,1,7) AS month, ROUND(SUM({REVENUE_EXPR}),2) AS revenue
                FROM sales WHERE {VALID_WHERE} GROUP BY substr(order_date,1,7) ORDER BY month""").fetchall()
            return {'question':original_question, 'intent':intent, 'answer':'Monthly revenue trend is shown in the supporting data.', 'data':[dict(r) for r in rows], 'policy':'Only valid completed transactions are included; returned and invalid rows are excluded.'}
        if intent == 'top_region':
            rows=conn.execute(f"""SELECT region, ROUND(SUM({REVENUE_EXPR}),2) AS revenue, SUM(quantity) AS units
                FROM sales WHERE {VALID_WHERE} AND region IS NOT NULL GROUP BY region ORDER BY revenue DESC, region ASC""").fetchall()
            if not rows: raise ValueError('No valid completed transactions are available.')
            top=rows[0]
            return {'question':original_question, 'intent':intent, 'answer':f"{top['region']} generated the highest revenue: {top['revenue']:,.2f}.", 'data':[dict(r) for r in rows], 'policy':'“Highest sales” is interpreted as highest net revenue. Only valid completed transactions are included.'}
        if intent == 'compare_months':
            m1, m2 = intent_data.get('month1'), intent_data.get('month2')
            valid_months={f'2026-{m:02d}' for m in range(1,7)}
            if m1 not in valid_months or m2 not in valid_months or m1 == m2:
                raise ValueError('Please compare two different months from January to June 2026.')
            rows=conn.execute(f"""SELECT substr(order_date,1,7) AS month, ROUND(SUM({REVENUE_EXPR}),2) AS revenue
                FROM sales WHERE {VALID_WHERE} AND substr(order_date,1,7) IN (?,?) GROUP BY substr(order_date,1,7)""",(m1,m2)).fetchall()
            values={r['month']:float(r['revenue'] or 0) for r in rows}
            a,b=values.get(m1,0.0),values.get(m2,0.0)
            diff=round(b-a,2)
            direction='increased' if diff>0 else 'decreased' if diff<0 else 'did not change'
            return {'question':original_question, 'intent':intent, 'answer':f"Revenue {direction} by {abs(diff):,.2f} from {m1} to {m2}.", 'data':[{'month':m1,'revenue':_money(a)},{'month':m2,'revenue':_money(b)}], 'difference':diff, 'policy':'Difference = second month revenue minus first month revenue. Months without eligible transactions are treated as zero.'}
    raise ValueError('Unsupported question. Ask about total revenue, top product, monthly trend, top region, or compare two months.')
