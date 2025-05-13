from fastapi import APIRouter, Query, HTTPException, Response, Depends
from typing import Optional
import logging
from starlette.responses import Response

from app.models.schemas import PlacesResponse
from app.services.places import PlacesClient
from app.models.database import PlacesDatabase

logger = logging.getLogger("real-estate-api")

router = APIRouter()

def get_places_client() -> PlacesClient:
    """Dependency to get the Places API client"""
    return PlacesClient()

def get_places_db() -> PlacesDatabase:
    """Dependency to get the Places database"""
    db = PlacesDatabase()
    try:
        yield db
    finally:
        db.close()

@router.get("/nearby", response_model=PlacesResponse)
async def nearby_search(
    location: str,
    radius: int = Query(1000, ge=100, le=50000),
    type: str = "restaurant",
    keyword: Optional[str] = None,
    pagetoken: Optional[str] = None,
    places_client: PlacesClient = Depends(get_places_client),
    places_db: PlacesDatabase = Depends(get_places_db)
):
    """
    Search for places near a location
    
    - **location**: Comma-separated latitude and longitude (e.g., "30.267153,-97.743057")
    - **radius**: Search radius in meters (max: 50000)
    - **type**: Type of place to search for (e.g., restaurant, hospital, school)
    - **keyword**: Optional search keyword to filter results
    - **pagetoken**: Optional page token for pagination
    """
    # If using page token, bypass cache
    if pagetoken:
        logger.info(f"Searching for places with page token: {pagetoken[:10]}...")
        return places_client.search_nearby(
            location=location,
            radius=radius,
            place_type=type,
            keyword=keyword,
            pagetoken=pagetoken
        )
    
    # Generate cache key for this request
    location_key = places_client.generate_location_key(location, radius, type, keyword)
    
    # Check cache first
    cached_results = places_db.get_cached_places(location_key)
    if cached_results:
        logger.info(f"Using cached results for {type} near {location}")
        return cached_results
    
    # If not cached, make API request
    results = places_client.search_nearby(
        location=location,
        radius=radius,
        place_type=type,
        keyword=keyword
    )
    
    # Cache the results if successful
    if "error" not in results:
        places_db.cache_places(
            location_key=location_key,
            location=location,
            radius=radius,
            place_type=type,
            keyword=keyword,
            results=results
        )
    
    return results


