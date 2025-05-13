# Real Estate Map Frontend

This directory contains the React frontend for the Real Estate Map application.

## Directory Structure

```
src/
├── components/            # All React components
│   ├── common/            # Shared UI components
│   │   ├── ActionButton.js      # Toggle button for listings
│   │   ├── ErrorMessage.js      # Error display component
│   │   └── LoadingIndicator.js  # Loading spinner
│   │
│   ├── listings/          # Property listing related components
│   │   ├── ImageGallery.js      # Main image and thumbnails container
│   │   ├── ListingPanel.js      # Detailed property information panel
│   │   └── ThumbnailGallery.js  # Scrollable thumbnail gallery
│   │
│   └── map/               # Map related components
│       ├── InfoBox.js           # Property preview popup
│       ├── ListingMarker.js     # Map marker for each property
│       └── MapComponent.js      # Google Maps wrapper
│
├── hooks/                 # Custom React hooks
│   └── useListings.js     # State and data management for listings
│
├── utils/                 # Utility functions
│   └── formatters.js      # Data formatting utilities
│
├── App.js                 # Main application component
├── App.css                # Main styles
├── config.js              # Configuration settings
└── index.js               # Entry point
```

## Setup and Running

1. Configure your Google Maps API key in `src/config.js`
2. Install dependencies:
   ```
   npm install
   ```
3. Start the development server:
   ```
   npm start
   ```

## Development Workflow

The application follows a component-based architecture where:

1. `App.js` is the main component that orchestrates all other components
2. State management is centralized in custom hooks (`useListings.js`)
3. UI components are organized by feature/purpose
4. Common utilities are extracted into the `utils` directory

When adding new features:
- Consider which logical component group they belong to
- Extract reusable logic into hooks or utilities
- Maintain the separation of concerns pattern

## Component Dependencies

- `App` → Uses MapComponent, ListingPanel, common components, and useListings hook
- `MapComponent` → Uses ListingMarker and InfoBox
- `ListingPanel` → Uses ImageGallery
- `ImageGallery` → Uses ThumbnailGallery

This hierarchical structure keeps the codebase modular and maintainable.

## Component Organization

### Component Index

The application uses a component index (`src/components/index.js`) to simplify imports:

```javascript
// In App.js
import {
  MapComponent,
  ListingPanel,
  ActionButton,
  LoadingIndicator,
  ErrorMessage
} from './components';
```

This approach:
- Makes imports cleaner and more organized
- Makes it easier to refactor component locations
- Provides a single entry point for all component exports

### CSS Organization

Each component group has its own CSS file:

```
components/
├── common/common.css     # Styles for common UI components
├── listings/listings.css # Styles for listing-related components
└── map/map.css           # Styles for map-related components
```

This modular approach keeps styles organized and avoids conflicts between components. 