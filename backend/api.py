import os
import json
import logging
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import uvicorn
from reso_listings import RESOClient, get_address_from_listing
from geo import GeocodingClient, GeocodingDatabase
import time
import argparse


os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("real-estate-api")

app = FastAPI(title="Real Estate Listings API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
reso_client = RESOClient(dataset_id="actris_ref")
geocoder = GeocodingClient()
geocoding_db = GeocodingDatabase()

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = f"{time.time()}-{os.urandom(4).hex()}"
    logger.info(f"Request {request_id} started: {request.method} {request.url.path}")
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(f"Request {request_id} completed: {response.status_code} in {process_time:.4f}s")
    return response

@app.get("/api/listings/active", response_model=List[Dict[str, Any]])
async def get_active_listings(limit: int = Query(10, ge=1, le=100)):
    """
    API endpoint to get active listings with geocoded coordinates
    
    Parameters:
    - limit: Number of listings to return (default: 10, max: 100)
    
    Returns:
    - List of active listings with coordinates
    """
    logger.info(f"Fetching {limit} active residential listings")
    try:
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
                if result and result[0] and result[1]:
                    coordinates = {"lat": result[0], "lng": result[1]}
                    cached_count += 1
                    logger.debug(f"Found cached coordinates for {address}")
            
            # If not in database, geocode the address
            if not coordinates:
                logger.debug(f"Geocoding address: {address}")
                result = geocoder.geocode_address(address)
                
                if result['success']:
                    coordinates = {
                        "lat": result['coordinates']['lat'],
                        "lng": result['coordinates']['lon']
                    }
                    geocoded_count += 1
                    logger.debug(f"Successfully geocoded {address}")
                    
                    # Save to database for future use
                    geocoding_db.save_geocoding_result_to_database(result)
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
                   f"({cached_count} from cache, {geocoded_count} freshly geocoded)")
        return processed_listings
    
    except Exception as e:
        logger.error(f"Error processing listings: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """
    Simple health check endpoint
    """
    logger.debug("Health check called")
    return {"status": "ok"}

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Real Estate Listings API')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    args = parser.parse_args()
    
    logger.info(f"Starting Real Estate Listings API on port {args.port}")
    
    # Run the FastAPI app with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=args.port, log_level="info") 