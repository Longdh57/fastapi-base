![alt text](logo-teal.png "FastAPI")

# FASTAPI BASE
Đây là phiên bản Backend base từ framework FastAPI. Trong code base này đã cấu hình sẵn
- FastAPI
- Postgresql >= 12
- Alembic
- API Login
- API CRUD User, API Get Me & API Update Me
- Phân trang
- Authen/Authorize với JWT
- Permission_required & Login_required
- Logging
- Pytest

## Mô tả
Dựng khung project để phát triển dự án khá tốn kém thời gian và công sức.

Vì vậy mình quyết định dựng FastAPI Base cung cấp sẵn các function basic nhất như CRUD User, Login, Register.

Project đã bao gồm migration DB và pytest để sẵn sàng sử dụng trong môi trường doanh nghiệp.

## Installation
**Cách 1:**
- Clone Project
- Cài đặt Postgresql & Create Database
- Cài đặt requirements.txt
- Run project ở cổng 8000
```
// Tạo postgresql Databases via CLI (Ubuntu 20.04)
$ sudo -u postgres psql
# CREATE DATABASE fastapi_base;
# CREATE USER db_user WITH PASSWORD 'secret123';
# GRANT ALL PRIVILEGES ON DATABASE fastapi_base TO db_user;

// Clone project & run
$ git clone https://github.com/Longdh57/fastapi-base
$ cd fastapi-base
$ virtualenv -p python3 .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ cp env.example .env       // Recheck SQL_DATABASE_URL ở bước này
$ alembic upgrade head
$ uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
**Cách 2:** Dùng Docker & Docker Compose - đơn giản hơn nhưng cần có kiến thức Docker
- Clone Project
- Run docker-compose
```
$ git clone https://github.com/Longdh57/fastapi-base
$ cd fastapi-base
$ DOCKER_BUILDKIT=1 docker build -t fastapi-base:latest .
$ docker-compose up -d
```

## Cấu trúc project
```
.  
├── alembic  
│   ├── versions    // thư mục chứa file migrations  
│   └── env.py  
├── app  
│   ├── api         // các file api được đặt trong này  
│   ├── core        // chứa file config load các biến env & function tạo/verify JWT access-token  
│   ├── db          // file cấu hình make DB session  
│   ├── helpers     // các function hỗ trợ như login_manager, paging  
│   ├── models      // Database model, tích hợp với alembic để auto generate migration  
│   ├── schemas     // Pydantic Schema  
│   ├── services    // Chứa logic CRUD giao tiếp với DB  
│   └── main.py     // cấu hình chính của toàn bộ project  
├── tests  
│   ├── api         // chứa các file test cho từng api  
│   ├── faker       // chứa file cấu hình faker để tái sử dụng  
│   ├── .env        // config DB test  
│   └── conftest.py // cấu hình chung của pytest  
├── .gitignore  
├── alembic.ini  
├── docker-compose.yaml  
├── Dockerfile  
├── env.example  
├── logging.ini     // cấu hình logging  
├── postgresql.conf // file cấu hình postgresql, sử dụng khi run docker-compose  
├── pytest.ini      // file setup cho pytest  
├── README.md  
└── requirements.txt
```

## Demo URL
Đang cập nhật
