# FASTAPI BASE
Đây là phiên bản Backend base từ framework FastAPI. Trong code base này đã dựng sẵn các phần
- Framework: FastAPI
- Database: Postgresql >= 12
- Alembic
- API Login
- API CRUD User, API Get Me & API Update Me
- Phân trang
- Xác thực người dùng với JWT
- Permission_required & Login_required sử dụng FastAPI-Depends
- Logging
## Installation
Cách 1:
- Clone Project
- Cài đặt Postgresql & Create Database
- Cài đặt requirements.txt
- Run project ở cổng 8000
```
$ git clone
$ virtualenv -p python3 .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Cách 2: Dùng Docker & Docker Compose - đơn giản hơn nhưng phải có kiến thức Docker
- Clone Project
- Run docker-compose
```
$ git clone
$ docker-compose up -d
```
## Cấu trúc project
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