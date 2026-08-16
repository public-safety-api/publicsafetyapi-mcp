"""
publicsafetyapi MCP server — exposes US public safety facility data as MCP tools.

Configure with environment variable:
  PUBLICSAFETYAPI_KEY=your_api_key

Run via uvx:
  uvx publicsafetyapi-mcp
"""

import os
import httpx
from mcp.server.fastmcp import FastMCP

BASE_URL = os.environ.get("PUBLICSAFETYAPI_BASE_URL", "https://api.publicsafetyapi.dev")
API_KEY = os.environ.get("PUBLICSAFETYAPI_KEY", "")

mcp = FastMCP(
    "publicsafetyapi",
    instructions=(
        "Use these tools to look up US public safety facilities: police stations, "
        "fire stations/departments, EMS bases, and hospitals. Data comes from federal "
        "HIFLD, USFA, and CMS sources. The most useful tool is "
        "find_stations_near_address — pass any US street address to find the nearest "
        "facilities. Use get_jurisdiction to determine which city and county contain "
        "a location, which is useful for routing or coverage questions."
    ),
)


def _headers() -> dict:
    if not API_KEY:
        raise ValueError(
            "PUBLICSAFETYAPI_KEY environment variable is not set. "
            "Get a free API key at https://publicsafetyapi.dev"
        )
    return {"X-API-Key": API_KEY, "Accept": "application/json"}


def _get(path: str, params: dict | None = None) -> dict:
    with httpx.Client(base_url=BASE_URL, headers=_headers(), timeout=15) as client:
        response = client.get(path, params=params)
        response.raise_for_status()
        return response.json()


# ---------------------------------------------------------------------------
# Proximity search
# ---------------------------------------------------------------------------

@mcp.tool()
def find_stations_near_address(
    address: str,
    type: str = "",
    radius_miles: float = 10.0,
    limit: int = 5,
) -> dict:
    """
    Find the public safety facilities nearest to a US street address,
    sorted by distance.

    Args:
        address:      Full US street address, e.g. "350 Fifth Ave, New York, NY"
        type:         Optional filter — "fire", "police", "ems", or "hospital".
                      Comma-separate for several; omit to return all types.
        radius_miles: Search radius in miles (0.1–50, default 10)
        limit:        Maximum facilities to return (1–25, default 5)
    """
    params: dict = {"address": address, "radius_miles": radius_miles, "limit": limit}
    if type:
        params["type"] = type
    return _get("/v1/stations/nearby", params=params)


@mcp.tool()
def find_stations_near_coordinates(
    lat: float,
    lng: float,
    type: str = "",
    radius_miles: float = 10.0,
    limit: int = 5,
) -> dict:
    """
    Find the public safety facilities nearest to a latitude/longitude,
    sorted by distance. Use this when you already have coordinates; it skips
    geocoding and is faster than find_stations_near_address.

    Args:
        lat:          Latitude (WGS84)
        lng:          Longitude (WGS84)
        type:         Optional filter — "fire", "police", "ems", or "hospital"
        radius_miles: Search radius in miles (0.1–50, default 10)
        limit:        Maximum facilities to return (1–25, default 5)
    """
    params: dict = {"lat": lat, "lng": lng, "radius_miles": radius_miles, "limit": limit}
    if type:
        params["type"] = type
    return _get("/v1/stations/nearby", params=params)


# ---------------------------------------------------------------------------
# Lookup and browse
# ---------------------------------------------------------------------------

@mcp.tool()
def get_station(station_id: str) -> dict:
    """
    Get the full record for one facility by its ID, including address, phone,
    coordinates, and (for hospitals) beds, trauma level, and ownership.

    Args:
        station_id: Facility ID, e.g. "fire_CA_12345"
    """
    return _get(f"/v1/stations/{station_id}")


@mcp.tool()
def list_stations(
    type: str = "",
    state: str = "",
    name: str = "",
    zip: str = "",
    limit: int = 25,
    offset: int = 0,
) -> dict:
    """
    List or search public safety facilities by type, state, name, or ZIP.
    Use this for questions like "how many fire stations are in Kansas" or to
    find a facility by name. For "what's nearest to X", use
    find_stations_near_address instead.

    Args:
        type:   "fire", "police", "ems", or "hospital" (comma-separate for several)
        state:  Two-letter state code, e.g. "CA"
        name:   Full-text search on the facility name
        zip:    5-digit ZIP code
        limit:  Results per page (1–100, default 25)
        offset: Pagination offset (default 0)
    """
    params: dict = {"limit": limit, "offset": offset}
    for key, value in (("type", type), ("state", state.upper()), ("name", name), ("zip", zip)):
        if value:
            params[key] = value
    return _get("/v1/stations", params=params)


# ---------------------------------------------------------------------------
# Jurisdiction and coverage
# ---------------------------------------------------------------------------

@mcp.tool()
def get_jurisdiction(address: str = "", lat: float | None = None, lng: float | None = None) -> dict:
    """
    Determine which Census-defined place (city/town) contains a location, and
    which agencies most likely respond there. Returns the place name, state,
    Census GEOID, boundary type, and a `likelyAgencies` list of nearby police,
    fire, EMS, and hospital facilities. Useful for routing, coverage reporting,
    or working out which local government and responders serve an address.

    Provide either an address, or a lat/lng pair.

    Args:
        address: Full US street address (geocoded automatically)
        lat:     Latitude (WGS84) — use with lng instead of address
        lng:     Longitude (WGS84) — use with lat instead of address
    """
    if address:
        params: dict = {"address": address}
    elif lat is not None and lng is not None:
        params = {"lat": lat, "lng": lng}
    else:
        raise ValueError("Provide either an address, or both lat and lng.")
    return _get("/v1/jurisdiction", params=params)


@mcp.tool()
def get_state_summary(state_code: str) -> dict:
    """
    Get facility counts by type (fire, police, EMS, hospital) for one state.

    Args:
        state_code: Two-letter state abbreviation, e.g. "CA"
    """
    return _get(f"/v1/states/{state_code.upper()}/summary")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    mcp.run()


if __name__ == "__main__":
    main()
