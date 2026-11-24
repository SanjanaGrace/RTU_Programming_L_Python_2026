"""Running queries against the flight database."""

import math
import re
from datetime import datetime

RECORD_KEYS = {
    "flight_id",
    "origin",
    "destination",
    "departure_datetime",
    "arrival_datetime",
    "price",
}

ALLOWED_KEYS = RECORD_KEYS | {"min_price", "sort_by", "order", "limit"}

DATETIME_PATTERN = r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}"


def valid_datetime(value):
    """Check whether a datetime has the exact required format."""

    if not isinstance(value, str):
        return False

    if not re.fullmatch(DATETIME_PATTERN, value):
        return False

    try:
        datetime.strptime(value, "%Y-%m-%d %H:%M")
        return True
    except ValueError:
        return False


def valid_query(query):
    """Check whether a query object follows all query rules."""

    if not isinstance(query, dict):
        return False

    if not all(key in ALLOWED_KEYS for key in query):
        return False

    # Exact-match string fields
    for key in ("flight_id", "origin", "destination"):
        if key in query and not isinstance(query[key], str):
            return False

    # Datetime filters
    for key in ("departure_datetime", "arrival_datetime"):
        if key in query and not valid_datetime(query[key]):
            return False

    # Price filters
    for key in ("price", "min_price"):
        if key in query:
            value = query[key]

            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return False

            if not math.isfinite(value):
                return False

    # Sorting field
    if "sort_by" in query:
        if not isinstance(query["sort_by"], str):
            return False

        if query["sort_by"] not in RECORD_KEYS:
            return False

    # Order requires sort_by
    if "order" in query:
        if "sort_by" not in query:
            return False

        if query["order"] not in ("asc", "desc"):
            return False

    # Limit must be a non-negative integer
    if "limit" in query:
        limit = query["limit"]

        if isinstance(limit, bool) or not isinstance(limit, int):
            return False

        if limit < 0:
            return False

    return True


def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for one query object."""

    if not valid_query(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    matches = []

    for flight in db:
        # Exact-match filters
        if "flight_id" in query:
            if flight["flight_id"] != query["flight_id"]:
                continue

        if "origin" in query:
            if flight["origin"] != query["origin"]:
                continue

        if "destination" in query:
            if flight["destination"] != query["destination"]:
                continue

        # Departure must be at or after requested time
        if "departure_datetime" in query:
            if flight["departure_datetime"] < query["departure_datetime"]:
                continue

        # Arrival must be at or before requested time
        if "arrival_datetime" in query:
            if flight["arrival_datetime"] > query["arrival_datetime"]:
                continue

        # Maximum price
        if "price" in query:
            if flight["price"] > query["price"]:
                continue

        # Minimum price
        if "min_price" in query:
            if flight["price"] < query["min_price"]:
                continue

        matches.append(flight)

    # Sorting
    if "sort_by" in query:
        sort_key = query["sort_by"]
        descending = query.get("order", "asc") == "desc"

        matches = sorted(
            matches, key=lambda flight: flight[sort_key], reverse=descending
        )

    # Limit results after sorting
    if "limit" in query:
        matches = matches[: query["limit"]]

    return {"query": query, "matches": matches}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list of query objects."""

    if isinstance(queries, dict):
        queries = [queries]

    if not isinstance(queries, list):
        return [{"query": queries, "error": "INVALID_QUERY", "matches": []}]

    return [run_query(db, query) for query in queries]
