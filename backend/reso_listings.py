import os
import requests
import pandas as pd
from dotenv import load_dotenv
import json
from geo import GeocodingClient, GeocodingDatabase

# Load environment variables
load_dotenv()

class RESOClient:
    def __init__(self, dataset_id, base_url="https://api.bridgedataoutput.com/api/v2/OData/", access_token=os.getenv('RESO_SERVER_TOKEN')):
        self.base_url = base_url
        self.access_token = access_token
        self.dataset_id = dataset_id
        self.headers = {
            'Accept': 'application/json'
        }

    def get_active_residential_listings(self, limit=100):
        """
        Fetch active listings from the RESO Web API
        """
        filter_param = "StandardStatus eq 'Active' and PropertyType eq 'Residential'"
        endpoint = (f"{self.base_url}{self.dataset_id}/Property"
                   f"?access_token={self.access_token}"
                   f"&$filter={filter_param}"
                   f"&$top={limit}")

        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json().get('value', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching active listings: {e}")
            return []

    def get_listing(self, listing_key):
        """
        Fetch historical data for a specific listing
        """
        endpoint = (f"{self.base_url}{self.dataset_id}/Property('{listing_key}')"
                   f"?access_token={self.access_token}")
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching listing for {listing_key}: {e}")
            return []

def get_address_from_listing(listing):
    """
    Extract a complete address from a listing
    
    Args:
        listing (dict): Listing data
        
    Returns:
        str: Complete address
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

def main():
    client = RESOClient(dataset_id="actris_ref")
    
    # Get active listings
    print("Fetching active listings...")
    active_listings = client.get_active_residential_listings(limit=10)  # Limiting to 10 for demonstration
    print(f"Found {len(active_listings)} active listings")
    
    os.makedirs('/Users/deepset/real-estate/data/active_listings', exist_ok=True)
    os.makedirs('/Users/deepset/real-estate/data/listings', exist_ok=True)

    # Initialize geocoding client and database
    geocoder = GeocodingClient()
    db_conn = GeocodingDatabase()
    
    # Process each active listing
    for listing in active_listings:
        listing_key = listing.get('ListingKey')
        print(f"Processing listing: {listing_key}")

        with open(f'/Users/deepset/real-estate/data/active_listings/{listing_key}.json', 'w') as f:
            json.dump(listing, f, indent=4)
            
        # Get historical data for this listing
        full_listing = client.get_listing(listing_key)
        with open(f'/Users/deepset/real-estate/data/listings/{listing_key}.json', 'w') as f:
            json.dump(full_listing, f, indent=4)
        
        # Extract complete address from listing
        address = get_address_from_listing(listing)
        if not address:
            print(f"Could not extract address from listing: {listing_key}")
            continue
            
        print(f"Extracted address: {address}")
        
        # Check if address is already in database
        if db_conn.address_exists_in_db(address):
            print(f"Address already exists in database: {address}")
            continue
            
        # If not in database, geocode the address
        print(f"Geocoding address: {address}")
        result = geocoder.geocode_address(address)
        
        if result['success']:
            print(f"Success! Coordinates: {result['coordinates']['lat']}, {result['coordinates']['lon']}")
            
            # Save the geocoding result to database
            db_conn.save_geocoding_result_to_database(result)
        else:
            print(f"Error geocoding address: {result.get('error')}")
            # Still save the failed result to database
            db_conn.save_geocoding_result_to_database(result)
    
    # Close the database connection
    db_conn.close()

if __name__ == "__main__":
    main()