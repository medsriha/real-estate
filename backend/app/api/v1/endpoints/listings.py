from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Dict, Any
import logging

from app.services.reso import RESOClient, get_address_from_listing
from app.services.geocoding import GeocodingClient
from app.models.database import GeocodingDatabase

logger = logging.getLogger("real-estate-api")

router = APIRouter()

def get_reso_client() -> RESOClient:
    """Dependency to get the RESO client"""
    return RESOClient(dataset_id="actris_ref")

def get_geocoding_client() -> GeocodingClient:
    """Dependency to get the geocoding client"""
    return GeocodingClient()

def get_geocoding_db() -> GeocodingDatabase:
    """Dependency to get the geocoding database"""
    db = GeocodingDatabase()
    try:
        yield db
    finally:
        db.close()

@router.get("/active", response_model=List[Dict[str, Any]])
async def get_active_listings(
    limit: int = Query(10, ge=1, le=100),
    reso_client: RESOClient = Depends(get_reso_client),
    geocoding_client: GeocodingClient = Depends(get_geocoding_client),
    geocoding_db: GeocodingDatabase = Depends(get_geocoding_db)
):
    """
    Get active real estate listings with geocoded coordinates
    
    - **limit**: Number of listings to return (default: 10, max: 100)
    """
    logger.info(f"Fetching {limit} active residential listings")
    
    # Fetch active listings from RESO API
    active_listings = reso_client.get_active_residential_listings(limit=limit)
    logger.info(f"Retrieved {len(active_listings)} listings from RESO API")
    
    # Process listings to include coordinates
    processed_listings = []
    cached_count = 0
    geocoded_count = 0
    
    for i, listing in enumerate(active_listings):
        # Extract address
        address = get_address_from_listing(listing)
        
        # Skip listings without a valid address
        if not address:
            logger.warning(f"Listing {i+1}/{len(active_listings)} skipped: No valid address found")
            continue
            
        logger.debug(f"Processing listing {i+1}/{len(active_listings)}: {address}")
        
        # Check if we already have coordinates for this address
        coordinates = None
        
        # Check geocoding database first
        if geocoding_db.address_exists_in_db(address):
            # Fetch from database
            cursor = geocoding_db.conn.cursor()
            cursor.execute("SELECT lat, lon FROM geocoding_results WHERE address = ?", (address,))
            result = cursor.fetchone()
            if result and result['lat'] and result['lon']:
                coordinates = {"lat": result['lat'], "lng": result['lon']}
                cached_count += 1
                logger.debug(f"Found cached coordinates for {address}")
        
        # If not in database, geocode the address
        if not coordinates:
            logger.debug(f"Geocoding address: {address}")
            result = geocoding_client.geocode_address(address)
            
            if result['success']:
                coordinates = {
                    "lat": result['coordinates']['lat'],
                    "lng": result['coordinates']['lon']
                }
                geocoded_count += 1
                logger.debug(f"Successfully geocoded {address}")
                
                # Save to database for future use
                geocoding_db.save_geocoding_result(result)
            else:
                logger.warning(f"Failed to geocode address: {address}")
        
        # Only include listings with coordinates
        if coordinates:
            # Add coordinates to the listing
            listing_with_coords = listing.copy()
            listing_with_coords["coordinates"] = coordinates
            processed_listings.append(listing_with_coords)
        else:
            logger.warning(f"No coordinates found for {address}, excluding from results")
    
    logger.info(f"Processed {len(processed_listings)} listings with coordinates " +
               f"(cached: {cached_count}, newly geocoded: {geocoded_count})")
    
    return processed_listings

@router.get("/{listing_key}", response_model=Dict[str, Any])
async def get_listing_details(
    listing_key: str,
    reso_client: RESOClient = Depends(get_reso_client)
):
    """
    Get detailed information for a specific listing
    
    - **listing_key**: The unique key for the listing
    """
    logger.info(f"Fetching details for listing: {listing_key}")
    
    listing = reso_client.get_listing(listing_key)
    
    if not listing:
        logger.warning(f"Listing not found: {listing_key}")
        raise HTTPException(status_code=404, detail="Listing not found")
    
    return listing 