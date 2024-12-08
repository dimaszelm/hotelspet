from datetime import date

from fastapi import APIRouter
from fastapi_cache.decorator import cache

from app.hotels.dao import HotelsDAO
from app.hotels.schemas import SHotels

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("/{location}")
@cache(expire=30)
async def get_hotels(location: str, date_from: date, date_to: date) -> list[SHotels]:
    hotels = await HotelsDAO.find_available_hotels(location, date_from, date_to)
    return hotels
