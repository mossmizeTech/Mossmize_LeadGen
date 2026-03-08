"""
City Grid Generator
Divides a city into geographic grid tiles for thorough Google Maps coverage.
"""

import math
import httpx

from app.config import settings


async def geocode_city(city: str) -> dict:
    """
    Use Google Geocoding API to get city bounds and center coordinates.

    Returns:
        dict with keys: lat, lng, northeast, southwest (bounding box)
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": city, "key": settings.google_maps_api_key}

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

    if data["status"] != "OK" or not data["results"]:
        raise ValueError(f"Geocoding failed for city '{city}': {data.get('status')}")

    result = data["results"][0]
    location = result["geometry"]["location"]
    bounds = result["geometry"].get("bounds") or result["geometry"].get("viewport", {})

    return {
        "lat": location["lat"],
        "lng": location["lng"],
        "northeast": bounds.get("northeast", {"lat": location["lat"] + 0.1, "lng": location["lng"] + 0.1}),
        "southwest": bounds.get("southwest", {"lat": location["lat"] - 0.1, "lng": location["lng"] - 0.1}),
    }


def _km_to_degrees_lat(km: float) -> float:
    """Convert kilometers to degrees latitude (approximately)."""
    return km / 111.0


def _km_to_degrees_lng(km: float, latitude: float) -> float:
    """Convert kilometers to degrees longitude at a given latitude."""
    return km / (111.0 * math.cos(math.radians(latitude)))


def create_grid(
    northeast: dict,
    southwest: dict,
    grid_size_km: float | None = None,
) -> list[dict]:
    """
    Create a grid of center points covering the bounding box.

    Args:
        northeast: {"lat": float, "lng": float}
        southwest: {"lat": float, "lng": float}
        grid_size_km: size of each grid tile in km (defaults to settings)

    Returns:
        List of {"lat": float, "lng": float} center points
    """
    if grid_size_km is None:
        grid_size_km = settings.grid_size_km

    min_lat = southwest["lat"]
    max_lat = northeast["lat"]
    min_lng = southwest["lng"]
    max_lng = northeast["lng"]

    center_lat = (min_lat + max_lat) / 2
    step_lat = _km_to_degrees_lat(grid_size_km)
    step_lng = _km_to_degrees_lng(grid_size_km, center_lat)

    grid_points = []
    lat = min_lat + step_lat / 2
    while lat <= max_lat:
        lng = min_lng + step_lng / 2
        while lng <= max_lng:
            grid_points.append({
                "lat": round(lat, 6),
                "lng": round(lng, 6),
            })
            lng += step_lng
        lat += step_lat

    return grid_points


async def generate_city_grid(city: str, grid_size_km: float | None = None) -> list[dict]:
    """
    High-level function: geocode a city and return grid center points.

    Args:
        city: city name (e.g. "Delhi")
        grid_size_km: optional tile size override

    Returns:
        List of {"lat": float, "lng": float} dicts
    """
    geo = await geocode_city(city)
    grid = create_grid(geo["northeast"], geo["southwest"], grid_size_km)
    return grid
