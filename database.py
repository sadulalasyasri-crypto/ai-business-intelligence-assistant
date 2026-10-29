import sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / 'data' / 'sales_data.csv'
DB_PATH = ROOT / 'sales.db'

SCHEMA = """
CREATE TABLE IF NOT EXISTS sales (
    transaction_id TEXT PRIMARY KEY,
    order_date TEXT,
    product TEXT,
    category TEXT,
    region TEXT,
    sales_channel TEXT,
    quantity INTEGER,
    unit_price REAL,
    discount_amount REAL,
    status TEXT,
    data_issue TEXT
);
"""

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database(force_reload=False):
    if not CSV_PATH.exists():
        raise FileNotFoundError(f'CSV file not found: {CSV_PATH}')
    df = pd.read_csv(CSV_PATH, dtype={'Transaction_Id': str})
    # Explicit day-first parsing because the supplied dates look like 03-01-2026.
    df['Order_date'] = pd.to_datetime(df['Order_date'], format='%d-%m-%Y', errors='coerce')
    for col in ['Quantity', 'Unit_price', 'Discount_amount']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['Status'] = df['Status'].astype('string').str.strip().str.title()
    df['Product'] = df['Product'].astype('string').str.strip()
    df['data_issue'] = ''
    df.loc[df['Order_date'].isna(), 'data_issue'] += 'invalid_date;'
    df.loc[df['Product'].isna() | (df['Product'] == ''), 'data_issue'] += 'missing_product;'
    df.loc[df['Unit_price'].isna(), 'data_issue'] += 'missing_unit_price;'
    df.loc[df['Quantity'].isna(), 'data_issue'] += 'invalid_quantity;'
    df.loc[df['Quantity'].notna() & (df['Quantity'] <= 0), 'data_issue'] += 'nonpositive_quantity;'
    df.loc[df['Discount_amount'].isna() | (df['Discount_amount'] < 0), 'data_issue'] += 'invalid_discount;'
    df.loc[~df['Status'].isin(['Completed', 'Returned']), 'data_issue'] += 'invalid_status;'
    with get_connection() as conn:
        conn.execute(SCHEMA)
        if force_reload:
            conn.execute('DELETE FROM sales')
        # Only load once by default; avoid duplicate inserts on every app start.
        count = conn.execute('SELECT COUNT(*) FROM sales').fetchone()[0]
        if count == 0:
            for _, row in df.iterrows():
                order_date = row['Order_date'].strftime('%Y-%m-%d') if pd.notna(row['Order_date']) else None
                def val(x):
                    return None if pd.isna(x) else x.item() if hasattr(x, 'item') else x
                conn.execute('INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (
                    val(row.get('Transaction_Id')), order_date, val(row.get('Product')),
                    val(row.get('Category')), val(row.get('Region')), val(row.get('Sales_channel')),
                    val(row.get('Quantity')), val(row.get('Unit_price')), val(row.get('Discount_amount')),
                    val(row.get('Status')), val(row.get('data_issue')) or None
                ))
        conn.commit()
