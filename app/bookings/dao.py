from datetime import date

from sqlalchemy import and_, delete, func, insert, or_, select
from sqlalchemy.exc import SQLAlchemyError

from app.bookings.models import Bookings
from app.DAO.base import BaseDAO
from app.database import async_session_maker
from app.hotels.rooms.models import Rooms
from app.logger import logger

class BookingDAO(BaseDAO):
    model = Bookings

    @classmethod
    async def add(
        cls,
        user_id: int,
        room_id: int,
        date_from: date,
        date_to: date,
    ):
        try:
            async with async_session_maker() as session:
                booked_rooms = (
                    select(Bookings)
                    .where(
                        and_(
                            Bookings.room_id == room_id,
                            or_(
                                and_(
                                    Bookings.date_from >= date_from,
                                    Bookings.date_from <= date_to,
                                ),
                                and_(
                                    Bookings.date_from <= date_from,
                                    Bookings.date_from > date_to,
                                ),
                            ),
                        )
                    )
                    .cte("booked_rooms")
                )

                get_rooms_left = (
                    select(
                        (Rooms.quantity - func.count(booked_rooms.c.room_id)).label(
                            "rooms_left"
                        )
                    )
                    .select_from(Rooms)
                    .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
                    .where(Rooms.id == room_id)
                    .group_by(Rooms.quantity, booked_rooms.c.room_id)
                )
                # print(get_rooms_left.compile(engine, compile_kwargs = {"literal_binds":True}))

                rooms_left = await session.execute(get_rooms_left)
                rooms_left: int = rooms_left.scalar()

                if rooms_left> 0:
                    get_price = select(Rooms.price).filter_by(id=room_id)
                    price = await session.execute(get_price)
                    price: int = price.scalar()
                    add_booking = (
                        insert(Bookings)
                        .values(
                            room_id=room_id,
                            user_id=user_id,
                            date_from=date_from,
                            date_to=date_to,
                            price=price,
                        )
                        .returning(Bookings)
                    )

                    new_booking = await session.execute(add_booking)
                    await session.commit()
                    return new_booking.scalar()
                else:
                    return None
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database"
            elif isinstance(e, Exception):
                msg = "Unknown"
            msg += "Exc: Cannot add booking"
            extra = {
                "user_id": user_id,
                "room_id": room_id,
                "date_from": date_from,
                "date_to": date_to
            }
            logger.error(msg, extra=extra, exc_info=True)

    @classmethod
    async def find_all(cls, user_id: int):
        async with async_session_maker() as session:
            query = (
                select(
                    Bookings.id,
                    Bookings.room_id,
                    Bookings.user_id,
                    Bookings.date_from,
                    Bookings.date_to,
                    Bookings.price,
                    Bookings.total_cost,
                    Bookings.total_days,
                    Rooms.image_id,
                    Rooms.name,
                    Rooms.description,
                    Rooms.services,
                )
                .join(Rooms, Bookings.room_id == Rooms.id)
                .where(Bookings.user_id == user_id)
            )

            results = await session.execute(query)

            bookings = results.mappings().all()
            return [dict(row) for row in bookings]

    @classmethod
    async def delete_booking(cls, user_id, booking_id: int):
        async with async_session_maker() as session:
            booking_query = select(Bookings).where(
                and_(Bookings.id == booking_id, Bookings.user_id == user_id)
            )

            booking = await session.execute(booking_query)
            booking = booking.scalar()

            if not booking:
                return None

            stmt = delete(Bookings).where(Bookings.id == booking_id)
            await session.execute(stmt)
            await session.commit()

            return "succes"
