import React, { useState, useEffect } from 'react';
import { APIProvider, Map, AdvancedMarker, InfoWindow } from '@vis.gl/react-google-maps';
import './App.css';

// Listing Marker component
function ListingMarker({ listing, onClick }) {
  return (
    <AdvancedMarker
      position={listing.coordinates}
      onClick={() => onClick(listing)}
      title={`$${listing.ListPrice ? listing.ListPrice.toLocaleString() : 'N/A'}`}
    >
      <div className="marker-price">
        ${listing.ListPrice ? (listing.ListPrice/1000).toFixed(0) : 0}K
      </div>
    </AdvancedMarker>
  );
}

function App() {
  // The location (default to Austin, TX)
  const position = { lat: 30.2672, lng: -97.7431 };
  const [showActiveListings, setShowActiveListings] = useState(false);
  const [activeListings, setActiveListings] = useState([]);
  const [selectedListing, setSelectedListing] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  

  // Function to fetch active listings from the Flask API
  const fetchActiveListings = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Call our Flask API endpoint
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/listings/active?limit=100`);
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (err) {
      console.error("Error fetching listings:", err);
      setError("Failed to fetch listings. Please try again.");
      return [];
    } finally {
      setIsLoading(false);
    }
  };
  
  // Load listings when the button is clicked
  useEffect(() => {
    if (showActiveListings) {
      fetchActiveListings().then(listings => {
        setActiveListings(listings);
      });
    } else {
      setActiveListings([]);
      setSelectedListing(null);
    }
  }, [showActiveListings]);
  
  // Handle marker click
  const handleMarkerClick = (listing) => {
    setSelectedListing(listing);
  };
  
  // Format address from listing
  const formatAddress = (listing) => {
    const street = `${listing.StreetNumber || ''} ${listing.StreetName || ''}`.trim();
    const city = listing.City || '';
    const state = listing.StateOrProvince || '';
    const zip = listing.PostalCode || '';
    
    return `${street}, ${city}, ${state} ${zip}`;
  };
  
  return (
    <div className="AdvancedExample" style={{ height: '100vh', width: '100vw', position: 'absolute', top: 0, left: 0, margin: 0, padding: 0 }}>
      <div style={{ height: '100%', width: '100%' }}>
        <APIProvider apiKey={process.env.REACT_APP_GOOGLE_MAPS_API_KEY}>
        <Map 
            defaultCenter={{ lat: 30.2672, lng: -97.7431 }} 
            defaultZoom={12}
            mapId={process.env.REACT_APP_GOOGLE_MAPS_MAP_ID}
            fullscreenControl={true}
            style={{ width: '100%', height: '100%' }}
            gestureHandling={'greedy'}
          >
            {/* Render listing markers when active */}
            {activeListings.map(listing => (
              <ListingMarker
                key={listing.ListingKey}
                listing={listing}
                onClick={handleMarkerClick}
              />
            ))}
            
            {/* Show info window for selected listing */}
            {selectedListing && (
              <InfoWindow
                position={selectedListing.coordinates}
                onCloseClick={() => setSelectedListing(null)}
              >
                <div className="listing-info">
                  <h3>${selectedListing.ListPrice ? selectedListing.ListPrice.toLocaleString() : 'N/A'}</h3>
                  <p>{formatAddress(selectedListing)}</p>
                  <p>
                    {selectedListing.BedroomsTotal || 'N/A'} bed, 
                    {selectedListing.BathroomsTotal || 'N/A'} bath, 
                    {selectedListing.LivingArea ? `${selectedListing.LivingArea} sqft` : 'N/A'}
                  </p>
                  {selectedListing.ListingId && (
                    <p className="listing-id">MLS#: {selectedListing.ListingId}</p>
                  )}
                </div>
              </InfoWindow>
            )}
          </Map>
        </APIProvider>
        <button 
          onClick={() => setShowActiveListings(!showActiveListings)}
          style={{
            position: 'absolute',
            bottom: '20px',
            right: '20px',
            padding: '10px 15px',
            backgroundColor: '#4285F4',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
            fontWeight: 'bold',
            zIndex: 10
          }}
        >
          {isLoading ? 'Loading...' : (showActiveListings ? 'Hide Active Listings' : 'Show Active Listings')}
        </button>
        
        {/* Error message */}
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        
        {/* Loading indicator */}
        {isLoading && (
          <div className="loading-indicator">
            <div className="spinner"></div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App; 