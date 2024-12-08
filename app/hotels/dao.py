from datetime import date

from sqlalchemy import and_, distinct, func, or_, select

from app.bookings.models import Bookings
from app.DAO.base import BaseDAO
from app.database import async_session_maker
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms


class HotelsDAO(BaseDAO):
    model = Hotels

    @classmethod
    async def find_available_hotels(cls, location: str, date_from: date, date_to: date):
        async with async_session_maker() as session:
            booked_rooms = (
                select(Bookings.room_id)
                .where(
                    or_(
                        and_(
                            Bookings.date_from <= date_to, Bookings.date_to >= date_from
                        )
                    )
                )
                .cte("booked_rooms")
            )

            query = (
                select(
                    Hotels.id,
                    Hotels.name,
                    Hotels.location,
                    Hotels.services,
                    Hotels.rooms_quantity,
                    Hotels.image_id,
                    (
                        Hotels.rooms_quantity
                        - func.coalesce(func.count(distinct(booked_rooms.c.room_id)), 0)
                    ).label("rooms_left"),
                )
                .join(Rooms, Rooms.hotel_id == Hotels.id)
                .outerjoin(booked_rooms, booked_rooms.c.room_id == Rooms.id)
                .where(Hotels.location.ilike(f"%{location}%"))
                .group_by(Hotels.id, Hotels.name, Hotels.location, Hotels.image_id)
                .having(
                    (
                        Hotels.rooms_quantity
                        - func.coalesce(func.count(distinct(booked_rooms.c.room_id)), 0)
                    )
                    > 0
                )
            )

            results = await session.execute(query)
            hotels = results.mappings().all()

            return hotels