@router.post("/clear-cache")
async def clear_places_cache(
    places_db: PlacesDatabase = Depends(get_places_db)
):
    """
    Clear the places cache to force fetching fresh data from API
    """
    try:
        result = places_db.clear_cache("places")
        logger.info(f"Places cache cleared. Deleted {result['deleted'].get('places', 0)} entries.")
        return {"success": True, "message": f"Places cache cleared. Deleted {result['deleted'].get('places', 0)} entries."}
    except Exception as e:
        logger.error(f"Error clearing places cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

@router.get("/schools", response_model=PlacesResponse)
async def nearby_schools(
    location: str,
    radius: int = Query(1500, ge=100, le=50000),
    keyword: Optional[str] = None,
    pagetoken: Optional[str] = None,
    places_client: PlacesClient = Depends(get_places_client),
    places_db: PlacesDatabase = Depends(get_places_db)
):
    """
    Search for schools near a location
    
    - **location**: Comma-separated latitude and longitude (e.g., "30.267153,-97.743057")
    - **radius**: Search radius in meters (max: 50000)
    - **keyword**: Optional search keyword to filter results
    - **pagetoken**: Optional page token for pagination
    """
    # Set the type to school
    place_type = "school"
    
    # If using page token, bypass cache
    if pagetoken:
        logger.info(f"Searching for schools with page token: {pagetoken[:10]}...")
        return places_client.search_nearby(
            location=location,
            radius=radius,
            place_type=place_type,
            keyword=keyword,
            pagetoken=pagetoken
        )
    
    # Generate cache key for this request
    location_key = places_client.generate_location_key(location, radius, place_type, keyword)
    
    # Check cache first
    cached_results = places_db.get_cached_places(location_key)
    if cached_results:
        logger.info(f"Using cached results for schools near {location}")
        return cached_results
    
    # If not cached, make API request
    results = places_client.search_nearby(
        location=location,
        radius=radius,
        place_type=place_type,
        keyword=keyword
    )
    
    # Cache the results if successful
    if "error" not in results:
        places_db.cache_places(
            location_key=location_key,
            location=location,
            radius=radius,
            place_type=place_type,
            keyword=keyword,
            results=results
        )
    
    return results

@router.get("/hospitals", response_model=PlacesResponse)
async def nearby_hospitals(
    location: str,
    radius: int = Query(2000, ge=100, le=50000),
    keyword: Optional[str] = None,
    pagetoken: Optional[str] = None,
    places_client: PlacesClient = Depends(get_places_client),
    places_db: PlacesDatabase = Depends(get_places_db)
):
    """
    Search for hospitals near a location
    
    - **location**: Comma-separated latitude and longitude (e.g., "30.267153,-97.743057")
    - **radius**: Search radius in meters (max: 50000)
    - **keyword**: Optional search keyword to filter results
    - **pagetoken**: Optional page token for pagination
    """
    # Set the type to hospital
    place_type = "hospital"
    
    # If using page token, bypass cache
    if pagetoken:
        logger.info(f"Searching for hospitals with page token: {pagetoken[:10]}...")
        return places_client.search_nearby(
            location=location,
            radius=radius,
            place_type=place_type,
            keyword=keyword,
            pagetoken=pagetoken
        )
    
    # Generate cache key for this request
    location_key = places_client.generate_location_key(location, radius, place_type, keyword)
    
    # Check cache first
    cached_results = places_db.get_cached_places(location_key)
    if cached_results:
        logger.info(f"Using cached results for hospitals near {location}")
        return cached_results
    
    # If not cached, make API request
    results = places_client.search_nearby(
        location=location,
        radius=radius,
        place_type=place_type,
        keyword=keyword
    )
    
    # Cache the results if successful
    if "error" not in results:
        places_db.cache_places(
            location_key=location_key,
            location=location,
            radius=radius,
            place_type=place_type,
            keyword=keyword,
            results=results
        )
    
    return results

@router.get("/grocery", response_model=PlacesResponse)
async def nearby_grocery(
    location: str,
    radius: int = Query(1500, ge=100, le=50000),
    keyword: Optional[str] = None,
    pagetoken: Optional[str] = None,
    places_client: PlacesClient = Depends(get_places_client),
    places_db: PlacesDatabase = Depends(get_places_db)
):
    """
    Search for grocery stores near a location
    
    - **location**: Comma-separated latitude and longitude (e.g., "30.267153,-97.743057")
    - **radius**: Search radius in meters (max: 50000)
    - **keyword**: Optional search keyword to filter results
    - **pagetoken**: Optional page token for pagination
    """
    # Set the type to grocery_or_supermarket
    place_type = "supermarket"
    
    # If using page token, bypass cache
    if pagetoken:
        logger.info(f"Searching for grocery stores with page token: {pagetoken[:10]}...")
        return places_client.search_nearby(
            location=location,
            radius=radius,
            place_type=place_type,
            keyword=keyword,
            pagetoken=pagetoken
        )
    
    # Generate cache key for this request
    location_key = places_client.generate_location_key(location, radius, place_type, keyword)
    
    # Check cache first
    cached_results = places_db.get_cached_places(location_key)
    if cached_results:
        logger.info(f"Using cached results for grocery stores near {location}")
        return cached_results
    
    # If not cached, make API request
    results = places_client.search_nearby(
        location=location,
        radius=radius,
        place_type=place_type,
        keyword=keyword
    )
    
    # Cache the results if successful
    if "error" not in results:
        places_db.cache_places(
            location_key=location_key,
            location=location,
            radius=radius,
            place_type=place_type,
            keyword=keyword,
            results=results
        )
    
    return results

@router.get("/transportation", response_model=PlacesResponse)
async def nearby_transportation(
    location: str,
    radius: int = Query(1500, ge=100, le=50000),
    keyword: Optional[str] = None,
    pagetoken: Optional[str] = None,
    places_client: PlacesClient = Depends(get_places_client),
    places_db: PlacesDatabase = Depends(get_places_db)
):
    """
    Search for public transportation near a location
    
    - **location**: Comma-separated latitude and longitude (e.g., "30.267153,-97.743057")
    - **radius**: Search radius in meters (max: 50000)
    - **keyword**: Optional search keyword to filter results
    - **pagetoken**: Optional page token for pagination
    """
    # Set the type to transit_station
    place_type = "transit_station"
    
    # If using page token, bypass cache
    if pagetoken:
        logger.info(f"Searching for transportation with page token: {pagetoken[:10]}...")
        return places_client.search_nearby(
            location=location,
            radius=radius,
            place_type=place_type,
            keyword=keyword,
            pagetoken=pagetoken
        )
    
    # Generate cache key for this request
    location_key = places_client.generate_location_key(location, radius, place_type, keyword)
    
    # Check cache first
    cached_results = places_db.get_cached_places(location_key)
    if cached_results:
        logger.info(f"Using cached results for transportation near {location}")
        return cached_results
    
    # If not cached, make API request
    results = places_client.search_nearby(
        location=location,
        radius=radius,
        place_type=place_type,
        keyword=keyword
    )
    
    # Cache the results if successful
    if "error" not in results:
        places_db.cache_places(
            location_key=location_key,
            location=location,
            radius=radius,
            place_type=place_type,
            keyword=keyword,
            results=results
        )
    
    return results 