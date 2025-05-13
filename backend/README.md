# Real Estate Listings API

A FastAPI-based API for real estate listings with geocoding and nearby places information.

## Project Structure

```
backend/
├── app/
│   ├── api/                 # API endpoints
│   │   └── v1/              # API version 1
│   │       ├── endpoints/   # API endpoint modules
│   │       └── router.py    # API router configuration
│   ├── core/                # Core application code
│   │   ├── config.py        # Application settings
│   │   └── maintenance.py   # Cache maintenance utilities
│   ├── db/                  # Database utilities
│   ├── models/              # Data models
│   │   ├── database.py      # Database models
│   │   └── schemas.py       # Pydantic schemas
│   ├── services/            # Business logic services
│   │   ├── geocoding.py     # Geocoding service
│   │   ├── places.py        # Places API service
│   │   └── reso.py          # RESO API service
│   └── main.py              # Application entry point
├── tests/                   # Test suite
├── data/                    # Data storage
├── requirements/            # Requirements files
│   ├── base.txt             # Base requirements
│   └── dev.txt              # Development requirements
├── requirements.txt         # Main requirements file
├── clear_cache.py           # Cache maintenance script
├── start.sh                 # Script to start the application
├── setup_env.sh             # Script to set up the environment
├── cron_setup.sh            # Script to set up cron job
└── pyproject.toml           # Project configuration
```

## Setup and Installation

### Quick Setup with uv (Recommended)

This project uses `uv` for faster dependency installation.

1. Install uv if you don't have it:
```bash
pip install uv
```

2. Use the setup script to create the environment and install dependencies:
```bash
./setup_env.sh        # For production
./setup_env.sh dev    # For development (includes testing tools)
```

### Manual Setup

If you prefer the manual approach:

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt  # For production
pip install -r requirements/dev.txt  # For development
```

## API Keys

Create a `.env` file with the following variables:
```
RESO_SERVER_TOKEN=your_reso_token
GEOAPIFY_API_KEY=your_geoapify_key
GOOGLE_MAPS_API_KEY=your_google_maps_key
```

## Running the Application

Start the server with:
```bash
./start.sh
```

Or manually:
```bash
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 5001 --reload
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

## Cache Maintenance

Run the cache maintenance script manually:
```bash
source .venv/bin/activate
python clear_cache.py

# Options
python clear_cache.py --dry-run   # Show what would be deleted without making changes
python clear_cache.py --json      # Output in JSON format
```

Set up a cron job to automatically clean up expired cache entries:
```bash
./cron_setup.sh
```

## Development

Make sure your virtual environment is activated:
```bash
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

## Performance Benefits with uv

This project benefits from using `uv`, a fast Python package installer:

- Faster dependency resolution and installation
- More efficient environment setup
- Parallel downloads of packages
- Generally better performance than pip

However, the regular Python toolchain (pip, venv) works fine too. 