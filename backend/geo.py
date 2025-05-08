import requests
import urllib.parse
import os
from dotenv import load_dotenv
import json
import pandas as pd
import sqlite3

load_dotenv()

class GeocodingClient:
    def __init__(self, base_url="https://api.geoapify.com/v1/geocode/search", api_key=os.getenv('GEOAPIFY_API_KEY')):
        """
        Initialize the geocoding client
        
        Args:
            api_key (str, optional): Geoapify API key. If not provided, it will try to get from environment variables
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Accept": "application/json"
        }
    
    def geocode_address(self, address):
        """
        Geocode an address to get latitude, longitude and other location data
        
        Args:
            address (str): The address to geocode
            
        Returns:
            dict: The geocoding result with location data
        """
        # URL encode the address
        encoded_address = urllib.parse.quote(address)
        
        # Construct the API URL
        url = f"{self.base_url}?text={encoded_address}&apiKey={self.api_key}"
        
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
                    'plus_code': props.get('plus_code'),
                    'place_id': props.get('place_id'),
                    'raw_response': data
                }
                
                return result
            else:
                return {
                    'success': False,
                    'address': address,
                    'error': 'No results found',
                    'raw_response': data
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'address': address,
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None)
            }

class GeocodingDatabase:
    def __init__(self, db_path='data/geocoding.db'):
        self.db_path = db_path
        self.conn = self.init_database()

    def init_database(self):
        """
        Initialize the SQLite database for storing geocoding results
    
        Args:
            db_path (str): Path to the SQLite database file
        
        Returns:
            sqlite3.Connection: Database connection
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Connect to the database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
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
        
        conn.commit()
        return conn

    def address_exists_in_db(self, address):
        """
        Check if an address already exists in the geocoding database
        
        Args:
            address (str): Address to check
            
        Returns:
            bool: True if address exists, False otherwise
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM geocoding_results WHERE address = ?", (address,))
        return cursor.fetchone() is not None

    def save_geocoding_result_to_database(self, result):
        """
        Save geocoding result to SQLite database
        
        Args:
            result (dict): Geocoding result to save
        """
        cursor = self.conn.cursor()
        
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
                result['formatted_address'],
                result['address_components']['house_number'],
                result['address_components']['street'],
                result['address_components']['city'],
                result['address_components']['county'],
                result['address_components']['state'],
                result['address_components']['country'],
                result['address_components']['postcode'],
                result['address_components']['suburb'],
                result['place_id'],
                json.dumps(result['raw_response'])
            ))
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
        
        self.conn.commit()
        print(f"Saved geocoding result for '{result['address']}' to database")
        
    def close(self):
        """
        Close the database connection
        """
        if self.conn:
            self.conn.close()