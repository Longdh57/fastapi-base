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
def create(user_data: UserCreateRequest) -> Any:
    """
    API Create User
    """
    try:
        exist_user = db.session.query(User).filter(User.email == user_data.email).first()
        if exist_user:
            raise Exception('Email already exists')
        new_user = UserService().create_user(user_data)
        return DataResponse().success_response(data=new_user)
    except Exception as e:
        raise CustomException(http_code=400, code='400', message=str(e))


@router.get("/me", dependencies=[Depends(login_required)], response_model=DataResponse[UserItemResponse])
def detail_me(current_user: User = Depends(UserService().get_current_user)) -> Any:
    """
    API get detail current User
    """
    return DataResponse().success_response(data=current_user)


@router.put("/me", dependencies=[Depends(login_required)], response_model=DataResponse[UserItemResponse])
def update_me(user_data: UserUpdateMeRequest,
              current_user: User = Depends(UserService().get_current_user)) -> Any:
    """
    API Update current User
    """
    try:
        if user_data.email is not None:
            exist_user = db.session.query(User).filter(
                User.email == user_data.email, User.id != current_user.id).first()
            if exist_user:
                raise Exception('Email already exists')
        updated_user = UserService().update_me(data=user_data, current_user=current_user)
        return DataResponse().success_response(data=updated_user)
    except Exception as e:
        raise CustomException(http_code=400, code='400', message=str(e))


@router.get("/{user_id}", dependencies=[Depends(login_required)], response_model=DataResponse[UserItemResponse])
def detail(user_id: int) -> Any:
    """
    API get Detail User
    """
    try:
        exist_user = db.session.query(User).get(user_id)
        if exist_user is None:
            raise Exception('User already exists')
        return DataResponse().success_response(data=exist_user)
    except Exception as e:
        raise CustomException(http_code=400, code='400', message=str(e))


@router.put("/{user_id}", dependencies=[Depends(PermissionRequired('admin'))],
            response_model=DataResponse[UserItemResponse])
def update(user_id: int, user_data: UserUpdateRequest) -> Any:
    """
    API update User
    """
    try:
        exist_user = db.session.query(User).get(user_id)
        if exist_user is None:
            raise Exception('User already exists')
        updated_user = UserService().update(user=exist_user, data=user_data)
        return DataResponse().success_response(data=updated_user)
    except Exception as e:
        raise CustomException(http_code=400, code='400', message=str(e))
