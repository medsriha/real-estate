/**
 * Utility functions for formatting values
 */

/**
 * Format price for marker display (compact, e.g. $1.2M or $500K)
 */
export const formatMarkerPrice = (price) => {
  if (!price) return 'N/A';
  if (price >= 1000000) {
    return `$${(price / 1000000).toFixed(1)}M`;
  }
  return `$${(price / 1000).toFixed(0)}K`;
};

/**
 * Format price for display with full currency formatting
 */
export const formatPrice = (price) => {
  if (!price) return 'N/A';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0
  }).format(price);
};

/**
 * Format address from listing data
 */
export const formatAddress = (listing) => {
  if (!listing) return '';
  
  const street = `${listing.StreetNumber || ''} ${listing.StreetName || ''}`.trim();
  const city = listing.City || '';
  const state = listing.StateOrProvince || '';
  const zip = listing.PostalCode || '';
  
  return `${street}, ${city}, ${state} ${zip}`;
}; 