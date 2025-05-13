import React, { useRef, useEffect, useState } from 'react';
import { APIProvider, Map, AdvancedMarker, Pin } from '@vis.gl/react-google-maps';
import ListingMarker from './ListingMarker';
import InfoBox from './InfoBox';
import config from '../../config';

function MapComponent({ 
  activeListings, 
  infoBoxListing, 
  onMarkerClick, 
  onInfoClick,
  selectedRestaurant = null, // Prop for selected restaurant location
  highlightedListing = null,  // Prop for the listing to highlight when viewing restaurant
  zoomToListingRef = null // New prop: ref or callback to expose zoom function
}) {
  const mapRef = useRef(null);
  const [mapInstance, setMapInstance] = useState(null);
  
  // Pan to fit both restaurant and listing
  useEffect(() => {
    if (!mapInstance) return;
    
    if (selectedRestaurant && highlightedListing) {
      try {
        const adjustMapView = () => {
          // Create bounds that include both points
          const bounds = new window.google.maps.LatLngBounds();
          
          // Add the restaurant location to the bounds
          bounds.extend({
            lat: selectedRestaurant.lat,
            lng: selectedRestaurant.lng
          });
          
          // Add the listing location to the bounds
          bounds.extend({
            lat: highlightedListing.coordinates.lat,
            lng: highlightedListing.coordinates.lng
          });
          
          // Fit the map to these bounds with some padding
          mapInstance.fitBounds(bounds, {
            top: 100,
            right: 100,
            bottom: 100,
            left: 100
          });
        };
        
        // Use setTimeout to ensure this runs after the current render cycle
        const timer = setTimeout(adjustMapView, 100);
        return () => clearTimeout(timer);
      } catch (error) {
        console.error('Error adjusting map view:', error);
      }
    } else if (selectedRestaurant) {
      // If no listing is visible, just focus on the restaurant
      try {
        const focusOnRestaurant = () => {
          // Pan to the restaurant location
          mapInstance.panTo({
            lat: selectedRestaurant.lat,
            lng: selectedRestaurant.lng
          });
          
          // Set zoom level to focus on restaurant
          mapInstance.setZoom(18);
        };
        
        const timer = setTimeout(focusOnRestaurant, 100);
        return () => clearTimeout(timer);
      } catch (error) {
        console.error('Error panning to restaurant:', error);
      }
    }
  }, [selectedRestaurant, mapInstance, highlightedListing]);
  
  // Disable map zoom when cursor is over info box
  useEffect(() => {
    const preventMapZoom = (e) => {
      e.stopPropagation();
      // We still want to allow scrolling content within the infobox
      if (!e.target.closest('.scrollable-content')) {
        e.preventDefault();
      }
    };
    
    // Add event listeners to all info boxes
    const containers = document.querySelectorAll('.info-box-container');
    containers.forEach(container => {
      container.addEventListener('wheel', preventMapZoom, { passive: false, capture: true });
      container.addEventListener('mousewheel', preventMapZoom, { passive: false, capture: true });
      container.addEventListener('DOMMouseScroll', preventMapZoom, { passive: false, capture: true });
      container.addEventListener('dblclick', preventMapZoom, { passive: false, capture: true });
      
      // Additional protection against gestures
      container.addEventListener('gesturestart', preventMapZoom, { passive: false, capture: true });
      container.addEventListener('gesturechange', preventMapZoom, { passive: false, capture: true });
      container.addEventListener('gestureend', preventMapZoom, { passive: false, capture: true });
    });
    
    return () => {
      // Get a fresh list of containers to ensure we're cleaning up all current ones
      const containersToCleanup = document.querySelectorAll('.info-box-container');
      containersToCleanup.forEach(container => {
        container.removeEventListener('wheel', preventMapZoom, { capture: true });
        container.removeEventListener('mousewheel', preventMapZoom, { capture: true });
        container.removeEventListener('DOMMouseScroll', preventMapZoom, { capture: true });
        container.removeEventListener('dblclick', preventMapZoom, { capture: true });
        
        container.removeEventListener('gesturestart', preventMapZoom, { capture: true });
        container.removeEventListener('gesturechange', preventMapZoom, { capture: true });
        container.removeEventListener('gestureend', preventMapZoom, { capture: true });
      });
    };
  }, [infoBoxListing]);
  
  // Handle map instance when it loads
  const handleMapLoad = (map) => {
    mapRef.current = map;
    setMapInstance(map);
  };
  
  // Expose zoomToListing function to parent
  useEffect(() => {
    if (zoomToListingRef) {
      zoomToListingRef.current = (listing) => {
        if (mapInstance && listing && listing.coordinates) {
          mapInstance.panTo({
            lat: listing.coordinates.lat,
            lng: listing.coordinates.lng
          });
          mapInstance.setZoom(18);
        }
      };
    }
  }, [mapInstance, zoomToListingRef]);
  
  return (
    <APIProvider apiKey={config.GOOGLE_MAPS_API_KEY}>
      <Map 
        defaultCenter={{ lat: config.DEFAULT_LAT, lng: config.DEFAULT_LNG }} 
        defaultZoom={config.DEFAULT_ZOOM}
        mapId={config.GOOGLE_MAPS_MAP_ID}
        fullscreenControl={true}
        style={{ width: '100%', height: '100%' }}
        gestureHandling={'greedy'}
        options={{
          scrollwheel: true, // Enabled by default but will be disabled on InfoBox
          disableDoubleClickZoom: true, // Let our code handle this
          clickableIcons: true // Enable Google POI clicks
        }}
        onLoad={handleMapLoad}
      >
        {/* Render listing markers when active */}
        {activeListings.map(listing => (
          <ListingMarker
            key={listing.ListingKey}
            listing={listing}
            onClick={onMarkerClick}
            onInfoClick={onInfoClick}
            isHighlighted={highlightedListing && highlightedListing.ListingKey === listing.ListingKey}
          />
        ))}
        
        {/* Render restaurant marker with Google Maps-like style */}
        {selectedRestaurant && (
          <AdvancedMarker
            position={{ lat: selectedRestaurant.lat, lng: selectedRestaurant.lng }}
            zIndex={2000} // Higher than other markers
            title={selectedRestaurant.name}
          >
            <Pin
              background="#E31C5F" // Google Maps style restaurant color
              glyphColor="#FFFFFF"
              borderColor="#FFFFFF"
              scale={1.0}
            />
          </AdvancedMarker>
        )}
        
        {/* Render info box for selected marker */}
        {infoBoxListing && (
          <AdvancedMarker
            position={infoBoxListing.coordinates}
            zIndex={1000}
          >
            <div 
              className="info-box-container"
              style={{ 
                position: 'absolute',
                bottom: '30px', 
                left: '50%',
                transform: 'translateX(-50%)',
                width: '320px'
              }}
            >
              <InfoBox 
                listing={infoBoxListing}
                onExpand={onMarkerClick}
              />
            </div>
          </AdvancedMarker>
        )}
      </Map>
    </APIProvider>
  );
}

export default MapComponent; 