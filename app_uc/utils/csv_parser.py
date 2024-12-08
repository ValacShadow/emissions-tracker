import pandas as pd
from io import TextIOWrapper
from typing import AsyncGenerator, Dict


async def parse_csv(file) -> AsyncGenerator[list[Dict], None]:
    """Asynchronously parse CSV content in chunks using Pandas and yield transactions."""
    CHUNK_SIZE = 1000

    chunk_iter = pd.read_csv(TextIOWrapper(file, encoding="utf-8"), chunksize=CHUNK_SIZE)

    for chunk in chunk_iter:
        
        # Clean column names by stripping spaces and converting to lowercase
        chunk.columns = chunk.columns.str.strip().str.lower().str.replace(' ', '_')

        required_columns = ['transaction_id', 'item_description', 'business_facility', 'transaction_date', 'co2_item']
        if not all(col in chunk.columns for col in required_columns):
            print(f"Error: Some required columns are missing: {set(required_columns) - set(chunk.columns)}")
            continue

        chunk = chunk[['transaction_id', 'item_description', 'business_facility', 'transaction_date', 'co2_item']]

        chunk['transaction_id'] = chunk['transaction_id'].astype(str)

        chunk['co2_item'] = pd.to_numeric(chunk['co2_item'], errors='coerce')

        transactions = chunk.to_dict(orient='records')

        yield transactions
