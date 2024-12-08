import pytest

from app.users.dao import UsersDAO


@pytest.mark.parametrize(
    "user_id,email,is_present",
    [(1, "test1@test1.com", True), (2, "test2@test2.com", True), (4, "email", False)],
)
async def test_find_by_id(user_id, email, is_present):
    user = await UsersDAO.find_by_id(user_id)

    if is_present:
        assert user
        assert user.id == user_id
        assert user.email == email

    else:
        assert not user
