from datetime import date

from fastapi import APIRouter, Depends
from fastapi_versioning import version

from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBooking, SBookingAdding
from app.exceptions import NotBookingOrUser, RoomCannotBeBooked
from app.tasks.tasks import send_booking_confirmation_email
from app.users.dependencies import get_current_user
from app.users.models import Users

router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"],
)


@router.get("")
@version(1)
async def get_bookings(user: Users = Depends(get_current_user)) -> list[SBooking]:
    return await BookingDAO.find_all(user_id=user.id)


@router.post("")
@version(1)
async def add_bookings(
    room_id: int,
    date_from: date,
    date_to: date,
    user: Users = Depends(get_current_user),
):
    booking = await BookingDAO.add(user.id, room_id, date_from, date_to)
    if not booking:
        raise RoomCannotBeBooked
    booking_model = SBookingAdding.model_validate(booking)
    booking_dict = booking_model.model_dump()
    send_booking_confirmation_email.delay(booking_dict, user.email)


@router.delete("", status_code=204)
@version(1)
async def delete_bookings(booking_id: int, user: Users = Depends(get_current_user)):
    result = await BookingDAO.delete_booking(user.id, booking_id)
    if result != "succes":
        raise NotBookingOrUser
