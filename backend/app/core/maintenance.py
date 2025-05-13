#!/usr/bin/env python3
"""
Script to clear expired cache entries from the database
This can be run as a scheduled task (e.g., with cron) to keep the cache size under control
"""

import os
import logging
import datetime
import argparse
import time
import uuid
import sqlite3
from typing import Dict, Any

from app.core.config import settings

# Create log directory
os.makedirs(settings.LOGS_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(settings.LOGS_DIR, "cache_maintenance.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("cache-maintenance")

def format_size(size_bytes: int) -> str:
    """Format bytes to human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"

def clear_expired_cache(db_path: str = settings.DB_PATH, dry_run: bool = False) -> Dict[str, Any]:
    """
    Clear expired cache entries from the database
    
    Args:
        db_path: Path to the SQLite database
        dry_run: If True, don't actually delete entries, just report
        
    Returns:
        Dictionary with statistics about the cleanup operation
    """
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Generate a unique ID for this maintenance run
    run_id = f"maint_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    logger.info(f"[{run_id}] Starting cache maintenance job, dry_run={dry_run}")
    
    start_time = time.time()
    
    try:
        # Connect to database
        logger.debug(f"[{run_id}] Connecting to database at {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Calculate cutoff timestamp
        cutoff_date = datetime.datetime.now() - datetime.timedelta(seconds=settings.CACHE_EXPIRATION)
        cutoff_timestamp = cutoff_date.isoformat()
        logger.debug(f"[{run_id}] Cache expiration cutoff: {cutoff_timestamp}")
        
        # Get database size before cleanup
        try:
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            db_size_before = page_count * page_size
            logger.info(f"[{run_id}] Database size before cleanup: {format_size(db_size_before)}")
        except Exception as e:
            logger.warning(f"[{run_id}] Could not determine database size: {str(e)}")
            db_size_before = None
        
        # Count total entries
        cursor.execute("SELECT COUNT(*) FROM nearby_places")
        total_places = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM place_photos")
        total_photos = cursor.fetchone()[0]
        
        logger.info(f"[{run_id}] Total entries: {total_places} places, {total_photos} photos")
        
        # Get total size of cached data
        cursor.execute("SELECT SUM(LENGTH(results)) FROM nearby_places")
        places_size = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(LENGTH(photo_data)) FROM place_photos")
        photos_size = cursor.fetchone()[0] or 0
        
        total_data_size = places_size + photos_size
        logger.info(f"[{run_id}] Total cached data size: {format_size(total_data_size)} " +
                   f"(Places: {format_size(places_size)}, Photos: {format_size(photos_size)})")
        
        # Find expired entries
        logger.debug(f"[{run_id}] Identifying expired entries older than {cutoff_timestamp}")
        cursor.execute("SELECT COUNT(*) FROM nearby_places WHERE timestamp < ?", (cutoff_timestamp,))
        expired_places = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM place_photos WHERE timestamp < ?", (cutoff_timestamp,))
        expired_photos = cursor.fetchone()[0]
        
        # Get size of expired data
        cursor.execute("SELECT SUM(LENGTH(results)) FROM nearby_places WHERE timestamp < ?", (cutoff_timestamp,))
        expired_places_size = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(LENGTH(photo_data)) FROM place_photos WHERE timestamp < ?", (cutoff_timestamp,))
        expired_photos_size = cursor.fetchone()[0] or 0
        
        expired_data_size = expired_places_size + expired_photos_size
        
        logger.info(f"[{run_id}] Found {expired_places}/{total_places} expired places entries " + 
                   f"({format_size(expired_places_size)})")
        logger.info(f"[{run_id}] Found {expired_photos}/{total_photos} expired photo entries " +
                   f"({format_size(expired_photos_size)})")
        logger.info(f"[{run_id}] Total expired data: {format_size(expired_data_size)}")
        
        deleted_places = 0
        deleted_photos = 0
        
        if not dry_run:
            # Delete expired entries
            if expired_places > 0:
                logger.debug(f"[{run_id}] Deleting {expired_places} expired places entries")
                cursor.execute("DELETE FROM nearby_places WHERE timestamp < ?", (cutoff_timestamp,))
                deleted_places = cursor.rowcount
                logger.info(f"[{run_id}] Deleted {deleted_places} nearby places entries")
            else:
                logger.info(f"[{run_id}] No expired places entries to delete")
            
            if expired_photos > 0:
                logger.debug(f"[{run_id}] Deleting {expired_photos} expired photo entries")
                cursor.execute("DELETE FROM place_photos WHERE timestamp < ?", (cutoff_timestamp,))
                deleted_photos = cursor.rowcount
                logger.info(f"[{run_id}] Deleted {deleted_photos} photo entries")
            else:
                logger.info(f"[{run_id}] No expired photo entries to delete")
            
            conn.commit()
            logger.debug(f"[{run_id}] Committed transaction")
        else:
            logger.info(f"[{run_id}] Dry run - no entries were deleted")
        
        # Run VACUUM to reclaim space
        if not dry_run and (expired_places > 0 or expired_photos > 0):
            logger.info(f"[{run_id}] Running VACUUM to reclaim space...")
            vacuum_start = time.time()
            cursor.execute("VACUUM")
            vacuum_time = time.time() - vacuum_start
            logger.info(f"[{run_id}] VACUUM completed in {vacuum_time:.2f}s")
            
            # Check database size after vacuum
            try:
                cursor.execute("PRAGMA page_count")
                page_count = cursor.fetchone()[0]
                cursor.execute("PRAGMA page_size")
                page_size = cursor.fetchone()[0]
                db_size_after = page_count * page_size
                size_diff = db_size_before - db_size_after if db_size_before is not None else 0
                
                logger.info(f"[{run_id}] Database size after cleanup: {format_size(db_size_after)}")
                if size_diff > 0:
                    logger.info(f"[{run_id}] Space reclaimed: {format_size(size_diff)}")
            except Exception as e:
                logger.warning(f"[{run_id}] Could not determine database size after cleanup: {str(e)}")
        
        # Count remaining entries
        cursor.execute("SELECT COUNT(*) FROM nearby_places")
        remaining_places = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM place_photos")
        remaining_photos = cursor.fetchone()[0]
        
        logger.info(f"[{run_id}] Remaining entries: {remaining_places} places, {remaining_photos} photos")
        
        conn.close()
        logger.debug(f"[{run_id}] Database connection closed")
        
        process_time = time.time() - start_time
        logger.info(f"[{run_id}] Cache maintenance completed in {process_time:.2f}s")
        
        return {
            "run_id": run_id,
            "total": {
                "places": total_places,
                "photos": total_photos,
                "size": format_size(total_data_size)
            },
            "expired": {
                "places": expired_places,
                "photos": expired_photos,
                "size": format_size(expired_data_size)
            },
            "deleted": {
                "places": deleted_places if not dry_run else 0,
                "photos": deleted_photos if not dry_run else 0,
                "size": format_size(expired_data_size) if not dry_run else "0 bytes"
            } if not dry_run else None,
            "remaining": {
                "places": remaining_places,
                "photos": remaining_photos,
                "size_diff": format_size(size_diff) if not dry_run and 'size_diff' in locals() else "N/A"
            },
            "processing_time": f"{process_time:.2f}s"
        }
    except Exception as e:
        logger.error(f"[{run_id}] Error during cache maintenance: {str(e)}")
        return {
            "run_id": run_id,
            "success": False,
            "error": str(e)
        } 