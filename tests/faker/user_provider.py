import logging
import faker.providers

from app.helpers.enums import UserRole
from app.models import User
from fastapi_sqlalchemy import db
from app.core.security import get_password_hash

logger = logging.getLogger()
fake = faker.Faker()


class UserProvider(faker.providers.BaseProvider):
    @staticmethod
    def user(data={}):
        """
        Fake an user in db for testing
        :return: user model object
        """
        user = User(
            full_name=data.get('name') or fake.name(),
            email=data.get('email') or fake.email(),
            hashed_password=get_password_hash(data.get('password')) or get_password_hash(fake.lexify(text='?????????')),
            is_active=data.get('is_active') if data.get('is_active') is not None else True,
            role=data.get('role') if data.get('role') is not None else UserRole.GUEST.value
        )
        with db():
            db.session.add(user)
            db.session.commit()
            db.session.refresh(user)
        return user
