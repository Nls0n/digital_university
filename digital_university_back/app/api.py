from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog


LOG = structlog.get_logger()
PATH = "/digital_university"

app = FastAPI()
origins = [
    "http://localhost:3000",  # адрес React/Vue dev-сервера
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,    # список разрешённых источников
    allow_credentials=True,
    allow_methods=["*"],      # разрешить все методы 
    allow_headers=["*"],      # разрешить все заголовки
)


@app.post("/digital_university/api/v1/auth")
async def auth():
    """auth logic"""
    pass


@app.get("/digital_university/api/v1/course/{course_id}/students")
async def get_students_by_course(course_id: int):
    pass


app.get("/digital_university/api/v1/teacher/{teacher_id}/students")
async def get_students_by_teacher(teacher_id: int):
    pass