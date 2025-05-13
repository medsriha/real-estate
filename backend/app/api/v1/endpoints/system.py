from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Dict, Any, Optional
import logging
import sqlite3
import os

from app.models.database import PlacesDatabase
from app.core.config import settings
from app.models.schemas import CacheStats, CacheClearResponse

logger = logging.getLogger("real-estate-api")

router = APIRouter()

def get_places_db() -> PlacesDatabase:
    """Dependency to get the Places database"""
    db = PlacesDatabase()
    try:
        yield db
    finally:
        db.close()

def format_size(size_bytes: int) -> str:
    """Format bytes to human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"

@router.get("/health")
async def health_check():
    """API health check endpoint"""
    return {
        "status": "ok",
        "version": "1.0.0"
    }

@router.get("/cache/stats", response_model=CacheStats)
async def cache_stats(places_db: PlacesDatabase = Depends(get_places_db)):
    """Get cache statistics"""
    # Get cache stats from database
    stats = places_db.get_cache_stats()
    
    # Calculate database file size if it exists
    db_size = None
    try:
        if os.path.exists(settings.DB_PATH):
            db_size = os.path.getsize(settings.DB_PATH)
    except Exception as e:
        logger.error(f"Error getting database file size: {str(e)}")
    
    # Format the sizes for display
    formatted_stats = {
        "places": stats["places"],
        "photos": stats["photos"],
        "total_cache_size": stats["total_cache_size"],
        "total_cache_size_formatted": format_size(stats["total_cache_size"]),
        "db_size": db_size,
        "db_size_formatted": format_size(db_size) if db_size is not None else "N/A"
    }
    
    return formatted_stats

@router.delete("/cache/clear", response_model=CacheClearResponse)
async def clear_cache(
    type: Optional[str] = None,
    places_db: PlacesDatabase = Depends(get_places_db)
):
    """
    Clear the cache
    
    - **type**: Optional type of cache to clear (places or photos). If not specified, clears all cache.
    """
    if type and type not in ["places", "photos"]:
        raise HTTPException(status_code=400, detail="Invalid cache type. Must be 'places' or 'photos'")
    
    try:
        result = places_db.clear_cache(type)
        
        deleted_count = sum(result["deleted"].values())
        type_str = f"{type} " if type else ""
        
        return {
            "deleted": result["deleted"],
            "success": True,
            "message": f"Successfully cleared {deleted_count} {type_str}cache entries"
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}") 