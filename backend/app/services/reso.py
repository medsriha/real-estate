import requests
from typing import List, Dict, Any, Optional
import logging
from app.core.config import settings

logger = logging.getLogger("real-estate-api")

class RESOClient:
    def __init__(self, dataset_id: str):
        """
        Initialize the RESO API client
        
        Args:
            dataset_id: The RESO dataset ID to connect to
        """
        self.base_url = settings.RESO_BASE_URL
        self.access_token = settings.RESO_SERVER_TOKEN
        self.dataset_id = dataset_id
        self.headers = {
            'Accept': 'application/json'
        }

    def get_active_residential_listings(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch active listings from the RESO Web API
        
        Args:
            limit: Maximum number of listings to return
            
        Returns:
            List of active residential listings
        """
        filter_param = "StandardStatus eq 'Active' and PropertyType eq 'Residential'"
        endpoint = (f"{self.base_url}{self.dataset_id}/Property"
                   f"?access_token={self.access_token}"
                   f"&$filter={filter_param}"
                   f"&$top={limit}")

        try:
            logger.info(f"Fetching {limit} active residential listings from RESO API")
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            listings = response.json().get('value', [])
            logger.info(f"Retrieved {len(listings)} listings from RESO API")
            return listings
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching active listings: {e}")
            return []

    def get_listing(self, listing_key: str) -> Optional[Dict[str, Any]]:
        """
        Fetch historical data for a specific listing
        
        Args:
            listing_key: The unique key for the listing
            
        Returns:
            Listing data dictionary or None if not found
        """
        endpoint = (f"{self.base_url}{self.dataset_id}/Property('{listing_key}')"
                   f"?access_token={self.access_token}")
        try:
            logger.info(f"Fetching listing details for {listing_key}")
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching listing for {listing_key}: {e}")
            return None


def get_address_from_listing(listing: Dict[str, Any]) -> str:
    """
    Extract a complete address from a listing
    
    Args:
        listing: Listing data dictionary
        
    Returns:
        Complete address as a string
    """
    # Extract address components
    street = listing.get('StreetNumber', '') + ' ' + listing.get('StreetName', '')
    city = listing.get('City', '')
    state = listing.get('StateOrProvince', '')
    postal_code = listing.get('PostalCode', '')
    country = listing.get('Country', 'United States')
    
    # Combine components into a complete address
    address_parts = [part for part in [street.strip(), city, state, postal_code, country] if part]
    return ', '.join(address_parts) 