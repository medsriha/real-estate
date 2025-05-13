import React from 'react';
import { formatPrice } from '../../utils/formatters';
import './listings.css';

const FinancialInfo = ({ listing }) => {
  if (!listing) return null;

  // Check if there's any financial data
  const hasFinancialData = 
    listing.ListPrice || 
    listing.ClosePrice || 
    listing.OriginalListPrice || 
    listing.TaxAnnualAmount || 
    listing.AssociationFee;

  if (!hasFinancialData) return null;

  // Calculate price per sq ft
  const pricePerSqFt = listing.ListPrice && listing.LivingArea
    ? Math.round(listing.ListPrice / listing.LivingArea)
    : null;

  return (
    <div className="financial-info-section">
      <h4>Financial Information</h4>
      
      <div className="financial-details">
        <div className="financial-grid">
          {listing.ListPrice && (
            <div className="financial-item">
              <span className="financial-label">List Price:</span>
              <span className="financial-value">{formatPrice(listing.ListPrice)}</span>
            </div>
          )}
          
          {listing.ClosePrice && (
            <div className="financial-item">
              <span className="financial-label">Close Price:</span>
              <span className="financial-value">{formatPrice(listing.ClosePrice)}</span>
            </div>
          )}
          
          {listing.OriginalListPrice && listing.OriginalListPrice !== listing.ListPrice && (
            <div className="financial-item">
              <span className="financial-label">Original List Price:</span>
              <span className="financial-value">{formatPrice(listing.OriginalListPrice)}</span>
            </div>
          )}
          
          {pricePerSqFt && (
            <div className="financial-item">
              <span className="financial-label">Price/Sq Ft:</span>
              <span className="financial-value">${pricePerSqFt}</span>
            </div>
          )}
          
          {listing.TaxAnnualAmount && (
            <div className="financial-item">
              <span className="financial-label">Annual Taxes:</span>
              <span className="financial-value">{formatPrice(listing.TaxAnnualAmount)}</span>
            </div>
          )}
          
          {listing.TaxYear && (
            <div className="financial-item">
              <span className="financial-label">Tax Year:</span>
              <span className="financial-value">{listing.TaxYear}</span>
            </div>
          )}
          
          {listing.AssociationFee && (
            <div className="financial-item">
              <span className="financial-label">HOA Fees:</span>
              <span className="financial-value">
                ${listing.AssociationFee}{listing.AssociationFeeFrequency ? ` ${listing.AssociationFeeFrequency}` : ''}
              </span>
            </div>
          )}
        </div>
        
        {/* Financing Information */}
        {(listing.FinancingProposed || listing.FinancingAvailable) && (
          <div className="financing-info">
            <h5>Financing Information</h5>
            {listing.FinancingProposed && (
              <div className="financing-item">
                <span className="financial-label">Financing Proposed:</span>
                <span className="financial-value">{listing.FinancingProposed}</span>
              </div>
            )}
            {listing.FinancingAvailable && Array.isArray(listing.FinancingAvailable) && (
              <div className="financing-item">
                <span className="financial-label">Financing Available:</span>
                <div className="financing-options">
                  {listing.FinancingAvailable.map((option, index) => (
                    <span key={index} className="financing-option">{option}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default FinancialInfo; 