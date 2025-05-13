import React from 'react';
import './listings.css';

const AmenitiesSection = ({ listing }) => {
  if (!listing) return null;

  // Helper to check if a section has any data
  const hasData = (listFields) => {
    return listFields.some(field => 
      listing[field] && 
      (Array.isArray(listing[field]) ? listing[field].length > 0 : true)
    );
  };

  // Community Features
  const communityFields = ['CommunityFeatures', 'SecurityFeatures', 'AssociationAmenities'];
  const hasCommunityFeatures = hasData(communityFields);

  // Utility Features
  const utilityFields = ['Utilities', 'WaterSource', 'SewerSystems', 'Heating', 'Cooling'];
  const hasUtilityFeatures = hasData(utilityFields);

  // Outdoor features
  const outdoorFields = ['LotFeatures', 'View', 'WaterfrontYN', 'WaterfrontFeatures'];
  const hasOutdoorFeatures = hasData(outdoorFields);

  // Render feature list with name
  const renderFeatureList = (title, fieldName) => {
    if (!listing[fieldName] || !listing[fieldName].length) return null;
    
    return (
      <div className="amenity-group">
        <h5>{title}</h5>
        <div className="amenity-tags">
          {Array.isArray(listing[fieldName]) ? 
            listing[fieldName].map((item, index) => (
              <span key={index} className="amenity-tag">{item}</span>
            )) : 
            <span className="amenity-tag">{listing[fieldName]}</span>
          }
        </div>
      </div>
    );
  };

  // If no amenities data is available
  if (!hasCommunityFeatures && !hasUtilityFeatures && !hasOutdoorFeatures) {
    return null;
  }

  return (
    <div className="amenities-section">
      <h4>Amenities and Features</h4>

      {hasCommunityFeatures && (
        <div className="amenity-category">
          <h5 className="category-title">Community</h5>
          {renderFeatureList('Community Features', 'CommunityFeatures')}
          {renderFeatureList('Security', 'SecurityFeatures')}
          {renderFeatureList('Association Amenities', 'AssociationAmenities')}
          
          {/* HOA Information if available */}
          {listing.AssociationFee && (
            <div className="amenity-group">
              <h5>Association</h5>
              <div className="property-detail-item">
                <span className="detail-label">HOA Fee:</span>
                <span className="detail-value">
                  ${listing.AssociationFee}{listing.AssociationFeeFrequency ? ` ${listing.AssociationFeeFrequency}` : ''}
                </span>
              </div>
            </div>
          )}
        </div>
      )}

      {hasUtilityFeatures && (
        <div className="amenity-category">
          <h5 className="category-title">Utilities</h5>
          {renderFeatureList('Utilities', 'Utilities')}
          {renderFeatureList('Water Source', 'WaterSource')}
          {renderFeatureList('Sewer', 'SewerSystems')}
          {listing.Heating && !Array.isArray(listing.Heating) && (
            <div className="amenity-group">
              <h5>Heating</h5>
              <span className="amenity-tag">{listing.Heating}</span>
            </div>
          )}
          {listing.Cooling && !Array.isArray(listing.Cooling) && (
            <div className="amenity-group">
              <h5>Cooling</h5>
              <span className="amenity-tag">{listing.Cooling}</span>
            </div>
          )}
        </div>
      )}

      {hasOutdoorFeatures && (
        <div className="amenity-category">
          <h5 className="category-title">Outdoor</h5>
          {renderFeatureList('Lot Features', 'LotFeatures')}
          {renderFeatureList('View', 'View')}
          {listing.WaterfrontYN === 'Y' && (
            <div className="amenity-group">
              <h5>Waterfront</h5>
              <span className="amenity-tag">Yes</span>
              {listing.WaterfrontFeatures && (
                <div className="amenity-tags">
                  {Array.isArray(listing.WaterfrontFeatures) ?
                    listing.WaterfrontFeatures.map((feature, index) => (
                      <span key={index} className="amenity-tag">{feature}</span>
                    )) :
                    <span className="amenity-tag">{listing.WaterfrontFeatures}</span>
                  }
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AmenitiesSection; 