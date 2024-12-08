from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from services.mongo_service import query_missing_ranges
from services.redis_service import get_cached_emissions, set_cached_emissions
from utils.helpers import validate_date_range  # Import from helpers
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_emissions_from_cache_or_db(facility: str, start_date: Optional[str], end_date: Optional[str]):
    cache_key = f"{facility}:{start_date}:{end_date}"
    
    cached_data = get_cached_emissions(facility, start_date, end_date)
    if cached_data:
        logger.info(f"Cache hit for key: {cache_key}")
        return cached_data

    logger.info(f"Cache miss for key: {cache_key}. Querying database.")
    missing_results = await query_missing_ranges([(start_date, end_date)], facility)
    
    set_cached_emissions(facility, start_date, end_date, missing_results)
    
    return missing_results

@router.get("/api/emissions/")
async def get_emissions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    business_facilities: List[str] = Query(...)
):
    """
    Fetch emissions data grouped by business facility. Handles optional date ranges.
    """
    try:
        # Log the received input
        logger.info(f"Received request with start_date={start_date}, end_date={end_date}, business_facilities={business_facilities}")

        # Validate dates and ensure start_date is not later than end_date
        start_dt, end_dt = validate_date_range(start_date, end_date)

        results = []

        # Process each facility
        for facility in business_facilities:
            # Fetch the emissions data from cache or database
            emissions_data = await get_emissions_from_cache_or_db(facility, start_date, end_date)
            
            # Add the results to the response
            for result in emissions_data:
                result_start = result.get("start_date")
                result_end = result.get("end_date")
                total_emissions = result.get("total_emissions", 0)

                # Ensure no "None" strings are used
                result_start = None if result_start == "None" else result_start
                result_end = None if result_end == "None" else result_end

                # Append results for each facility
                results.append({
                    "facility": facility,
                    "start_date": result_start or "None",
                    "end_date": result_end or "None",
                    "co2": total_emissions
                })

        logger.info(f"Final response data: {results}")
        return {"data": results}

    except HTTPException as e:
        logger.error(f"Error fetching emissions: {str(e.detail)}")
        raise e
    except Exception as e:
        logger.error(f"Error fetching emissions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching emissions: {str(e)}")
