import os
import asyncio
import motor.motor_asyncio

from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Tuple
from pymongo import UpdateOne
from fastapi import HTTPException
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

MONGO_DETAILS = os.getenv("MONGO_DETAILS")
DB_NAME = os.getenv("DB_NAME")
TRANSACTIONS_COLLECTION = os.getenv("TRANSACTIONS_COLLECTION")
MAX_RETRIES = 3
RETRY_DELAY = 2


if not MONGO_DETAILS:
    raise ValueError("MONGO_DETAILS environment variable is not set")

try:
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

    db = client[DB_NAME]  
    transaction_collection = db[TRANSACTIONS_COLLECTION]

    async def verify_connection():
        try:
            await client.server_info()
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            raise

except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    raise


async def close_connection():
    """Gracefully close the MongoDB connection."""
    try:
        client.close()
        print("MongoDB connection closed.")
    except Exception as e:
        print(f"Error closing MongoDB connection: {e}")
 

async def safe_bulk_write(operations, retries=MAX_RETRIES):
    for attempt in range(retries):
        try:
            await transaction_collection.bulk_write(operations)
            return
        except Exception as e:
            logger.error(f"Bulk write failed (attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                await asyncio.sleep(RETRY_DELAY)
            else:
                raise


async def insert_or_update_transactions(data: List[Dict], batch_size: int = 5000):
    try:
        operations = []

        for row in data:
            transaction_id = row.get("transaction_id")
            if not transaction_id:
                continue

            if "transaction_date" in row and row["transaction_date"]:
                try:
                    # Assuming the format is "MM/DD/YY" or "M/D/YY"
                    row["transaction_date"] = datetime.strptime(row["transaction_date"], "%d/%m/%y")
                except ValueError as e:
                    logger.warning(f"Invalid date format for transaction_id {transaction_id}: {e}")
                    continue

            clean_row = {key: value for key, value in row.items() if key and value not in [None, "", {}]}
            if not clean_row:
                continue

            operation = UpdateOne(
                {"transaction_id": transaction_id},
                {"$set": clean_row},
                upsert=True
            )
            operations.append(operation)

            if len(operations) == batch_size:
                await safe_bulk_write(operations)
                operations.clear()

        if operations:
            await safe_bulk_write(operations)

        logger.info(f"Successfully processed {len(data)} transactions")
    except Exception as e:
        logger.error(f"Error inserting/updating transactions: {e}")
        raise


async def query_emissions(filters, group_by):
    """
    Query MongoDB for emissions based on dynamic filters.
    Args:
        filters: Dict of conditions (e.g., {"business_facility": {"$in": ["CHANGI_20_976-1"]}})
        group_by: Field to group by (e.g., "business_facility").
    Returns:
        List of aggregated results.
    """
    collection = db[TRANSACTIONS_COLLECTION]
    pipeline = [
        {"$match": filters},
        {"$group": {
            "_id": f"${group_by}",
            "total_emissions": {"$sum": "$co2_item"}
        }}
    ]
    cursor = collection.aggregate(pipeline)
    results = await cursor.to_list(length=None)  # Consume the async cursor
    return results


async def query_missing_ranges(missing_ranges: List[Tuple[str, str]], facility: str):
    """
    Query MongoDB for missing date ranges and return aggregated results.
    """
    results = []
    for start_date, end_date in missing_ranges:
        print("dates", start_date, end_date)
        if not start_date and not end_date:

            filters = {
                "business_facility": {"$in": [facility]}
            }
        else:
            try:
                start_date_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
                end_date_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")

            # Ensure start_date is not after end_date
            if start_date_dt and end_date_dt and start_date_dt > end_date_dt:
                raise HTTPException(status_code=400, detail="start_date cannot be after end_date.")
                
            filters = {
                "transaction_date": {
                    "$gte": start_date_dt, 
                    "$lte": end_date_dt
                },
                "business_facility": {"$in": [facility]}
            }
        logger.info(f"Querying MongoDB with filters: {filters}")
        
        try:
            # Call query_emissions with the filters
            partial_results = await query_emissions(filters, group_by="business_facility")
            logger.info(f"Results from MongoDB for range {start_date}-{end_date}: {partial_results}")

            partial_results[-1]['start_date'] = start_date
            partial_results[-1]['end_date'] = end_date
            results.extend(partial_results)
        except Exception as e:
            logger.error(f"Error querying MongoDB for range {start_date}-{end_date}: {e}")
            raise HTTPException(status_code=500, detail=f"Error querying MongoDB: {str(e)}")

    return results