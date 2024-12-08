import redis
import json
from typing import Optional, List

# Redis connection setup
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)


def get_cached_emissions(facility: str, start_date: Optional[str], end_date: Optional[str]) -> List[dict]:
    """
    Fetch emissions data from the Redis cache for a given facility and date range.
    
    :param facility: The facility for which data is requested.
    :param start_date: The start date of the emissions data.
    :param end_date: The end date of the emissions data.
    :return: List of cached emissions data as dictionaries, or an empty list if not found.
    """
    cache_key = f"{facility}:{start_date}:{end_date}"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        return json.loads(cached_data)
    else:
        return []


def set_cached_emissions(facility: str, start_date: Optional[str], end_date: Optional[str], emissions_data: List[dict]):
    """
    Store emissions data in the Redis cache for a given facility and date range.
    
    :param facility: The facility for which data is being cached.
    :param start_date: The start date of the emissions data.
    :param end_date: The end date of the emissions data.
    :param emissions_data: The data to be cached, as a list of dictionaries.
    """
    cache_key = f"{facility}:{start_date}:{end_date}"
    
    redis_client.setex(cache_key, 86400, json.dumps(emissions_data))  # TTL of 24 hours (86400 seconds)
