import React from 'react';
import './common.css';

function ActionButton({ onClick, isLoading, showingListings }) {
  return (
    <button 
      onClick={onClick}
      className="action-button"
    >
      {isLoading ? 'Loading...' : (showingListings ? 'Hide Active Listings' : 'Show Active Listings')}
    </button>
  );
}

export default ActionButton; 