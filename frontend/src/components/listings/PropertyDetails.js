import React from 'react';
import { formatPrice, formatAddress } from '../../utils/formatters';
import './listings.css';

const PropertyDetails = ({ listing }) => {
  if (!listing) return null;

  // Helper function to render a detail row if the data exists
  const renderDetailItem = (label, value, formatter = null) => {
    if (!value && value !== 0) return null;
    
    const displayValue = formatter ? formatter(value) : value;
    
    return (
      <div className="property-detail-item">
        <span className="detail-label">{label}:</span>
        <span className="detail-value">{displayValue}</span>
      </div>
    );
  };

  // Format listing date
  const formatDate = (dateString) => {
    if (!dateString) return null;
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    }).format(date);
  };

  return (
    <div className="property-details">
      <div className="property-header">
        <h3 className="property-price">{formatPrice(listing.ListPrice)}</h3>
        <p className="property-address">{formatAddress(listing)}</p>
        
        <div className="property-primary-details">
          {renderDetailItem('Beds', listing.BedroomsTotal)}
          {renderDetailItem('Baths', listing.BathroomsTotal)}
          {renderDetailItem('Sq Ft', listing.LivingArea)}
          {renderDetailItem('Year Built', listing.YearBuilt)}
        </div>
      </div>

      <div className="property-status">
        <div className="status-tag">{listing.StandardStatus || 'Active'}</div>
        {listing.CloseDate && <div className="status-tag sold">Sold on {formatDate(listing.CloseDate)}</div>}
        {renderDetailItem('Listed', formatDate(listing.ListDate))}
        {listing.DaysOnMarket && renderDetailItem('Days on Market', listing.DaysOnMarket)}
      </div>

      <div className="property-description">
        <h4>Description</h4>
        <p>{listing.PublicRemarks || 'No description available'}</p>
      </div>

      <div className="property-section">
        <h4>Property Details</h4>
        <div className="details-grid">
          {renderDetailItem('Property Type', listing.PropertyType)}
          {renderDetailItem('Lot Size', listing.LotSizeArea && `${listing.LotSizeArea} ${listing.LotSizeUnits || 'sq ft'}`)}
          {renderDetailItem('Heating', listing.Heating)}
          {renderDetailItem('Cooling', listing.Cooling)}
          {renderDetailItem('Parking', listing.ParkingTotal && `${listing.ParkingTotal} spaces`)}
          {renderDetailItem('Garage', listing.GarageSpaces && `${listing.GarageSpaces} cars`)}
          {renderDetailItem('Stories', listing.Stories)}
          {renderDetailItem('Fireplaces', listing.FireplacesTotal)}
          {renderDetailItem('Pool', listing.PoolPrivateYN === 'Y' ? 'Yes' : listing.PoolPrivateYN === 'N' ? 'No' : null)}
        </div>
      </div>

      {listing.Appliances && listing.Appliances.length > 0 && (
        <div className="property-section">
          <h4>Appliances</h4>
          <div className="property-appliances">
            {listing.Appliances.map((appliance, index) => (
              <div key={index} className="appliance-tag">{appliance}</div>
            ))}
          </div>
        </div>
      )}

      {listing.InteriorFeatures && listing.InteriorFeatures.length > 0 && (
        <div className="property-section">
          <h4>Interior Features</h4>
          <div className="features-list">
            {listing.InteriorFeatures.map((feature, index) => (
              <div key={index} className="feature-tag">{feature}</div>
            ))}
          </div>
        </div>
      )}

      {listing.ExteriorFeatures && listing.ExteriorFeatures.length > 0 && (
        <div className="property-section">
          <h4>Exterior Features</h4>
          <div className="features-list">
            {listing.ExteriorFeatures.map((feature, index) => (
              <div key={index} className="feature-tag">{feature}</div>
            ))}
          </div>
        </div>
      )}

      <div className="listing-info-footer">
        {listing.ListingId && (
          <p className="listing-id">MLS#: {listing.ListingId}</p>
        )}
        {listing.ListingKey && (
          <p className="listing-id">Listing Key: {listing.ListingKey}</p>
        )}
      </div>
    </div>
  );
};

export default PropertyDetails; 