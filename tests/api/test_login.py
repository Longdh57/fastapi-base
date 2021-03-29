from starlette.testclient import TestClient

from app.core.config import settings
from app.models import User
from tests.faker import fake


class TestLogin:
    def test_success(self, client: TestClient):
        """
            Test api user login success
            Step by step:
            - Khởi tạo data mẫu với password hash
            - Gọi API Login
            - Đầu ra mong muốn:
                . status code: 200
                . access_token != null
                . token_type == 'bearer'
        """
        current_user: User = fake.user({'password': 'secret123'})
        r = client.post(f"{settings.API_PREFIX}/login", data={
            'username': current_user.email,
            'password': 'secret123'
        })
        assert r.status_code == 200
        response = r.json()
        assert response['data']['access_token'] is not None
        assert response['data']['token_type'] == 'bearer'

    def test_incorrect_password(self, client: TestClient):
        """
            Test api user login with incorrect password
            Step by step:
            - Khởi tạo data mẫu với password hash
            - Gọi API Login với wrong password
            - Đầu ra mong muốn:
                . status code: 400
        """
        current_user: User = fake.user({'password': 'secret123'})
        r = client.post(f"{settings.API_PREFIX}/login", data={
            'username': current_user.email,
            'password': 'secret1234'
        })
        assert r.status_code == 400

    def test_user_inactive(self, client: TestClient):
        """
            Test api user is_active = False
            Step by step:
            - Khởi tạo data mẫu với password hash và is_active = False
            - Gọi API Login
            - Đầu ra mong muốn:
                . status code: 401
        """
        current_user: User = fake.user({'password': 'secret123', 'is_active': False})
        r = client.post(f"{settings.API_PREFIX}/login", data={
            'username': current_user.email,
            'password': 'secret123'
        })
        assert r.status_code == 401
