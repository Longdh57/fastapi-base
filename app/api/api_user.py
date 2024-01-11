import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi_sqlalchemy import db

from app.helpers.exception_handler import CustomException
from app.helpers.login_manager import login_required, PermissionRequired
from app.helpers.paging import Page, PaginationParams, paginate
from app.schemas.sche_base import DataResponse
from app.schemas.sche_user import UserItemResponse, UserCreateRequest, UserUpdateMeRequest, UserUpdateRequest
from app.services.srv_user import UserService
from app.models import User

logger = logging.getLogger()
router = APIRouter()


@router.get("", dependencies=[Depends(login_required)], response_model=Page[UserItemResponse])
def get(params: PaginationParams = Depends()) -> Any:
    """
    API Get list User
    """
    try:
        _query = db.session.query(User)
        users = paginate(model=User, query=_query, params=params)
        return users
    except Exception as e:
        return HTTPException(status_code=400, detail=logger.error(e))


@router.post("", dependencies=[Depends(PermissionRequired('admin'))], response_model=DataResponse[UserItemResponse])
def create(user_data: UserCreateRequest, user_service: UserService = Depends()) -> Any:
    """
    API Create User
    """
    try:
        new_user = user_service.create_user(user_data)
        return DataResponse().success_response(data=new_user)
    except Exception as e:
        raise CustomException(http_code=400, code='400', message=str(e))


@router.get("/me", dependencies=[Depends(login_required)], response_model=DataResponse[UserItemResponse])
def detail_me(current_user: User = Depends(UserService.get_current_user)) -> Any:
    """
    API get detail current User
    """
    return DataResponse().success_response(data=current_user)


@router.put("/me", dependencies=[Depends(login_required)], response_model=DataResponse[UserItemResponse])
def update_me(user_data: UserUpdateMeRequest,
              current_user: User = Depends(UserService.get_current_user),
              user_service: UserService = Depends()) -> Any:
    """
    API Update current User
    """
    try:
        updated_user = user_service.update_me(data=user_data, current_user=current_user)
        return DataResponse().success_response(data=updated_user)
    except Exception as e:
        raise CustomException(http_code=400, code='400', message=str(e))


@router.get("/{user_id}", dependencies=[Depends(login_required)], response_model=DataResponse[UserItemResponse])
def detail(user_id: int, user_service: UserService = Depends()) -> Any:
    """
    API get Detail User
    """
    try:
        return DataResponse().success_response(data=user_service.get(user_id))
    except Exception as e:
        raise CustomException(http_code=400, code='400', message=str(e))


@router.put("/{user_id}", dependencies=[Depends(PermissionRequired('admin'))],
            response_model=DataResponse[UserItemResponse])
def update(user_id: int, user_data: UserUpdateRequest, user_service: UserService = Depends()) -> Any:
    """
    API update User
    """
    try:
        updated_user = user_service.update(user_id=user_id, data=user_data)
        return DataResponse().success_response(data=updated_user)
    except Exception as e:
        raise CustomException(http_code=400, code='400', message=str(e))
