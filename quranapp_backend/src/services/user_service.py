from fastapi import HTTPException

from src.mappers import user_mapper
from src.models import UserModel
from src.dal.actions import user_actions


class UserService:
    __instance = None

    def __init__(self):
        return

    @classmethod
    def instance(cls):
        if not cls.__instance:
            cls.__instance = UserService()
        return cls.__instance

    def get_user_by_id(self, user_id: str) -> UserModel:
        return self.__get_user_by_value__(user_id, user_actions.get_user_by_id)

    def get_user_by_alias(self, alias: str) -> UserModel:
        return self.__get_user_by_value__(alias, user_actions.get_user_by_alias)

    @staticmethod
    def check_if_alias_exists(alias: str) -> bool:
        return user_actions.check_alias_exists(alias)

    def create_user(self, user: UserModel) -> object:
        if self.check_if_alias_exists(user.alias):
            raise HTTPException(status_code=409, detail=f'Alias {user.alias} already in use.')

        if self.get_user_by_id(user.id) is not None:
            raise HTTPException(status_code=409, detail=f'ID already in use.')

        user_dal = user_mapper.map_to_dal(user)
        user_actions.add_user(user_dal)
        return {'message': 'User added successfully'}

    @staticmethod
    def __get_user_by_value__(value, func) -> UserModel:
        user = func(value)

        if user is None:
            return None

        return user_mapper.map_to_model(user)
