import requests
import urllib.parse
import logging
from typing import Dict, Any
from app.core.config import settings

logger = logging.getLogger("real-estate-api")

class GeocodingClient:
    def __init__(self):
        """Initialize the geocoding client"""
        self.api_key = settings.GEOAPIFY_API_KEY
        self.base_url = settings.GEOAPIFY_BASE_URL
        self.headers = {
            "Accept": "application/json"
        }
    
    def geocode_address(self, address: str) -> Dict[str, Any]:
        """
        Geocode an address to get latitude, longitude and other location data
        
        Args:
            address: The address to geocode
            
        Returns:
            dict: The geocoding result with location data
        """
        # URL encode the address
        encoded_address = urllib.parse.quote(address)
        
        # Construct the API URL
        url = f"{self.base_url}?text={encoded_address}&apiKey={self.api_key}"
        
        logger.debug(f"Geocoding address: {address}")
        
        try:
            # Make the request
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            if data.get('features') and len(data['features']) > 0:
                feature = data['features'][0]
                props = feature['properties']
                
                # Extract the most useful information
                result = {
                    'success': True,
                    'address': address,
                    'coordinates': {
                        'lat': props.get('lat'),
                        'lon': props.get('lon')
                    },
                    'formatted_address': props.get('formatted'),
                    'address_components': {
                        'house_number': props.get('housenumber'),
                        'street': props.get('street'),
                        'city': props.get('city'),
                        'county': props.get('county'),
                        'state': props.get('state'),
                        'country': props.get('country'),
                        'postcode': props.get('postcode'),
                        'suburb': props.get('suburb')
                    },
                    'place_id': props.get('place_id'),
                    'raw_response': data
                }
                
                logger.debug(f"Successfully geocoded {address}")
                return result
            else:
                logger.warning(f"No geocoding results found for {address}")
                return {
                    'success': False,
                    'address': address,
                    'error': 'No results found',
                    'raw_response': data
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error geocoding address {address}: {str(e)}")
            return {
                'success': False,
                'address': address,
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None)
            } 