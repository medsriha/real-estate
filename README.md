# Real Estate Map Application

A modern web application for visualizing real estate listings on an interactive map. This application allows users to browse active property listings, view property details, and interact with a responsive map interface.

## Features

- Interactive Google Maps integration
- Property listings displayed as markers on the map
- Quick preview of properties via InfoBox
- Detailed property panel with image gallery
- Thumbnail navigation with scroll functionality
- Responsive design with clean UI

## Project Structure

The project follows React best practices by organizing components based on features and responsibilities:

```
frontend/src/
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

## Component Breakdown

### Map Components

#### MapComponent
- Main container for Google Maps
- Renders the map, markers, and info boxes
- Handles map interactions

#### ListingMarker
- Renders property markers on the map
- Displays price in a compact format
- Handles click events for showing property info

#### InfoBox
- Property preview that shows when a marker is clicked
- Displays basic property information and primary image
- Includes a button to view full details

### Listing Components

#### ListingPanel
- Detailed property information panel
- Displays when a user wants to see more details
- Contains image gallery and property specifications

#### ImageGallery
- Main property image display
- Contains the ThumbnailGallery for navigating multiple images

#### ThumbnailGallery
- Horizontally scrollable thumbnails with navigation arrows
- Handles complex scroll logic and thumbnail selection
- Uses refs to track visible thumbnails

### Common Components

#### ActionButton
- Toggle button for showing/hiding listings
- Adapts its text based on current state

#### LoadingIndicator
- Spinner shown during data loading

#### ErrorMessage
- Displays error messages when API calls fail

## Custom Hooks

### useListings
- Centralizes all listing-related state and logic
- Handles API calls to fetch listings
- Manages selection states and user interactions
- Provides methods for component interaction

## Utility Functions

### formatters.js
- `formatMarkerPrice`: Formats prices for map markers (e.g., $1.2M)
- `formatPrice`: Formats full price with currency formatting
- `formatAddress`: Combines address components into a readable string

## Key React Patterns Used

1. **Component Composition**: Breaking UI into smaller, reusable components
2. **Custom Hooks**: Extracting stateful logic into reusable hooks
3. **Container/Presentational Pattern**: Separating data logic from UI components
4. **Conditional Rendering**: Showing/hiding components based on state
5. **Event Handling**: Managing user interactions across components
6. **React Refs**: Using refs for DOM manipulation in the thumbnail gallery
7. **Responsive Design**: Adapting UI based on available space

## Implementation Details

### State Management
- Used React's built-in useState and useEffect hooks for state management
- Centralized listing-related state in a custom hook
- Implemented proper data flow with props

### Styling Approach
- Used inline styles for component-specific styling
- Leveraged CSS classes for common styling patterns

### API Integration
- Integrated with a backend API to fetch property listings
- Implemented proper loading and error states

## Technologies Used

- React (Hooks, Function Components)
- Google Maps API (@vis.gl/react-google-maps)
- Fetch API for data retrieval
- ResizeObserver for responsive elements

## Styling Approach

The application uses a modular CSS organization to maintain clean separation of concerns:

```
frontend/src/
├── components/
│   ├── common/
│   │   └── common.css        # Styles for common UI components
│   ├── listings/
│   │   └── listings.css      # Styles for listing-related components
│   └── map/
│       └── map.css           # Styles for map-related components
├── App.css                   # Application-wide styles
```

This approach:
- Groups styles with their related components
- Makes it easier to find and update styles
- Prevents style conflicts by scoping them to their components
- Improves maintainability by organizing styles logically

## Code Architecture Improvements

The codebase was restructured following these principles:

1. **Separation of Concerns**: Each component has a single responsibility
2. **Modularity**: Components are modular and reusable
3. **DRY (Don't Repeat Yourself)**: Common code is extracted into utilities
4. **Single Responsibility Principle**: Components do one thing well
5. **Custom Hooks**: Stateful logic is extracted from components
6. **Prop Drilling Minimization**: State is managed at appropriate levels

This architecture makes the codebase:
- Easier to maintain and extend
- More testable
- Better organized
- More performant through component isolation