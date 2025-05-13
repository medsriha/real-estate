# Real Estate Map Application

A full-stack web application for visualizing real estate listings on an interactive map. This application allows users to browse active property listings, view property details, and interact with a responsive map interface.

## Project Overview

This project consists of two main components:

1. **Frontend**: React-based web application with Google Maps integration
2. **Backend**: FastAPI-based API for real estate listings with geocoding and nearby places information

## Features

- Interactive Google Maps integration
- Property listings displayed as markers on the map
- Quick preview of properties via InfoBox
- Detailed property panel with image gallery
- Thumbnail navigation with scroll functionality
- Responsive design with clean UI
- Geocoding and nearby places information
- Caching system for improved performance

## Project Structure

```
/
├── frontend/             # React frontend application
│   ├── src/              # Source code
│   │   ├── components/   # React components
│   │   ├── hooks/        # Custom React hooks
│   │   ├── utils/        # Utility functions
│   │   ├── App.js        # Main application component
│   │   └── ...
│   └── ...               # Frontend configuration files
│
├── backend/              # FastAPI backend application
│   ├── app/              # Application code
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core application code
│   │   ├── db/           # Database utilities
│   │   ├── models/       # Data models
│   │   ├── services/     # Business logic services
│   │   └── main.py       # Application entry point
│   ├── tests/            # Test suite
│   ├── data/             # Data storage
│   └── ...               # Backend configuration files
```

## Setup and Installation

### Backend Setup

#### Quick Setup with uv (Recommended)

1. Install uv if you don't have it:
```bash
pip install uv
```

2. Use the setup script to create the environment and install dependencies:
```bash
cd backend
./setup_env.sh        # For production
./setup_env.sh dev    # For development (includes testing tools)
```

#### Manual Backend Setup

1. Create a virtual environment:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt  # For production
pip install -r requirements/dev.txt  # For development
```

#### API Keys for Backend

Create a `.env` file in the backend directory with:
```
RESO_SERVER_TOKEN=your_reso_token
GEOAPIFY_API_KEY=your_geoapify_key
GOOGLE_MAPS_API_KEY=your_google_maps_key
```

### Frontend Setup

1. Configure your Google Maps API key in `frontend/src/config.js`
2. Install dependencies:
```bash
cd frontend
npm install
```

## Running the Application

### Running the Backend

Start the server with:
```bash
cd backend
./start.sh
```

Or manually:
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 5001 --reload
```

### Running the Frontend

```bash
cd frontend
npm start
```

## API Endpoints

### Listings
- `GET /api/listings/active` - Get active real estate listings
- `GET /api/listings/{listing_key}` - Get details for a specific listing

### Places
- `GET /api/places/nearby` - Search for places near a location
- `GET /api/places/photo` - Get a photo by reference

### System
- `GET /api/health` - Check API health
- `GET /api/cache/stats` - Get cache statistics
- `DELETE /api/cache/clear` - Clear cache

## Frontend Architecture

### Component Breakdown

#### Map Components
- **MapComponent**: Main container for Google Maps
- **ListingMarker**: Renders property markers on the map
- **InfoBox**: Property preview that shows when a marker is clicked

#### Listing Components
- **ListingPanel**: Detailed property information panel
- **ImageGallery**: Main property image display
- **ThumbnailGallery**: Horizontally scrollable thumbnails

#### Common Components
- **ActionButton**: Toggle button for showing/hiding listings
- **LoadingIndicator**: Spinner shown during data loading
- **ErrorMessage**: Displays error messages when API calls fail

### Custom Hooks
- **useListings**: Centralizes all listing-related state and logic

### Component Organization
The frontend uses a component index (`src/components/index.js`) to simplify imports and follows a modular CSS organization to maintain clean separation of concerns.

## Backend Architecture

### Core Services
- **Geocoding Service**: Handles location data conversion
- **Places API Service**: Retrieves nearby places information
- **RESO API Service**: Interfaces with real estate data

### Cache Maintenance
Run the cache maintenance script manually:
```bash
cd backend
source .venv/bin/activate
python clear_cache.py

# Options
python clear_cache.py --dry-run   # Show what would be deleted without making changes
python clear_cache.py --json      # Output in JSON format
```

Set up a cron job to automatically clean up expired cache entries:
```bash
cd backend
./cron_setup.sh
```

## Development

### Backend Development

Make sure your virtual environment is activated:
```bash
cd backend
source .venv/bin/activate
```

Run tests:
```bash
pytest
```

Format code:
```bash
black .
isort .
```

Lint code:
```bash
ruff check .
```

### Frontend Development Workflow

The application follows a component-based architecture where:

1. `App.js` is the main component that orchestrates all other components
2. State management is centralized in custom hooks (`useListings.js`)
3. UI components are organized by feature/purpose
4. Common utilities are extracted into the `utils` directory

## Technologies Used

### Frontend
- React (Hooks, Function Components)
- Google Maps API (@vis.gl/react-google-maps)
- Fetch API for data retrieval
- ResizeObserver for responsive elements

### Backend
- FastAPI (Python web framework)
- Pydantic for data validation
- uv for dependency management
- Geocoding and Places APIs

## Code Architecture Principles

1. **Separation of Concerns**: Each component has a single responsibility
2. **Modularity**: Components are modular and reusable
3. **DRY (Don't Repeat Yourself)**: Common code is extracted into utilities
4. **Single Responsibility Principle**: Components do one thing well
5. **Custom Hooks**: Stateful logic is extracted from components
6. **Prop Drilling Minimization**: State is managed at appropriate levels