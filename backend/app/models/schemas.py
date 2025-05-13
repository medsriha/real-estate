from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class Coordinates(BaseModel):
    lat: float
    lng: float


class AddressComponents(BaseModel):
    house_number: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postcode: Optional[str] = None
    suburb: Optional[str] = None


class GeocodingResult(BaseModel):
    success: bool
    address: str
    coordinates: Optional[Coordinates] = None
    formatted_address: Optional[str] = None
    address_components: Optional[AddressComponents] = None
    place_id: Optional[str] = None
    error: Optional[str] = None


class Listing(BaseModel):
    """Representation of a real estate listing"""
    ListingKey: str
    ListingId: Optional[str] = None
    StandardStatus: Optional[str] = None
    StreetNumber: Optional[str] = None
    StreetName: Optional[str] = None
    City: Optional[str] = None
    StateOrProvince: Optional[str] = None
    PostalCode: Optional[str] = None
    Country: Optional[str] = None
    BedroomsTotal: Optional[int] = None
    BathroomsTotal: Optional[float] = None
    ListPrice: Optional[float] = None
    LivingArea: Optional[float] = None
    LotSizeArea: Optional[float] = None
    YearBuilt: Optional[int] = None
    PublicRemarks: Optional[str] = None
    Media: Optional[List[Dict[str, Any]]] = None
    coordinates: Optional[Coordinates] = None
    
    class Config:
        extra = "allow"  # Allow extra fields that aren't defined in the model


class Place(BaseModel):
    """Representation of a place from Google Places API"""
    place_id: str
    name: str
    vicinity: Optional[str] = None
    formatted_address: Optional[str] = None
    geometry: Dict[str, Any]
    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    types: Optional[List[str]] = None
    opening_hours: Optional[Dict[str, Any]] = None
    price_level: Optional[int] = None
    
    class Config:
        extra = "allow"  # Allow extra fields


class PlacesResponse(BaseModel):
    """Response model for places search"""
    results: List[Place]
    next_page_token: Optional[str] = None


class CacheStats(BaseModel):
    """Cache statistics response model"""
    places: Dict[str, Any]
    total_cache_size: int
    total_cache_size_formatted: str
    db_size: Optional[int] = None
    db_size_formatted: Optional[str] = None


class CacheClearResponse(BaseModel):
    """Response for cache clearing operation"""
    deleted: Dict[str, int]
    success: bool
    message: str 