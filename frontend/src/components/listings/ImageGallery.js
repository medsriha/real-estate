import React from 'react';
import ThumbnailGallery from './ThumbnailGallery';
import './listings.css';

function ImageGallery({ media, selectedImageIndex, onThumbnailClick }) {
  const THUMBNAIL_HEIGHT = 80;
  const THUMBNAIL_WIDTH = 110;

  return (
    <div className="listing-images">
      {media && media.length > 0 ? (
        <div className="image-container">
          <img 
            src={media[selectedImageIndex].MediaURL} 
            alt="Property" 
            className="main-image"
          />
          
          {/* Thumbnail row with navigation */}
          {media.length > 1 && (
            <ThumbnailGallery
              media={media}
              selectedImageIndex={selectedImageIndex}
              onThumbnailClick={onThumbnailClick}
              thumbnailHeight={THUMBNAIL_HEIGHT}
              thumbnailWidth={THUMBNAIL_WIDTH}
            />
          )}
        </div>
      ) : (
        <div className="no-images">
          No images available
        </div>
      )}
    </div>
  );
}

export default ImageGallery; 