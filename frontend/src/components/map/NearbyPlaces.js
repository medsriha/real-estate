import React, { useState, useEffect } from 'react';
import config from '../../config';
import './map.css';

function NearbyPlaces({ coordinates, onViewOnMap, placeType = 'restaurant' }) {
  const [places, setPlaces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [nextPageToken, setNextPageToken] = useState(null);
  
  // Limit the number of places to display to fit panel height
  const MAX_PLACES = 5;
  
  // Define place type specific settings
  const placeTypeConfig = {
    restaurant: {
      endpoint: 'nearby',
      radius: 1000,
      label: 'Restaurants',
      loadingMessage: 'Loading nearby restaurants...',
      noResultsMessage: 'No restaurants found nearby'
    },
    school: {
      endpoint: 'schools',
      radius: 1500,
      label: 'Schools',
      loadingMessage: 'Loading nearby schools...',
      noResultsMessage: 'No schools found nearby'
    },
    hospital: {
      endpoint: 'hospitals',
      radius: 2000,
      label: 'Hospitals',
      loadingMessage: 'Loading nearby hospitals...',
      noResultsMessage: 'No hospitals found nearby'
    },
    grocery: {
      endpoint: 'grocery',
      radius: 1500,
      label: 'Grocery Stores',
      loadingMessage: 'Loading nearby grocery stores...',
      noResultsMessage: 'No grocery stores found nearby'
    },
    transportation: {
      endpoint: 'transportation',
      radius: 1000,
      label: 'Public Transit',
      loadingMessage: 'Loading nearby public transportation...',
      noResultsMessage: 'No public transportation found nearby'
    }
  };
  
  // Get the configuration for the current place type
  const currentConfig = placeTypeConfig[placeType] || placeTypeConfig.restaurant;

  // Helper function to get transit type icon based on place types and name
  const getTransitIcon = (place) => {
    if (!place || placeType !== 'transportation') return null;
    
    const types = place.types || [];
    const name = (place.name || '').toLowerCase();
    
    // Define icon mapping for different transit types
    const transitIcons = {
      subway: '🚇', // subway, metro
      train: '🚆', // train station
      bus: '🚌', // bus station, bus stop
      tram: '🚊', // tram, light rail
      ferry: '⛴️', // ferry terminal
      airport: '✈️', // airport
      taxi: '🚕', // taxi stand
      bike: '🚲', // bike sharing
      cable: '🚡', // cable car
      monorail: '🚝', // monorail
      parking: '🅿️', // parking
      car: '🚗', // car rental, car sharing
      default: '🚏' // default transit icon
    };

    // Common keywords for different transit types
    const transitKeywords = {
      subway: ['subway', 'metro', 'underground', 'tube', 'subte', 'u-bahn'],
      train: ['train', 'railway', 'rail', 'station', 'amtrak', 'railroad'],
      bus: ['bus', 'shuttle', 'coach', 'omnibus'],
      tram: ['tram', 'light rail', 'streetcar', 'trolley', 'transit', 'lrt'],
      ferry: ['ferry', 'boat', 'port', 'pier', 'dock', 'harbor', 'waterway', 'water taxi'],
      airport: ['airport', 'terminal', 'aerodrome', 'aviation', 'planes'],
      taxi: ['taxi', 'cab', 'ride', 'uber', 'lyft', 'hired'],
      bike: ['bike', 'bicycle', 'cycling', 'bikeshare', 'cycle'],
      cable: ['cable car', 'gondola', 'lift', 'aerial tramway', 'ski lift'],
      monorail: ['monorail'],
      parking: ['parking', 'park', 'garage'],
      car: ['car rental', 'car sharing', 'carshare', 'rental car', 'car']
    };
    
    // First check for specific place types
    if (types.includes('subway_station')) return transitIcons.subway;
    if (types.includes('train_station')) return transitIcons.train;
    if (types.includes('bus_station') || types.includes('bus_stop')) return transitIcons.bus;
    if (types.includes('tram_station')) return transitIcons.tram;
    if (types.includes('ferry_terminal')) return transitIcons.ferry;
    if (types.includes('airport')) return transitIcons.airport;
    if (types.includes('taxi_stand')) return transitIcons.taxi;
    if (types.includes('parking')) return transitIcons.parking;
    
    // Then check name against keywords
    for (const [transitType, keywords] of Object.entries(transitKeywords)) {
      if (keywords.some(keyword => name.includes(keyword))) {
        return transitIcons[transitType];
      }
    }
    
    // Default transit icon if no specific type is detected
    return transitIcons.default;
  };

  useEffect(() => {
    let isMounted = true;
    
    if (coordinates) {
      setLoading(true);
      setPlaces([]);
      setNextPageToken(null);
      
      fetchNearbyPlaces().then(result => {
        if (isMounted) {
          if (result.error) {
            setError(result.error);
          } else {
            setPlaces(result.places);
            setNextPageToken(result.nextPageToken);
          }
          setLoading(false);
        }
      });
    }
    
    return () => {
      isMounted = false;
    };
  }, [coordinates, placeType]);

  // Calculate distance between two coordinates in kilometers
  const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const R = 6371; // Radius of the earth in km
    const dLat = deg2rad(lat2 - lat1);
    const dLon = deg2rad(lon2 - lon1);
    const a = 
      Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) * 
      Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
    const distance = R * c; // Distance in km
    return distance;
  };
  
  // Convert degrees to radians
  const deg2rad = (deg) => {
    return deg * (Math.PI/180);
  };
  
  // Format distance to show in miles or km
  const formatDistance = (distance) => {
    // Convert km to miles and round to 1 decimal place
    const miles = (distance * 0.621371).toFixed(1);
    return `${miles} mi`;
  };

  const fetchNearbyPlaces = async (pageToken = null) => {
    try {
      // Build the URL for the backend request
      let url = `${config.BACKEND_URL}/api/places/${currentConfig.endpoint}?location=${coordinates.lat},${coordinates.lng}&radius=${currentConfig.radius}`;
      
      if (pageToken) {
        url += `&pagetoken=${pageToken}`;
      }
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to fetch nearby ${placeType}s`);
      }
      
      const data = await response.json();
      
      // Add distance calculation to each place
      const placesWithDistance = data.results.map(place => {
        let distance = 0;
        
        // Check if the place has geometry with location
        if (place.geometry && place.geometry.location) {
          const { lat, lng } = place.geometry.location;
          distance = calculateDistance(
            coordinates.lat, 
            coordinates.lng, 
            lat, 
            lng
          );
        }
        
        return {
          ...place,
          distance
        };
      });
      
      // Sort places by distance
      placesWithDistance.sort((a, b) => a.distance - b.distance);
      
      let resultPlaces;
      if (pageToken) {
        // Append results if using page token but respect the maximum limit
        const combinedResults = [...places, ...placesWithDistance];
        resultPlaces = combinedResults.slice(0, MAX_PLACES);
      } else {
        // Replace results for new search, respecting maximum limit
        resultPlaces = placesWithDistance.slice(0, MAX_PLACES);
      }
      
      // Only include next page token if we haven't reached the maximum
      let resultNextPageToken = null;
      if (data.next_page_token && resultPlaces.length < MAX_PLACES) {
        resultNextPageToken = data.next_page_token;
      }
      
      return {
        places: resultPlaces,
        nextPageToken: resultNextPageToken,
        error: null
      };
    } catch (err) {
      return {
        places: [],
        nextPageToken: null,
        error: err.message
      };
    }
  };

  const loadMoreResults = async () => {
    if (nextPageToken && !loading) {
      setLoading(true);
      const result = await fetchNearbyPlaces(nextPageToken);
      
      if (result.error) {
        setError(result.error);
      } else {
        setPlaces(result.places);
        setNextPageToken(result.nextPageToken);
      }
      setLoading(false);
    }
  };

  // Handle View on map click
  const handleViewOnMap = (place) => {
    if (!place) return;
    if (!onViewOnMap) return;
    
    // Check for the place location data
    if (!place.geometry || !place.geometry.location) return;
    
    // Extract location data
    const { lat, lng } = place.geometry.location;
    
    // Create location object for the map
    const locationData = {
      lat: typeof lat === 'function' ? lat() : lat, // Handle Google Maps LatLng objects
      lng: typeof lng === 'function' ? lng() : lng,
      name: place.name,
      place_id: place.place_id
    };
    
    // Call the parent component handler
    onViewOnMap(locationData);
  };

  return (
    <div className="place-content">
      {loading && places.length === 0 && (
        <div className="loading">{currentConfig.loadingMessage}</div>
      )}
      
      {error && (
        <div className="error">Error: {error}</div>
      )}
      
      {places.length > 0 ? (
        <div className="place-list">
          {places.map((place, index) => (
            <div key={`${place.place_id || 'place'}-${index}`} className="place-item">
              <div className="place-header">
                {placeType === 'transportation' ? (
                  <>
                    <div className="name-with-icon">
                      <span className="transit-icon">{getTransitIcon(place)}</span>
                      <h4>{place.name}</h4>
                    </div>
                  </>
                ) : (
                  <h4>{place.name}</h4>
                )}
                <span className="place-distance">{formatDistance(place.distance)}</span>
              </div>
              <div className="place-details">
                <div>
                  {/* Only show ratings for non-transit places */}
                  {placeType !== 'transportation' && (
                    place.rating ? (
                      <span className="rating">
                        {place.rating} ★ ({place.user_ratings_total || 0} reviews)
                      </span>
                    ) : (
                      <span className="no-rating">No reviews yet</span>
                    )
                  )}
                  <p>{place.vicinity}</p>
                </div>
              </div>
              <div className="place-actions">
                <button 
                  className="view-on-map-button"
                  onClick={() => handleViewOnMap(place)}
                >
                  View on map
                </button>
                {place.website && (
                  <a 
                    href={place.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="visit-website"
                  >
                    Website
                  </a>
                )}
              </div>
            </div>
          ))}
          
          {loading && places.length > 0 && (
            <div className="loading-more">Loading more...</div>
          )}
          
          {nextPageToken && !loading && places.length < MAX_PLACES && (
            <button 
              className="load-more-button"
              onClick={loadMoreResults}
            >
              Load More Results
            </button>
          )}
        </div>
      ) : !loading && (
        <div className="no-results">{currentConfig.noResultsMessage}</div>
      )}
    </div>
  );
}

export default NearbyPlaces;