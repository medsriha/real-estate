import { useState, useEffect } from 'react';
import config from '../config';

/**
 * Custom hook to manage listing data and state
 */
function useListings() {
  const [showActiveListings, setShowActiveListings] = useState(false);
  const [activeListings, setActiveListings] = useState([]);
  const [pinnedPanels, setPinnedPanels] = useState([]); // Array of pinned listing panels
  const [selectedListing, setSelectedListing] = useState(null); // Current active listing (not pinned)
  const [infoBoxListing, setInfoBoxListing] = useState(null);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isPanelVisible, setIsPanelVisible] = useState(true);
  const [isPanelExpanded, setIsPanelExpanded] = useState(true);
  const [showMaxPanelsWarning, setShowMaxPanelsWarning] = useState(false); // Warning when max panels reached
  const [selectedRestaurant, setSelectedRestaurant] = useState(null); // Restaurant location selected from listing panel
  const [highlightedListing, setHighlightedListing] = useState(null); // Listing to highlight when viewing restaurant
  
  const MAX_PANELS = 10; // Maximum number of panels allowed

  // Function to fetch active listings from the Flask API
  const fetchActiveListings = async () => {
    try {
      // Call our Flask API endpoint
      const response = await fetch(`${config.BACKEND_URL}/api/listings/active?limit=100`);
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (err) {
      console.error("Error fetching listings:", err);
      throw err;
    }
  };
  
  // Load listings when the button is clicked
  useEffect(() => {
    let isMounted = true;
    
    if (showActiveListings) {
      setIsLoading(true);
      setError(null);
      
      fetchActiveListings()
        .then(listings => {
          if (isMounted) {
            setActiveListings(listings);
            setIsLoading(false);
          }
        })
        .catch(err => {
          if (isMounted) {
            console.error("Error fetching listings:", err);
            setError("Failed to fetch listings. Please try again.");
            setIsLoading(false);
          }
        });
    } else {
      setActiveListings([]);
      setSelectedListing(null);
      // Don't reset pinned panels when toggling listings
    }
    
    return () => {
      isMounted = false;
    };
  }, [showActiveListings]);
  
  // Add an event listener to close only unpinned infobox and primary panel when clicking outside
  useEffect(() => {
    const handleDocumentClick = (e) => {
      // Don't close if we're clicking inside a marker, info box, panel, or toggle buttons
      if (
        e.target.closest('.marker-price') || 
        e.target.closest('.info-box') || 
        e.target.closest('.listing-panel') ||
        e.target.closest('.action-button') ||
        e.target.closest('.expand-toggle-button') ||
        e.target.closest('.pin-panel-button') ||
        e.target.closest('.unpin-panel-button')
      ) {
        return;
      }
      
      // Close any info box
      if (infoBoxListing) {
        setInfoBoxListing(null);
      }
      
      // Close the selected listing panel (we only close unpinned panels)
      setSelectedListing(null);
    };
    
    // Add the event listener
    document.addEventListener('click', handleDocumentClick);
    
    // Clean up on unmount
    return () => {
      document.removeEventListener('click', handleDocumentClick);
    };
  }, [infoBoxListing]);
  
  // Auto-hide the max panels warning after 5 seconds
  useEffect(() => {
    let timer;
    if (showMaxPanelsWarning) {
      timer = setTimeout(() => {
        setShowMaxPanelsWarning(false);
      }, 5000);
    }
    return () => clearTimeout(timer);
  }, [showMaxPanelsWarning]);
  
  // Handle toggle listings button click
  const toggleActiveListings = () => {
    setShowActiveListings(!showActiveListings);
  };
  
  // Handle marker click to show info box
  const handleInfoClick = (listing) => {
    // Toggle info box
    if (infoBoxListing && infoBoxListing.ListingKey === listing.ListingKey) {
      setInfoBoxListing(null);
    } else {
      // Show info box for the new listing
      setInfoBoxListing(listing);
    }
  };
  
  // Handle marker click for expanding to full panel
  const handleMarkerClick = (listing, zoomToListing) => {
    setSelectedListing(listing);
    setInfoBoxListing(null); // Close the infobox when opening details panel
    setSelectedImageIndex(0); // Reset to first image when selecting a new listing
    setIsPanelVisible(true); // Make sure panel is visible
    setIsPanelExpanded(true); // Make sure panel is expanded
    if (zoomToListing) {
      zoomToListing(listing);
    }
  };
  
  // Handle thumbnail click
  const handleThumbnailClick = (index, panelId = null) => {
    if (panelId !== null) {
      // Update image for a pinned panel
      setPinnedPanels(prevPanels => 
        prevPanels.map(panel => 
          panel.id === panelId
            ? { ...panel, selectedImageIndex: index }
            : panel
        )
      );
    } else {
      // Update image for the main panel
      setSelectedImageIndex(index);
    }
  };

  // Handle close listing panel
  const handleClosePanel = () => {
    setSelectedListing(null);
  };
  
  // Handle closing a pinned panel
  const handleClosePinnedPanel = (panelId) => {
    setPinnedPanels(prevPanels => prevPanels.filter(panel => panel.id !== panelId));
  };

  // Toggle panel visibility
  const togglePanelVisibility = () => {
    setIsPanelVisible(!isPanelVisible);
  };

  // Toggle panel expanded state
  const togglePanelExpanded = () => {
    setIsPanelExpanded(!isPanelExpanded);
  };
  
  // Toggle pinned panel expanded state
  const togglePinnedPanelExpanded = (panelId) => {
    setPinnedPanels(prevPanels => 
      prevPanels.map(panel => 
        panel.id === panelId
          ? { ...panel, isExpanded: !panel.isExpanded }
          : panel
      )
    );
  };
  
  // Pin the current panel
  const pinCurrentPanel = () => {
    if (!selectedListing) return;
    
    // Check if we already have the maximum number of panels
    if (pinnedPanels.length >= MAX_PANELS) {
      setShowMaxPanelsWarning(true);
      return;
    }
    
    // Check if this listing is already pinned
    const isAlreadyPinned = pinnedPanels.some(
      panel => panel.listing.ListingKey === selectedListing.ListingKey
    );
    
    if (!isAlreadyPinned) {
      const newPinnedPanel = {
        id: Date.now(), // Unique ID for the panel
        listing: selectedListing,
        selectedImageIndex,
        isExpanded: true
      };
      
      setPinnedPanels(prev => [...prev, newPinnedPanel]);
    }
    
    // Clear the current non-pinned panel
    setSelectedListing(null);
  };
  
  // Unpin a pinned panel (convert it to the current panel)
  const unpinPanel = (panelId) => {
    // Find the panel to unpin
    const panelToUnpin = pinnedPanels.find(panel => panel.id === panelId);
    
    if (panelToUnpin) {
      // If there's already a selected listing, close it or pin it first
      if (selectedListing) {
        // Check if we can pin the current panel before replacing it
        if (pinnedPanels.length < MAX_PANELS) {
          // Pin the current panel
          pinCurrentPanel();
        } else {
          // Just close the current panel since we can't pin it
          setSelectedListing(null);
        }
      }
      
      // Set the unpinned panel as the current selected listing
      setSelectedListing(panelToUnpin.listing);
      setSelectedImageIndex(panelToUnpin.selectedImageIndex);
      setIsPanelVisible(true);
      setIsPanelExpanded(panelToUnpin.isExpanded);
      
      // Remove the panel from pinned panels
      setPinnedPanels(prevPanels => prevPanels.filter(panel => panel.id !== panelId));
    }
  };

  // Handle viewing a restaurant on the map from a listing panel
  const handleViewRestaurantOnMap = (restaurantData) => {
    // Extract the restaurant location
    const { lat, lng, name, place_id, listing } = restaurantData;
    
    if (!lat || !lng) {
      console.error('Restaurant coordinates are missing');
      return;
    }
    
    // Set the restaurant location to show on the map
    setSelectedRestaurant({
      lat,
      lng,
      name: name || 'Restaurant',
      place_id
    });
    
    // Also set the listing to highlight that this restaurant belongs to
    if (listing) {
      setHighlightedListing(listing);
    }
  };

  return {
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
  };
}

export default useListings; 