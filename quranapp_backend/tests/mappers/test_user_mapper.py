import uuid

from src.dal.models import User as UserDal
from src.models import UserModel
from src.mappers.user_mapper import map_to_dal


def test_map_to_dal():
    user_id = str(uuid.uuid4())
    user = UserModel(id=user_id, alias="  tESt  ", name="  Name", surname="Surname  ")

    user_dal = map_to_dal(user)

    assert user_dal is not None
    assert type(user_dal) is UserDal
    assert user_dal.id == user_id
    assert user_dal.alias == "test"
    assert user_dal.name == "Name"
    assert user_dal.surname == "Surname"
