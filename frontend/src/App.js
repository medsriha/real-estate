import React, { useRef } from 'react';
import './App.css';
import {
  MapComponent,
  ListingPanel,
  ActionButton,
  LoadingIndicator,
  ErrorMessage
} from './components';
import useListings from './hooks/useListings';

function App() {
  const {
    showActiveListings,
    activeListings,
    selectedListing,
    infoBoxListing,
    selectedImageIndex,
    isLoading,
    error,
    isPanelVisible,
    isPanelExpanded,
    pinnedPanels,
    showMaxPanelsWarning,
    MAX_PANELS,
    selectedRestaurant,
    highlightedListing,
    toggleActiveListings,
    handleInfoClick,
    handleMarkerClick,
    handleThumbnailClick,
    handleClosePanel,
    handleClosePinnedPanel,
    togglePanelVisibility,
    togglePanelExpanded,
    togglePinnedPanelExpanded,
    pinCurrentPanel,
    unpinPanel,
    handleViewRestaurantOnMap
  } = useListings();
  
  const zoomToListingRef = useRef(null);
  
  // Calculate total panels for width calculations
  const totalPanels = (selectedListing ? 1 : 0) + pinnedPanels.length;
  
  // Update handleMarkerClick to handle the zoom reference properly
  const handleMarkerClickWithZoom = (listing) => {
    if (zoomToListingRef.current) {
      handleMarkerClick(listing, zoomToListingRef.current);
    } else {
      // Fallback if the ref is not yet assigned
      handleMarkerClick(listing);
    }
  };
  
  return (
    <div className="AdvancedExample" style={{ height: '100vh', width: '100vw', position: 'absolute', top: 0, left: 0, margin: 0, padding: 0 }}>
      <div style={{ height: '100%', width: '100%', position: 'relative' }}>
        <MapComponent 
          activeListings={activeListings}
          infoBoxListing={infoBoxListing}
          onMarkerClick={handleMarkerClickWithZoom}
          onInfoClick={handleInfoClick}
          selectedRestaurant={selectedRestaurant}
          highlightedListing={highlightedListing}
          zoomToListingRef={zoomToListingRef}
        />
        
        {/* Max Panels Warning */}
        {showMaxPanelsWarning && (
          <div className="max-panels-warning">
            <p>You can only pin up to {MAX_PANELS} listings at once. Please close a panel before adding another.</p>
          </div>
        )}
        
        {/* Pinned Panels */}
        {pinnedPanels.map((panel, index) => (
          <ListingPanel 
            key={panel.id}
            listing={panel.listing}
            selectedImageIndex={panel.selectedImageIndex}
            onThumbnailClick={handleThumbnailClick}
            onClose={() => handleClosePinnedPanel(panel.id)}
            isVisible={true}
            isExpanded={panel.isExpanded}
            onToggleExpand={() => togglePinnedPanelExpanded(panel.id)}
            isPinned={true}
            panelId={panel.id}
            onUnpin={() => unpinPanel(panel.id)}
            panelIndex={index}
            totalPanels={totalPanels}
            allPinnedPanels={pinnedPanels}
            onViewMapLocation={handleViewRestaurantOnMap}
          />
        ))}
        
        {/* Current Listing Info Panel */}
        {selectedListing && (
          <>
            {/* Removing Panel Toggle Button */}
            <ListingPanel 
              listing={selectedListing}
              selectedImageIndex={selectedImageIndex}
              onThumbnailClick={handleThumbnailClick}
              onClose={handleClosePanel}
              isVisible={isPanelVisible}
              isExpanded={isPanelExpanded}
              onToggleExpand={togglePanelExpanded}
              isPinned={false}
              onPin={pinCurrentPanel}
              panelIndex={pinnedPanels.length}
              totalPanels={totalPanels}
              allPinnedPanels={pinnedPanels}
              onViewMapLocation={handleViewRestaurantOnMap}
            />
          </>
        )}
        
        <ActionButton 
          onClick={toggleActiveListings}
          isLoading={isLoading}
          showingListings={showActiveListings}
        />
        
        {/* Error message */}
        {error && <ErrorMessage message={error} />}
        
        {/* Loading indicator */}
        {isLoading && <LoadingIndicator />}
      </div>
    </div>
  );
}

export default App; 