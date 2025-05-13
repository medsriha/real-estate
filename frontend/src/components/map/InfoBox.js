import React, { useState, useEffect } from 'react';
import { formatPrice, formatAddress } from '../../utils/formatters';
import './map.css';

/**
 * InfoBox component displayed when a marker is clicked
 */
function InfoBox({ listing, onExpand }) {
  // Note: We rely on the closest() check in useListings instead of stopPropagation
  // This allows the document click handler to work properly
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [scrollPosition, setScrollPosition] = useState(0);
  const [totalImages, setTotalImages] = useState(0);

  // Reset selected image when listing changes
  useEffect(() => {
    setSelectedImageIndex(0);
    setTotalImages(listing.Media?.length || 0);
  }, [listing]);

  // Navigate to next/previous image
  const navigateImage = (direction) => {
    if (!listing.Media || listing.Media.length <= 1) return;
    
    if (direction === 'next') {
      setSelectedImageIndex((prev) => (prev + 1) % listing.Media.length);
      setScrollPosition((prev) => (prev + 1) / listing.Media.length);
    } else {
      setSelectedImageIndex((prev) => (prev - 1 + listing.Media.length) % listing.Media.length);
      setScrollPosition((prev) => (prev - 1 + listing.Media.length) / listing.Media.length);
    }
  };

  // Calculate the scroll indicator dimensions
  const calculateScrollIndicator = () => {
    // Only show indicator if there are multiple images
    if (!listing.Media || listing.Media.length <= 1) {
      return { display: 'none' };
    }
    
    // Calculate the visible portion width as a percentage of total
    const indicatorWidth = Math.max(100 / listing.Media.length, 10); // At least 10% wide
    
    // Calculate the scroll position as a percentage
    const indicatorLeft = (selectedImageIndex / (listing.Media.length - 1)) * (100 - indicatorWidth);
    
    return {
      width: `${indicatorWidth}%`,
      left: `${indicatorLeft}%`
    };
  };

  // Get scroll indicator position and size
  const scrollIndicatorStyle = calculateScrollIndicator();

  // Handle click on the InfoBox
  const handleInfoBoxClick = (e) => {
    // Only stop propagation to prevent default map behavior
    e.stopPropagation();
    
    // Check if click was on a navigation arrow or scroll indicator - don't expand if it was
    if (
      e.target.closest('.info-box-arrow') ||
      e.target.closest('.info-box-scroll-indicator-track') ||
      e.target.closest('.info-box-scroll-indicator-thumb')
    ) {
      return;
    }
    
    // Otherwise, expand the listing
    onExpand(listing);
  };

  return (
    <div 
      className="info-box clickable"
      onClick={handleInfoBoxClick}
    >
      {/* Image Gallery with Navigation */}
      {listing.Media && listing.Media.length > 0 && (
        <div className="info-box-image-container">
          <img 
            src={listing.Media[selectedImageIndex].MediaURL} 
            alt="Property" 
            className="info-box-image"
          />
          
          {/* Image Navigation Arrows */}
          {listing.Media.length > 1 && (
            <>
              <div className="info-box-arrow left" onClick={(e) => {
                e.stopPropagation();
                navigateImage('prev');
              }}>
                <svg 
                  width="24" 
                  height="24" 
                  viewBox="0 0 24 24" 
                  fill="none" 
                  stroke="#ffffff"
                  strokeWidth="3" 
                  strokeLinecap="round" 
                  strokeLinejoin="round"
                >
                  <polyline points="15 18 9 12 15 6"></polyline>
                </svg>
              </div>
              
              <div className="info-box-arrow right" onClick={(e) => {
                e.stopPropagation();
                navigateImage('next');
              }}>
                <svg 
                  width="24" 
                  height="24" 
                  viewBox="0 0 24 24" 
                  fill="none" 
                  stroke="#ffffff"
                  strokeWidth="3" 
                  strokeLinecap="round" 
                  strokeLinejoin="round"
                >
                  <polyline points="9 18 15 12 9 6"></polyline>
                </svg>
              </div>
              
              {/* Image Counter */}
              <div className="info-box-image-counter">
                {selectedImageIndex + 1}/{listing.Media.length}
              </div>
              
              {/* Scroll Indicator */}
              <div className="info-box-scroll-indicator-track" onClick={(e) => e.stopPropagation()}>
                <div 
                  className="info-box-scroll-indicator-thumb" 
                  style={scrollIndicatorStyle}
                  onClick={(e) => e.stopPropagation()}
                />
              </div>
            </>
          )}
        </div>
      )}
      
      <div className="info-box-content">
        <div className="info-price-line">
          <span className="info-price">{formatPrice(listing.ListPrice)}</span>
          <div className="info-box-badge">
            {listing.PropertyType || "Residential"}
          </div>
        </div>
        
        <div className="info-address">
          {formatAddress(listing)}
        </div>
        
        <div className="info-features">
          <div className="info-feature">
            <span className="info-feature-icon">🛏️</span>
            <span className="info-feature-value">{listing.BedroomsTotal || 'N/A'}</span>
            <span className="info-feature-label">Beds</span>
          </div>
          
          <div className="info-feature">
            <span className="info-feature-icon">🚿</span>
            <span className="info-feature-value">{listing.BathroomsTotal || 'N/A'}</span>
            <span className="info-feature-label">Baths</span>
          </div>
          
          <div className="info-feature">
            <span className="info-feature-icon">📏</span>
            <span className="info-feature-value">{listing.LivingArea || 'N/A'}</span>
            <span className="info-feature-label">Sqft</span>
          </div>
        </div>
        
        {listing.PublicRemarks && (
          <div className="info-description">
            {listing.PublicRemarks.length > 100 
              ? `${listing.PublicRemarks.substring(0, 100)}...` 
              : listing.PublicRemarks}
          </div>
        )}
        
        <div className="info-hint">Click for details</div>
      </div>
    </div>
  );
}

export default InfoBox; 