import React from 'react';
import { AdvancedMarker } from '@vis.gl/react-google-maps';
import { formatMarkerPrice } from '../../utils/formatters';
import './map.css';

/**
 * Marker component for property listings on the map
 */
function ListingMarker({ 
  listing, 
  onClick, 
  onInfoClick,
  isHighlighted = false // New prop to indicate if this listing should be highlighted
}) {
  // Determine the marker class based on highlight state
  const markerClass = isHighlighted ? "marker-price highlighted" : "marker-price";
  
  return (
    <AdvancedMarker
      position={listing.coordinates}
      onClick={() => onInfoClick(listing)}
      title={`$${listing.ListPrice ? listing.ListPrice.toLocaleString() : 'N/A'}`}
    >
      <div className={markerClass}>
        {formatMarkerPrice(listing.ListPrice)}
      </div>
    </AdvancedMarker>
  );
}

export default ListingMarker; 