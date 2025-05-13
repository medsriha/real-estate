import sqlite3
from typing import Dict, Any, Optional
import os
import datetime
import json
import logging
from app.core.config import settings

logger = logging.getLogger("real-estate-api")

class Database:
    def __init__(self):
        self.conn = None

    def connect(self):
        """Create and return a database connection"""
        os.makedirs(os.path.dirname(settings.DB_PATH), exist_ok=True)
        logger.debug(f"Connecting to database at {settings.DB_PATH}")
        # Add check_same_thread=False to allow access from multiple threads
        self.conn = sqlite3.connect(settings.DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            logger.debug("Closing database connection")
            self.conn.close()

    def is_cache_expired(self, timestamp_str: str) -> bool:
        """
        Check if cached data is expired
        
        Args:
            timestamp_str: ISO format timestamp string
            
        Returns:
            bool: True if the cache is expired
        """
        if not timestamp_str:
            return True
        
        try:
            # Parse the timestamp
            timestamp = datetime.datetime.fromisoformat(timestamp_str)
            current_time = datetime.datetime.now()
            
            # Calculate the difference in seconds
            diff = (current_time - timestamp).total_seconds()
            
            # Return True if the cache is expired
            return diff > settings.CACHE_EXPIRATION
        except Exception as e:
            logger.error(f"Error checking cache expiration: {str(e)}")
            return True

class GeocodingDatabase(Database):
    def __init__(self):
        super().__init__()
        self.conn = self.connect()
        self.init_database()
        logger.debug("GeocodingDatabase initialized")

    def init_database(self):
        """Initialize the geocoding database schema"""
        cursor = self.conn.cursor()
        logger.debug("Initializing geocoding database schema")
        
        # Create table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS geocoding_results (
            address TEXT PRIMARY KEY,
            success INTEGER,
            lat REAL,
            lon REAL,
            formatted_address TEXT,
            house_number TEXT,
            street TEXT,
            city TEXT,
            county TEXT,
            state TEXT,
            country TEXT,
            postcode TEXT,
            suburb TEXT,
            place_id TEXT,
            raw_response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        self.conn.commit()

    def address_exists_in_db(self, address: str) -> bool:
        """
        Check if an address already exists in the geocoding database
        
        Args:
            address: Address to check
            
        Returns:
            bool: True if address exists, False otherwise
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM geocoding_results WHERE address = ?", (address,))
        result = cursor.fetchone() is not None
        logger.debug(f"Address '{address[:30]}...' exists in database: {result}")
        return result

    def save_geocoding_result(self, result: Dict[str, Any]) -> None:
        """
        Save geocoding result to SQLite database
        
        Args:
            result: Geocoding result dict to save
        """
        cursor = self.conn.cursor()
        address = result['address']
        
        logger.debug(f"Saving geocoding result for '{address[:30]}...'")
        
        if result['success']:
            # Extract data from result
            cursor.execute('''
            INSERT OR REPLACE INTO geocoding_results 
            (address, success, lat, lon, formatted_address, 
            house_number, street, city, county, state, country, 
            postcode, suburb, place_id, raw_response)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result['address'],
                1 if result['success'] else 0,
                result['coordinates']['lat'],
                result['coordinates']['lon'],
                result.get('formatted_address', ''),
                result['address_components'].get('house_number', ''),
                result['address_components'].get('street', ''),
                result['address_components'].get('city', ''),
                result['address_components'].get('county', ''),
                result['address_components'].get('state', ''),
                result['address_components'].get('country', ''),
                result['address_components'].get('postcode', ''),
                result['address_components'].get('suburb', ''),
                result.get('place_id', ''),
                json.dumps(result.get('raw_response', {}))
            ))
            logger.debug(f"Successfully saved geocoding result for '{address[:30]}...'")
        else:
            # For failed geocoding attempts, just store the address and error
            cursor.execute('''
            INSERT OR REPLACE INTO geocoding_results 
            (address, success, raw_response)
            VALUES (?, ?, ?)
            ''', (
                result['address'],
                0,
                json.dumps(result)
            ))
            logger.debug(f"Saved failed geocoding result for '{address[:30]}...'")
        
        self.conn.commit()

class PlacesDatabase(Database):
    def __init__(self):
        super().__init__()
        self.conn = self.connect()
        self.init_database()
        logger.debug("PlacesDatabase initialized")

    def init_database(self):
        """Initialize the places database schema"""
        cursor = self.conn.cursor()
        logger.debug("Initializing places database schema")
        
        # Create table for caching nearby places results
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS nearby_places (
            location_key TEXT PRIMARY KEY,
            location TEXT,
            radius INTEGER,
            type TEXT,
            keyword TEXT,
            results TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create table for caching place photos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS place_photos (
            photo_reference TEXT PRIMARY KEY,
            photo_data BLOB,
            content_type TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        self.conn.commit()

    def get_cached_places(self, location_key: str) -> Optional[Dict[str, Any]]:
        """Get cached places data if it exists and is not expired"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT results, timestamp FROM nearby_places WHERE location_key = ?", 
            (location_key,)
        )
        result = cursor.fetchone()
        
        if result:
            is_expired = self.is_cache_expired(result['timestamp'])
            if not is_expired:
                logger.debug(f"Found valid places cache for key: {location_key[:15]}...")
                return json.loads(result['results'])
            else:
                logger.debug(f"Found expired places cache for key: {location_key[:15]}...")
        else:
            logger.debug(f"No places cache found for key: {location_key[:15]}...")
        
        return None

    def cache_places(self, location_key: str, location: str, radius: int, place_type: str, 
                     keyword: Optional[str], results: Dict[str, Any]) -> None:
        """Cache places search results"""
        cursor = self.conn.cursor()
        logger.debug(f"Caching places results for location key: {location_key[:15]}...")
        
        cursor.execute(
            """
            INSERT OR REPLACE INTO nearby_places 
            (location_key, location, radius, type, keyword, results, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (location_key, location, radius, place_type, keyword, json.dumps(results))
        )
        self.conn.commit()
        logger.debug(f"Cached {len(results.get('results', []))} places results")

    def get_cached_photo(self, photo_reference: str) -> Optional[Dict[str, Any]]:
        """Get cached photo if it exists and is not expired"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT photo_data, content_type, timestamp FROM place_photos WHERE photo_reference = ?", 
            (photo_reference,)
        )
        result = cursor.fetchone()
        
        if result:
            is_expired = self.is_cache_expired(result['timestamp'])
            if not is_expired:
                logger.debug(f"Found valid photo cache for reference: {photo_reference[:10]}...")
                return {
                    'photo_data': result['photo_data'],
                    'content_type': result['content_type']
                }
            else:
                logger.debug(f"Found expired photo cache for reference: {photo_reference[:10]}...")
        else:
            logger.debug(f"No photo cache found for reference: {photo_reference[:10]}...")
        
        return None

    def cache_photo(self, photo_reference: str, photo_data: bytes, content_type: str) -> None:
        """Cache a photo from Google Places API"""
        cursor = self.conn.cursor()
        data_size = len(photo_data) if photo_data else 0
        logger.debug(f"Caching photo ({data_size} bytes) for reference: {photo_reference[:10]}...")
        
        cursor.execute(
            """
            INSERT OR REPLACE INTO place_photos
            (photo_reference, photo_data, content_type, timestamp)
            VALUES (?, ?, ?, datetime('now'))
            """,
            (photo_reference, photo_data, content_type)
        )
        self.conn.commit()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about cached data"""
        logger.debug("Retrieving cache statistics")
        cursor = self.conn.cursor()
        
        # Get places stats
        cursor.execute("SELECT COUNT(*) FROM nearby_places")
        places_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(LENGTH(results)) FROM nearby_places")
        places_size = cursor.fetchone()[0] or 0
        
        # Get photo stats
        cursor.execute("SELECT COUNT(*) FROM place_photos")
        photos_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(LENGTH(photo_data)) FROM place_photos")
        photos_size = cursor.fetchone()[0] or 0
        
        # Calculate total size
        total_size = places_size + photos_size
        
        logger.info(f"Cache stats: {places_count} places ({places_size} bytes), {photos_count} photos ({photos_size} bytes)")
        
        return {
            "places": {
                "count": places_count,
                "size": places_size
            },
            "photos": {
                "count": photos_count,
                "size": photos_size
            },
            "total_cache_size": total_size
        }

    def clear_cache(self, cache_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Clear the cache
        
        Args:
            cache_type: Type of cache to clear (places or photos). If None, clears all.
            
        Returns:
            Dict with results of the operation
        """
        cursor = self.conn.cursor()
        result = {"deleted": {}}
        
        logger.info(f"Clearing cache {'(' + cache_type + ')' if cache_type else '(all)'}")
        
        try:
            if cache_type is None or cache_type == "places":
                cursor.execute("SELECT COUNT(*) FROM nearby_places")
                places_count = cursor.fetchone()[0]
                cursor.execute("DELETE FROM nearby_places")
                result["deleted"]["places"] = places_count
                logger.info(f"Deleted {places_count} entries from places cache")
            
            if cache_type is None or cache_type == "photos":
                cursor.execute("SELECT COUNT(*) FROM place_photos")
                photos_count = cursor.fetchone()[0]
                cursor.execute("DELETE FROM place_photos")
                result["deleted"]["photos"] = photos_count
                logger.info(f"Deleted {photos_count} entries from photos cache")
            
            self.conn.commit()
            return result
            
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            self.conn.rollback()
            raise 