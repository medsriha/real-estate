import React, { useMemo, useState, useEffect } from 'react';
import ImageGallery from './ImageGallery';
import PropertyDetails from './PropertyDetails';
import AmenitiesSection from './AmenitiesSection';
import FinancialInfo from './FinancialInfo';
import NearbyPlaces from '../map/NearbyPlaces';
import { formatPrice, formatAddress } from '../../utils/formatters';
import './listings.css';

function ListingPanel({ 
  listing, 
  selectedImageIndex, 
  onThumbnailClick, 
  onClose,
  isVisible = true,
  isExpanded = true,
  onToggleExpand,
  isPinned = false,
  panelId = null,
  onPin = null,
  onUnpin = null,
  panelIndex = 0,
  allPinnedPanels = [],
  onViewMapLocation = null
}) {
  const panelWidth = isExpanded ? 500 : 150;
  const [selectedTab, setSelectedTab] = useState('details');
  const [selectedPlaceType, setSelectedPlaceType] = useState('restaurant');
  
  // Add debugging log when place type changes
  useEffect(() => {
    console.log(`Selected place type changed to: ${selectedPlaceType}`);
  }, [selectedPlaceType]);
  
  const rightPosition = useMemo(() => {
    let position;
    
    if (isPinned) {
      let totalWidth = 0;
      allPinnedPanels.forEach((panel, idx) => {
        if (idx < panelIndex) {
          totalWidth += panel.isExpanded ? 500 : 150;
        }
      });
      position = `${totalWidth}px`;
    } else {
      let pinnedWidth = 0;
      allPinnedPanels.forEach(panel => {
        pinnedWidth += panel.isExpanded ? 500 : 150;
      });
      position = `${pinnedWidth}px`;
    }
    
    return position;
  }, [isPinned, panelIndex, allPinnedPanels, isExpanded]);

  const handleViewOnMap = (placeLocation) => {
    if (onViewMapLocation && placeLocation) {
      onViewMapLocation({
        ...placeLocation,
        listing
      });
    }
  };
  
  // Function to handle place type selection
  const handlePlaceTypeChange = (type) => {
    console.log(`Changing place type from ${selectedPlaceType} to ${type}`);
    setSelectedPlaceType(type);
  };

  if (!listing) return null;

  // Compact panel view for collapsed panel
  if (!isExpanded) {
    return (
      <div 
        className={`listing-panel compact ${isPinned ? 'pinned' : ''}`}
        style={{
          width: `${panelWidth}px`,
          right: rightPosition,
          transform: isVisible ? 'translateX(0)' : 'translateX(100%)',
          transition: 'transform 0.3s ease, width 0.3s ease, right 0.3s ease',
          borderRight: isPinned && panelIndex > 0 ? '1px solid #e0e0e0' : 'none'
        }}
      >
        <div className="panel-controls">
          <button 
            className="expand-toggle-button" 
            onClick={onToggleExpand}
            title="Expand panel"
          >
            ▶
          </button>
        </div>
        
        <div className="compact-info">
          <h3>{formatPrice(listing.ListPrice)}</h3>
          <p className="beds-baths">
            {listing.BedroomsTotal || 'N/A'} bed, {' '}
            {listing.BathroomsTotal || 'N/A'} bath
          </p>
          {listing.Media && listing.Media.length > 0 && (
            <img 
              src={listing.Media[0].MediaURL} 
              alt="Property"
              className="compact-image" 
            />
          )}
        </div>
      </div>
    );
  }

  // Available place types
  const placeTypes = [
    { id: 'restaurant', label: 'Restaurants' },
    { id: 'school', label: 'Schools' },
    { id: 'grocery', label: 'Grocery' },
    { id: 'hospital', label: 'Hospitals' },
    { id: 'transportation', label: 'Transit' }
  ];

  // Available tabs
  const tabs = [
    { id: 'details', label: 'Details' },
    { id: 'amenities', label: 'Amenities' },
    { id: 'financial', label: 'Financial' },
    { id: 'nearby', label: 'Nearby Places' }
  ];

  return (
    <div 
      className={`listing-panel ${isPinned ? 'pinned' : ''}`}
      style={{
        width: `${panelWidth}px`,
        right: rightPosition,
        transform: isVisible ? 'translateX(0)' : 'translateX(100%)',
        transition: 'transform 0.3s ease, width 0.3s ease, right 0.3s ease',
        borderRight: isPinned && panelIndex > 0 ? '1px solid #e0e0e0' : 'none'
      }}
    >
      <div className="panel-controls sticky-header">
        <button 
          className="expand-toggle-button" 
          onClick={onToggleExpand}
          title="Collapse panel"
        >
          ◀
        </button>
        
        {!isPinned && onPin && (
          <button 
            className="pin-panel-button" 
            onClick={onPin}
            title="Pin panel"
          >
            📌
          </button>
        )}
        
        {isPinned && onUnpin && (
          <button 
            className="unpin-panel-button" 
            onClick={onUnpin}
            title="Unpin panel"
          >
            📍
          </button>
        )}
        
        <button 
          className="close-button" 
          onClick={onClose}
          title="Close panel"
        >
          ×
        </button>
      </div>
      
      <div className="panel-content">
        <ImageGallery 
          media={listing.Media} 
          selectedImageIndex={selectedImageIndex}
          onThumbnailClick={(index) => onThumbnailClick(index, panelId)}
        />
        
        <div className="listing-basic-info">
          <h3>{formatPrice(listing.ListPrice)}</h3>
          <p>{formatAddress(listing)}</p>
          <p className="beds-baths">
            {listing.BedroomsTotal || 'N/A'} bed, {' '}
            {listing.BathroomsTotal || 'N/A'} bath, {' '}
            {listing.LivingArea ? `${listing.LivingArea} sqft` : 'N/A'}
          </p>
        </div>
        
        {/* Tab Navigation */}
        <div className="panel-tabs">
          {tabs.map(tab => (
            <button 
              key={tab.id}
              className={`panel-tab ${selectedTab === tab.id ? 'active' : ''}`}
              onClick={() => setSelectedTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>
        
        {/* Tab Content */}
        <div className="tab-content">
          {selectedTab === 'details' && <PropertyDetails listing={listing} />}
          
          {selectedTab === 'amenities' && <AmenitiesSection listing={listing} />}
          
          {selectedTab === 'financial' && <FinancialInfo listing={listing} />}
          
          {selectedTab === 'nearby' && (
            <div className="nearby-places-section">
              <div className="place-type-tabs">
                {placeTypes.map(type => (
                  <button 
                    key={type.id}
                    className={`tab-button ${selectedPlaceType === type.id ? 'active' : ''}`}
                    onClick={() => handlePlaceTypeChange(type.id)}
                  >
                    {type.label}
                  </button>
                ))}
              </div>
              
              <div className="nearby-places-container">
                <NearbyPlaces 
                  key={`nearby-${selectedPlaceType}`}
                  coordinates={listing.coordinates}
                  onViewOnMap={handleViewOnMap} 
                  placeType={selectedPlaceType}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ListingPanel; 