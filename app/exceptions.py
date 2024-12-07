from fastapi import HTTPException, status


class BookingException(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Произошла ошибка"

    def __init__(self, detail: str = None, status_code: int = None):
        super().__init__(
            status_code=status_code or self.status_code, detail=detail or self.detail
        )


class UserAlreadyExistsException(BookingException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь уже существует"


class IncorrectEmailOrPasswordException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверная почта или пароль"


class TokenExpiredException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен истек"


class TokenNotFoundException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен отсутствует"


class IncorrectTokenFormatException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный формат токена"


class UserIsNotPresentException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Пользователь не найден"


class RoomCannotBeBooked(BookingException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Не осталось свободных номеров"


class NotBookingOrUser(BookingException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Данный пользователь не бронировал данный id заказа"
