from datetime import date

from sqlalchemy import and_, func, select

from app.bookings.models import Bookings
from app.DAO.base import BaseDAO
from app.database import async_session_maker
from app.hotels.rooms.models import Rooms


class RoomsDAO(BaseDAO):
    model = Rooms

    @classmethod
    async def all_rooms_in_hotel(cls, hotel_id: int, date_from: date, date_to: date):
        async with async_session_maker() as session:
            # CTE для забронированных комнат
            booked_rooms = (
                select(Bookings.room_id, func.count().label("booked_count"))
                .where(
                    and_(Bookings.date_from <= date_to, Bookings.date_to >= date_from)
                )
                .group_by(Bookings.room_id)
                .cte("booked_rooms")
            )

            # Основной запрос для получения информации о комнатах
            query = (
                select(
                    Rooms.id.label("id"),
                    Rooms.hotel_id,
                    Rooms.name,
                    Rooms.description,
                    Rooms.services,
                    Rooms.price,
                    Rooms.quantity,
                    Rooms.image_id,
                    (
                        Rooms.price * (func.date(date_to) - func.date(date_from)) + 1
                    ).label("total_cost"),
                    (
                        Rooms.quantity
                        - func.coalesce(func.count(booked_rooms.c.room_id), 0)
                    ).label("rooms_left"),
                )
                .select_from(Rooms)
                .outerjoin(booked_rooms, booked_rooms.c.room_id == Rooms.id)
                .where(Rooms.hotel_id == hotel_id)
                .group_by(
                    Rooms.id,
                    Rooms.hotel_id,
                    Rooms.name,
                    Rooms.description,
                    Rooms.price,
                    Rooms.quantity,
                    Rooms.image_id,
                )
                .order_by(Rooms.id)
            )

            result = await session.execute(query)
            room_details = result.mappings().all()

            return room_details
