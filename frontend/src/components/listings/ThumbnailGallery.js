import React, { useRef, useEffect, useState } from 'react';
import './listings.css';

function ThumbnailGallery({ 
  media, 
  selectedImageIndex, 
  onThumbnailClick,
  thumbnailHeight = 80,
  thumbnailWidth = 110
}) {
  const thumbnailsContainerRef = useRef(null);
  const thumbnailRefs = useRef([]);
  const [canScrollRight, setCanScrollRight] = useState(false);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [scrollPosition, setScrollPosition] = useState(0);
  const [scrollWidth, setScrollWidth] = useState(1);
  const [containerWidth, setContainerWidth] = useState(1);
  const [lastScrollTime, setLastScrollTime] = useState(0);
  const scrollDebounceTime = 150; // ms to wait before processing scroll event

  // Set up thumbnail refs when listing changes
  useEffect(() => {
    if (media) {
      thumbnailRefs.current = Array(media.length).fill().map(() => React.createRef());
    }
  }, [media]);

  // Find the first visible thumbnail
  const findFirstVisibleThumbnail = () => {
    if (!thumbnailsContainerRef.current || thumbnailRefs.current.length === 0) return 0;
    
    const container = thumbnailsContainerRef.current;
    const containerRect = container.getBoundingClientRect();
    
    // Find the first thumbnail that's at least 50% visible in the container
    for (let i = 0; i < thumbnailRefs.current.length; i++) {
      const ref = thumbnailRefs.current[i];
      if (ref.current) {
        const rect = ref.current.getBoundingClientRect();
        const visibleWidth = Math.min(rect.right, containerRect.right) - Math.max(rect.left, containerRect.left);
        
        // If at least 50% of the thumbnail is visible
        if (visibleWidth > thumbnailWidth / 2) {
          return i;
        }
      }
    }
    
    return 0;
  };
  
  // Check scrollability and update selected image
  const checkScrollability = () => {
    if (thumbnailsContainerRef.current) {
      const container = thumbnailsContainerRef.current;
      
      // Check if we can scroll right (not at the end)
      const canScroll = container.scrollWidth > container.clientWidth;
      
      // Check if we can scroll right
      const canRight = canScroll && 
                        container.scrollLeft < (container.scrollWidth - container.clientWidth - 10); // 10px buffer
      
      // Check if we can scroll left
      const canLeft = canScroll && container.scrollLeft > 10; // 10px buffer
      
      setCanScrollRight(canRight);
      setCanScrollLeft(canLeft);
      
      // Update scroll metrics for scroll indicator
      setScrollPosition(container.scrollLeft);
      setScrollWidth(container.scrollWidth);
      setContainerWidth(container.clientWidth);
    }
  };
  
  // Handle manual scrolling (from mousepad/trackpad)
  const handleManualScroll = () => {
    // Get the first visible thumbnail and update the selected image immediately
    const firstVisibleIndex = findFirstVisibleThumbnail();
    if (firstVisibleIndex !== selectedImageIndex) {
      onThumbnailClick(firstVisibleIndex);
    }
  };

  // Set up scroll event listener
  useEffect(() => {
    const container = thumbnailsContainerRef.current;
    
    if (container) {
      // Add listener for scrollability checks
      container.addEventListener('scroll', checkScrollability);
      
      // Add listener for updating the selected image on manual scroll
      // This will update the main image in real-time as the user scrolls
      const scrollHandler = () => {
        // Update immediately during scroll
        handleManualScroll();
      };
      
      container.addEventListener('scroll', scrollHandler);
      
      // Set up a resize observer
      const resizeObserver = new ResizeObserver(checkScrollability);
      if (container) {
        resizeObserver.observe(container);
      }
      
      return () => {
        if (container) {
          container.removeEventListener('scroll', checkScrollability);
          container.removeEventListener('scroll', scrollHandler);
        }
        resizeObserver.disconnect();
      };
    }
  }, [media, selectedImageIndex]);
  
  // Initial check for scrollability
  useEffect(() => {
    checkScrollability();
  }, [media]);

  // Scroll the thumbnails container
  const scrollThumbnails = (direction) => {
    if (thumbnailsContainerRef.current) {
      const scrollAmount = direction === 'right' ? thumbnailWidth + 5 : -(thumbnailWidth + 5);
      
      // First update the scroll position
      thumbnailsContainerRef.current.scrollBy({
        left: scrollAmount,
        behavior: 'smooth'
      });
      
      // Then immediately update the image (this will be more responsive)
      // For arrow clicks, we can predict what the first visible will be
      let predictedIndex;
      if (direction === 'right') {
        // Find the current first visible and predict the next one
        const currentFirst = findFirstVisibleThumbnail();
        predictedIndex = Math.min(currentFirst + 1, media.length - 1);
      } else {
        // Find the current first visible and predict the previous one
        const currentFirst = findFirstVisibleThumbnail();
        predictedIndex = Math.max(currentFirst - 1, 0);
      }
      
      // Update the main image immediately
      onThumbnailClick(predictedIndex);
    }
  };

  // Calculate the scroll indicator dimensions
  const calculateScrollIndicator = () => {
    // Only show indicator if there are multiple images and scrolling is possible
    if (!media || media.length <= 1 || scrollWidth <= containerWidth) {
      return { display: 'none' };
    }
    
    // Calculate the visible portion width as a percentage of total
    const visiblePercent = containerWidth / scrollWidth;
    const indicatorWidth = Math.max(visiblePercent * 100, 10); // At least 10% wide
    
    // Calculate the scroll position as a percentage
    const maxScrollLeft = scrollWidth - containerWidth;
    const scrollPercent = maxScrollLeft === 0 ? 0 : scrollPosition / maxScrollLeft;
    const indicatorLeft = scrollPercent * (100 - indicatorWidth);
    
    return {
      width: `${indicatorWidth}%`,
      left: `${indicatorLeft}%`
    };
  };

  // Get scroll indicator position and size
  const scrollIndicatorStyle = calculateScrollIndicator();

  if (!media || media.length <= 1) {
    return null;
  }

  return (
    <div style={{ position: 'relative' }}>
      <div 
        ref={thumbnailsContainerRef}
        className="image-thumbnails" 
        style={{ 
          paddingLeft: canScrollLeft ? '30px' : '0',
          paddingRight: canScrollRight ? '30px' : '0', // Add padding for the arrow
        }}
      >
        {media.map((image, index) => (
          <img 
            key={index}
            ref={thumbnailRefs.current[index]}
            src={image.MediaURL} 
            alt={`Property ${index + 1}`}
            className={`thumbnail ${selectedImageIndex === index ? 'selected' : ''}`}
            style={{
              width: thumbnailWidth,
              height: thumbnailHeight,
            }}
            onClick={() => onThumbnailClick(index)}
          />
        ))}
      </div>
      
      {/* Scroll Indicator */}
      <div className="scroll-indicator-track">
        <div 
          className="scroll-indicator-thumb" 
          style={scrollIndicatorStyle}
        />
      </div>
      
      {/* Left Arrow indicator */}
      {canScrollLeft && (
        <div 
          className="scroll-arrow left"
          onClick={() => scrollThumbnails('left')}
        >
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
      )}
      
      {/* Right Arrow indicator */}
      {canScrollRight && (
        <div 
          className="scroll-arrow right"
          onClick={() => scrollThumbnails('right')}
        >
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
      )}
    </div>
  );
}

export default ThumbnailGallery; 