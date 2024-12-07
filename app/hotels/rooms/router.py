from datetime import date

from fastapi import APIRouter

from app.hotels.rooms.dao import RoomsDAO
from app.hotels.rooms.schemas import SRooms

router = APIRouter(prefix="/hotels", tags=["Комнаты"])


@router.get("/{hotel_id}/rooms")
async def get_hotels_id_rooms(
    hotel_id: int, date_from: date, date_to: date
) -> list[SRooms]:
    rooms = await RoomsDAO.all_rooms_in_hotel(hotel_id, date_from, date_to)
    return rooms
