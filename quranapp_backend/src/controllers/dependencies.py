from fastapi import Depends

from src.dal.database import get_session
from src.services import tokens_service

api_key_dependency = Depends(tokens_service.verify_api_key)
jwt_dependency = Depends(tokens_service.verify_access_token)
db_session_dependency = Depends(get_session)
