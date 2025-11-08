from fastapi import FastAPI, HTTPException, status, Depends
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import structlog
from sqlalchemy import select, update, insert, values
from sqlalchemy.orm import Session
from .database import get_db, get_redis, init_redis, close_redis, close_engine, create_tables
from .models import *
import redis.asyncio as redis

LOG = structlog.get_logger()
PATH = "/digital_university"

@asynccontextmanager
async def lifespan(app: FastAPI):  # lifespan для дополнительного слоя логики при включении и отключении приложения, найстройка интеграций
    LOG.info("Запуск приложения, создание таблиц в бд")
    try:
        await create_tables()
        LOG.info("Таблицы успешно созданы или существуют")
    except Exception as e:
        LOG.error(f"Ошибка при создании таблиц в бд. Ошибка {str(e)}")
    
    try:
        redis_client = await init_redis()
        if redis_client:
            app.state.redis = redis_client
            LOG.info("Redis подключен успешно")
        else:
            LOG.error("Redis не подключен")
            app.state.redis = None
    except Exception as e:
        LOG.error("Ошибка при инициализации Redis")
    
    app.state.cache_enabled = redis_client is not None
    app.state.is_ready = True

    LOG.info("Postgres и Redis инициализированы, интеграции работают исправно")

    yield

    LOG.info("Отключение приложения и интеграций")
    await close_redis()
    LOG.info("Redis отключен")
    await close_engine()
    LOG.info("Postgres отключен")

    LOG.info("Приложение остановлено")

app = FastAPI(lifespan=lifespan)  # бинд lifespan
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
@app.get('/cache/{key}')
async def get_cached_value(key: str, redis_client: redis.Redis = Depends(get_redis), status_code=status.HTTP_200_OK):
    """Ручка для получения кэшированных значений из Redis"""
    if not redis_client:
        LOG.error("Не удалось получить значение из кэша. Redis недоступен")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Redis unvailable")
    value = await redis_client.get(key)
    if value is None:
        LOG.error("Не удалось получить значение из кэша. Несуществующий ключ")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Value not found in cache")
    return {"status": "accessed", "key": key, "value": value}

@app.post("/cache/{key}", status_code=status.HTTP_201_CREATED)
async def set_cache_value(key: str, value: str, expire: int = 3600, redis_client: redis.Redis = Depends(get_redis)):
    """Ручка для установки значения в Redis"""
    if not redis_client:
        LOG.error("Не удалось получить значение из кэша. Redis недоступен")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Redis unvailable")
    await redis_client.set(key=key, value=value, ex=expire)
    return {"status": "added", "key": key, "expire": expire}

@app.delete("/cache/{key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cache_value(key: str, redis_client: redis.Redis = Depends(get_redis)):
    if not redis_client:
        LOG.error("Не удалось получить значение из кэша. Redis недоступен")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Redis unvailable")
    res = await redis_client.delete(key)
    return {"status": "deleted", "key": key, "affected": res}

        
@app.post("/digital_university/api/v1/auth")
async def auth():
    """auth logic"""
    pass


@app.get("/digital_university/api/v1/group/{group_id}/students", status_code=status.HTTP_200_OK)
async def get_students_by_group(group_id: int, db: AsyncSession = Depends(get_db)):
    students = await db.execute(select(Groups.students).where(Groups.id == group_id))
    students = students.scalar_one_or_none()
    if not students:
        raise HTTPException(404, "group_not_found")
    return students
    


@app.get("/digital_university/api/v1/professor/{professor_id}/students", status_code=status.HTTP_200_OK)
async def get_students_by_teacher(professor_id: int, db: AsyncSession = Depends(get_db)):
    groups = await db.execute(select(Professors.groups).where(Professors.id == professor_id))
    students_list = []

    for group_id in groups:
        students = await db.execute(select(Groups.students).where(Groups.id == group_id))
        students = list(students)
        students_list.extend(students)
    
    return students_list

@app.patch("/digital_university/api/v1/add/student/{student_id}/group/{group_id}", status_code=status.HTTP_200_OK)
async def add_student_to_group(student_id: int, group_id: int, db: AsyncSession = Depends(get_db)):
    students_list = await db.execute(select(Groups.students).where(Groups.id == group_id))
    students_list = list(students_list)
    students_list.append(student_id)
    await db.execute(
        update(Groups.students)
        .where(Groups.id == group_id)
        .values(students_list)
    )

    await db.commit()

@app.delete("/digital_university/api/v1/move/student/{student_id}/group/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student_from_group(student_id: int, group_id: int, db: AsyncSession = Depends(get_db)):
    students_list = await db.execute(select(Groups.students).where(Groups.id == group_id))
    students_list = list(students_list)
    students_list.remove(student_id)
    await db.execute(
        update(Groups.students)
        .where(Groups.id == group_id)
        .values(students_list)
    )

    await db.commit()

@app.get('/digital_university/api/v1/student/{student_id}/shedule', status_code=status.HTTP_200_OK)
async def get_achievements(student_id: int, db: AsyncSession = Depends(get_db)):
    achievements = await db.execute(
        select(Students.achievments)
        .where(Students.id == student_id)
    )

    return achievements

@app.get("/digital_university/api/v1/student/{student_id}/average_grade/")
async def get_average_grade(student_id: int, db: AsyncSession = Depends(get_db)):
    avg = await db.execute(select(Students.average_grade).where(Students.id == student_id))

    return avg

@app.get("/digital_university/api/v1/student/{student_id}")
async def get_student_by_id(student_id: int, db: AsyncSession = Depends(get_db)):
    student = await db.execute(select(Students).where(Students.id == student_id))
    student = student.scalar_one_or_none()
    if not student:
        raise HTTPException(404, "student not found")
    return student