from fastapi import APIRouter
from app.api.v1.endpoints import listings, places, system

api_router = APIRouter()

# Include routers from endpoint modules
api_router.include_router(listings.router, prefix="/listings", tags=["listings"])
api_router.include_router(places.router, prefix="/places", tags=["places"])
api_router.include_router(system.router, tags=["system"]) 