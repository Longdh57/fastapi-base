from functools import wraps

from fastapi import HTTPException


def permission_required(*permission):
    def wrapper(fn):

        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if current_user.role not in permission:
                raise HTTPException(status_code=400,
                                    detail=f'User {current_user.email} can not access this api')
            else:
                return fn(*args, **kwargs)

        return wrapper

    return wrapper
