import requests
import logging
import hashlib
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger("real-estate-api")

class PlacesClient:
    def __init__(self):
        """Initialize the Google Places API client"""
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        self.places_api_url = settings.PLACES_API_BASE_URL
        self.photo_api_url = settings.PLACE_PHOTO_API_URL
        self.photo_api_url_new = settings.PLACE_PHOTO_API_URL_NEW
    
    def search_nearby(
        self, 
        location: str,
        radius: int = 1000, 
        place_type: str = "restaurant",
        keyword: Optional[str] = None,
        pagetoken: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for places near a location
        
        Args:
            location: Location coordinates in "lat,lng" format
            radius: Search radius in meters (max 50000)
            place_type: Type of place to search for
            keyword: Optional search keyword
            pagetoken: Optional page token for pagination
            
        Returns:
            Dictionary with search results
        """
        logger.info(f"Searching for {place_type} places near {location} within {radius}m")
        
        # If using a page token, only that parameter is needed
        if pagetoken:
            params = {
                "key": self.api_key,
                "pageToken": pagetoken
            }
        else:
            # Create location object for the API
            lat, lng = map(float, location.split(','))
            
            location_object = {
                "circle": {
                    "center": {
                        "latitude": lat,
                        "longitude": lng
                    },
                    "radius": radius
                }
            }
            
            # Create the request payload
            payload = {
                "includedTypes": [place_type],
                "locationRestriction": location_object,
                "maxResultCount": 20
            }
            
            # Add keyword if provided
            if keyword:
                payload["textQuery"] = keyword
            
            params = {"key": self.api_key}
        
        # Make the API request
        try:
            # Define the fields needed based on what's used in NearbyPlaces.js
            # Set the field mask based on the data we need for our frontend
            field_mask = "places.displayName,places.id,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.types,places.photos,places.regularOpeningHours,places.priceLevel"
            
            # If using pagetoken, GET request is used
            if pagetoken:
                response = requests.get(
                    self.places_api_url,
                    params=params,
                    headers={"X-Goog-FieldMask": field_mask}
                )
            else:
                # Otherwise, POST request with JSON payload
                headers = {
                    "Content-Type": "application/json",
                    "X-Goog-FieldMask": field_mask
                }
                response = requests.post(
                    self.places_api_url,
                    json=payload,
                    params=params,
                    headers=headers
                )
            
            response.raise_for_status()
            data = response.json()
            
            # Transform the response to match our expected format
            transformed_data = self._transform_places_response(data)
            logger.info(f"Found {len(transformed_data['results'])} places")
            
            return transformed_data
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching for places: {str(e)}")
            error_response = {"error": str(e), "status": "ERROR"}
            if hasattr(e, 'response') and e.response is not None:
                error_response["status_code"] = e.response.status_code
                try:
                    error_response["response"] = e.response.json()
                except:
                    error_response["response"] = e.response.text
            return error_response
    
    def get_place_photo(self, photo_reference: str, max_width: int = 400, max_height: Optional[int] = None) -> Dict[str, Any]:
        """
        Get a place photo from Google Places API
        
        Args:
            photo_reference: Photo reference string
            max_width: Maximum width of the photo
            max_height: Optional maximum height of the photo
            
        Returns:
            Dictionary with photo data and content type
        """
        logger.debug(f"Fetching place photo: {photo_reference[:10]}...")
        
        # Use the new photos API endpoint
        url = f"{self.photo_api_url_new}"
        params = {
            "key": self.api_key,
            "photoReference": photo_reference,
            "maxWidth": max_width
        }
        
        if max_height:
            params["maxHeight"] = max_height
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # Return the photo data and content type
            return {
                "photo_data": response.content,
                "content_type": response.headers.get('Content-Type', 'image/jpeg')
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching photo: {str(e)}")
            
            # If new API fails, try the legacy API
            try:
                legacy_url = f"{self.photo_api_url}"
                # Rename parameters for legacy API
                legacy_params = {
                    "key": self.api_key,
                    "photoreference": photo_reference,
                    "maxwidth": max_width
                }
                
                if max_height:
                    legacy_params["maxheight"] = max_height
                
                legacy_response = requests.get(legacy_url, params=legacy_params)
                legacy_response.raise_for_status()
                
                return {
                    "photo_data": legacy_response.content,
                    "content_type": legacy_response.headers.get('Content-Type', 'image/jpeg')
                }
            except requests.exceptions.RequestException as legacy_error:
                logger.error(f"Both API endpoints failed to fetch photo: {str(legacy_error)}")
                return {
                    "error": f"Failed to fetch photo: {str(e)}, legacy API also failed: {str(legacy_error)}",
                    "status": "ERROR"
                }
    
    def _transform_places_response(self, new_api_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform the new Places API response format to match our expected format
        
        Args:
            new_api_response: Response from the new Places API
            
        Returns:
            Transformed response
        """
        transformed = {
            "results": [],
            "status": "OK"
        }
        
        # Add next page token if available
        if "nextPageToken" in new_api_response:
            transformed["next_page_token"] = new_api_response["nextPageToken"]
        
        # Transform each place
        for place in new_api_response.get("places", []):
            transformed_place = {
                "place_id": place.get("id", ""),
                "name": place.get("displayName", {}).get("text", ""),
                "vicinity": self._extract_vicinity(place),
                "formatted_address": place.get("formattedAddress", ""),
                "geometry": {
                    "location": {
                        "lat": place.get("location", {}).get("latitude", 0),
                        "lng": place.get("location", {}).get("longitude", 0)
                    }
                },
                "types": place.get("types", []),
                "rating": place.get("rating", 0),
                "user_ratings_total": place.get("userRatingCount", 0),
            }
            
            # Add opening hours if available
            if "regularOpeningHours" in place:
                transformed_place["opening_hours"] = {
                    "open_now": place.get("regularOpeningHours", {}).get("openNow", False),
                    "weekday_text": place.get("regularOpeningHours", {}).get("weekdayDescriptions", [])
                }
            
            # Add price level if available
            if "priceLevel" in place:
                price_level_map = {
                    "PRICE_LEVEL_FREE": 0,
                    "PRICE_LEVEL_INEXPENSIVE": 1,
                    "PRICE_LEVEL_MODERATE": 2,
                    "PRICE_LEVEL_EXPENSIVE": 3,
                    "PRICE_LEVEL_VERY_EXPENSIVE": 4
                }
                transformed_place["price_level"] = price_level_map.get(place["priceLevel"], 0)
            
            # Transform photos
            if "photos" in place:
                transformed_place["photos"] = []
                for photo in place["photos"]:
                    # Convert author attributions from objects to strings
                    html_attr_strings = []
                    try:
                        for attr in photo.get("authorAttributions", []):
                            if not isinstance(attr, dict):
                                logger.warning(f"Unexpected authorAttribution format: {attr}")
                                continue
                                
                            display_name = attr.get("displayName", "")
                            uri = attr.get("uri", "")
                            if display_name and uri:
                                html_attr_strings.append(f'<a href="{uri}">{display_name}</a>')
                    except Exception as e:
                        logger.error(f"Error processing photo attribution: {str(e)}")
                        # Provide empty list if there's an error
                        html_attr_strings = []
                    
                    transformed_photo = {
                        "photo_reference": photo.get("name", ""),
                        "height": photo.get("heightPx", 0),
                        "width": photo.get("widthPx", 0),
                        "html_attributions": html_attr_strings
                    }
                    transformed_place["photos"].append(transformed_photo)
            
            transformed["results"].append(transformed_place)
        
        return transformed
    
    def _extract_vicinity(self, place: Dict[str, Any]) -> str:
        """
        Extract a vicinity string from place data
        
        Args:
            place: Place data
            
        Returns:
            Vicinity string
        """
        logger.debug("Extracting vicinity from place data")
        
        # If we have components, use them to build a vicinity string
        vicinity = place.get("formattedAddress", "")
        
        # If address is too long, create a shortened version
        if vicinity and len(vicinity) > 50:
            address_parts = vicinity.split(',')
            if len(address_parts) >= 2:
                # Use the first part and truncate other parts
                vicinity = address_parts[0].strip()
                logger.debug(f"Shortened vicinity to: {vicinity}")
        
        return vicinity
    
    def generate_location_key(self, location: str, radius: int, place_type: str, keyword: Optional[str] = None) -> str:
        """
        Generate a unique key for caching location search results
        
        Args:
            location: Location string (lat,lng)
            radius: Search radius
            place_type: Type of place
            keyword: Optional search keyword
            
        Returns:
            Unique cache key
        """
        logger.debug(f"Generating location key for {place_type} near {location}")
        
        # Create a string with all parameters
        key_string = f"{location}_{radius}_{place_type}"
        if keyword:
            key_string += f"_{keyword}"
        
        # Create a hash of the string
        key = hashlib.md5(key_string.encode()).hexdigest()
        logger.debug(f"Generated location key: {key}")
        
        return key 