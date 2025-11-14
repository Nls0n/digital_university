from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, insert
from sqlalchemy.exc import NoResultFound
from typing import Dict, Any
import redis.asyncio as redis
import json
import structlog
from datetime import datetime
from ..max_bot.bot import bot
from .database import (
    get_db,
    get_redis,
    init_redis,
    close_redis,
    close_engine,
    create_tables,
)
from .models import *
from .utils import get_cache_value, set_cache_value, delete_cached_value
from . import schemas
from .database import setup_database

LOG = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    LOG.info("Запуск приложения, создание таблиц в бд")
    try:
        setup_database()
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


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000",  # dev react/vue server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/cache/{key}")
async def get_cached_value(
    key: str,
    redis_client: redis.Redis = Depends(get_redis),
    status_code=status.HTTP_200_OK,
):
    """Ручка для получения кэшированных значений из Redis"""
    if not redis_client:
        LOG.error("Не удалось получить значение из кэша. Redis недоступен")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Redis unvailable"
        )
    value = redis_client.get(key)
    if value is None:
        LOG.error("Не удалось получить значение из кэша. Несуществующий ключ")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Value not found in cache"
        )
    return {"status": "accessed", "key": key, "value": value}


@app.post("/cache/{key}", status_code=status.HTTP_201_CREATED)
async def set_cached_value(
    key: str, body: schemas.CacheRequest, redis_client: redis.Redis = Depends(get_redis)
):
    """Ручка для установки значения в Redis"""
    if not redis_client:
        LOG.error("Не удалось записать значение в кэш. Redis недоступен")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Redis unvailable"
        )
    redis_client.set(name=key, value=body.value, ex=body.expire)
    return {"status": "added", "key": key, "expire": body.expire}


@app.delete("/cache/{key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cache_value(key: str, redis_client: redis.Redis = Depends(get_redis)):
    if not redis_client:
        LOG.error("Не удалось удалить значение из кэша. Redis недоступен")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Redis unvailable"
        )
    res = redis_client.delete(key)
    return {"status": "deleted", "key": key, "affected": res}


@app.get(
    "/digital_university/api/v1/schedule/student/{max_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ScheduleReponse,
)
async def get_schedule(
    max_id: int,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
):
    """Получить расписание по max_id"""
    url: str = f"/digital_university/api/v1/schedule/student/{max_id}"

    if redis_client:
        cached_schedule = get_cache_value(url, redis_client)
        if cached_schedule:
            return json.loads(cached_schedule)
    result = await db.execute(
        select(Schedules)
        .select_from(Students)
        .join(Schedules, Students.group == Schedules.group)
        .where(Students.max_id == max_id)
    )
    try:
        schedule = result.scalars().one()
    except NoResultFound:
        LOG.error(f"Schedule for max_id {max_id} not found")
        raise HTTPException(status_code=404, detail="Schedule not found")

    schedule_data = {
        "id": schedule.id,
        "group": schedule.group,
        "schedule_data": schedule.schedule_data,
    }

    if redis_client:
        set_cache_value(url, json.dumps(schedule_data), redis_client)

    return schedule_data

@app.post("/digital_university/api/v1/assign/{max_id}", status_code=status.HTTP_201_CREATED)
async def assign_user(max_id: int,
    db: AsyncSession = Depends(get_db),
):
  user = await db.execute(select(Users.max_id).where(Users.max_id == max_id))
  user = user.scalar_one_or_none()
  if user:
      raise HTTPException(404, "User already exists")
  await db.execute(insert(Users).values(max_id=max_id))
  await db.commit()
  return {"status": "added", "user_max_id": max_id}

@app.delete('/digital_university/api/v1/reset/{max_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    max_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        await db.execute(delete(Users).where(Users.max_id == max_id))
        await db.commit()
    except:
        pass
    try:
        await db.execute(delete(Professors).where(Professors.max_id == max_id))
        await db.commit()
    except:
        pass
    try:
        await db.execute(delete(Students).where(Students.max_id == max_id))
        await db.commit()
    except:
        pass
    try:
        await db.execute(delete(Applicants).where(Applicants.max_id == max_id))
        await db.commit()
    except:
        pass
@app.post("/digital_university/api/v1/assign/{max_id}/{role}", status_code=status.HTTP_201_CREATED)
async def assign_user_role(max_id: int,
    role: str,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
):
  role = role.lower()
  match role:
    case "student":
        db.execute(insert(Students).values(max_id=max_id))
        db.execute(insert(Users).values(role="student"))
        db.commit()
        return {"status": "added", "user_max_id": max_id, "role": role.lower()}
    case "professor":
        db.execute(insert(Professors).values(max_id=max_id))
        db.execute(insert(Users).values(role="professor"))
        db.commit()
        return {"status": "added", "user_max_id": max_id, "role": role.lower()}
    case "applicant":
        db.execute(insert(Applicants).values(max_id=max_id))
        db.execute(insert(Users).values(role="applicant"))
        db.commit()
        return {"status": "added", "user_max_id": max_id, "role": role.lower()}
          
  raise HTTPException(404, "role not found")

    

@app.get("/digital_university/api/v1/presense/{max_id}", status_code=status.HTTP_200_OK)
async def check_presense(
    max_id: int,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
):
    url = f"/digital_university/api/v1/presense/{max_id}"
    if redis_client:
        cached_schedule = get_cache_value(url, redis_client)
        if cached_schedule:
            return 1 == cached_schedule
    student_exists = await db.execute(
        select(Users.max_id).where(Users.max_id == max_id)
    )
    if student_exists.scalar_one_or_none():
        set_cache_value(url, 1, redis_client)
        return True
    set_cache_value(url, 0, redis_client)
    return False


@app.get(
    "/digital_university/api/v1/opendoordays/dates", status_code=status.HTTP_200_OK
)
async def get_door_opened_dates(
    db: AsyncSession = Depends(get_db), redis_client: redis.Redis = Depends(get_redis)
):
    url = f"/digital_university/api/v1/opendoordays/dates"

    if redis_client:
        dates = get_cache_value(url, redis_client)
        if dates:
            return json.loads(dates)
    try:
        result = await db.execute(select(OpenDoorDays.date))
        result = result.scalars().all()
    except NoResultFound:
        return []
    if result:
        set_cache_value(url, json.dumps(result), redis_client)

        return result
    return []


@app.put(
    "/digital_university/api/v1/opendoordays/{name}/student/{max_id}",
    status_code=status.HTTP_200_OK,
)
async def open_door_day_student_append(
    name: str, max_id: int, db: AsyncSession = Depends(get_db), redis_client: redis.Redis = Depends(get_redis)
):
    url = f"/digital_university/api/v1/opendoordays/{name}/student/{max_id}"
    students = await db.execute(
        select(OpenDoorDays.id).where(OpenDoorDays.name == name)
    )
    students = students.scalar_one_or_none()
    if not students:
        raise HTTPException(404, f"opendoorday with name {name} not found")
    students = await db.execute(
        select(OpenDoorDays.students).where(OpenDoorDays.name == name)
    )

    students = students.scalar_one_or_none()

    if not students:
        students = [max_id]
        await db.execute(
            update(OpenDoorDays)
            .where(OpenDoorDays.name == name)
            .values(students=students)
        )
        await db.commit()
        return {"status": "added", "students": students}
    if max_id in students:
        raise HTTPException(404, "Student already registered")
    students.append(max_id)
    await db.execute(
        update(OpenDoorDays).where(OpenDoorDays.name == name).values(students=students)
    )
    set_cache_value(
        f"/digital_university/api/v1/opendoordays/{name}/students", {"status": "added", "students": students},
        redis_client=redis_client
    )
    await db.commit()

    return {"status": "added", "students": students}


@app.delete(
    "/digital_university/api/v1/opendoordays/{name}/student/{max_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def open_door_day_student_remove(
    name: str,
    max_id: int,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
):
    url = f"/digital_university/api/v1/opendoordays/{name}/student/{max_id}"
    students = await db.execute(
        select(OpenDoorDays.id).where(OpenDoorDays.name == name)
    )
    students = students.scalar_one_or_none()
    if not students:
        raise HTTPException(404, f"opendoorday with name {name} not found")
    students = await db.execute(
        select(OpenDoorDays.students).where(OpenDoorDays.name == name)
    )

    students = list(students.scalar_one_or_none())
    try:
        students.remove(max_id)
    except Exception as e:
        raise HTTPException(404, "Check if there is a student, that you want to remove")
    await db.execute(
        update(OpenDoorDays).where(OpenDoorDays.name == name).values(students=students)
    )
    await db.commit()
    set_cache_value(
        f"/digital_university/api/v1/opendoordays/{name}/students",
        {"status": "removed", "students": students},
        redis_client,
    )
    return {"status": "removed", "students": students}


@app.get(
    "/digital_university/api/v1/opendoordays/{name}/students",
    status_code=status.HTTP_200_OK,
)
async def open_door_day_student_get(
    name: str,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
):
    url = f"/digital_university/api/v1/opendoordays/{name}/students"

    if redis_client:
        students = get_cache_value(url, redis_client)
        if students:
            return {"status": "added", "students": students[1:-1].split(", ")}
    students = await db.execute(
        select(OpenDoorDays.students).where(OpenDoorDays.name == name)
    )
    students = students.scalar_one_or_none()
    set_cache_value(url, students, redis_client=redis_client)
    return {"students": students}


@app.post("/digital_university/api/v1/statements/{max_id}/applicant", status_code=status.HTTP_201_CREATED)
async def create_statement(max_id: int, db: AsyncSession = Depends(get_db)):
    await db.execute(insert(Statements).values(status="Модерация", max_id=max_id, type="Заявление на поступление"))
    await db.commit()
    return {"success": True}

@app.get("/digital_university/api/v1/statements/{max_id}")
async def get_statements(
    max_id: int,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
):
    url = f"/digital_university/api/v1/statements/{max_id}"
    if redis_client:
        statements = get_cache_value(url, redis_client)
        if statements:
            return statements
    statements = await db.execute(select(Statements).where(Statements.max_id == max_id))
    statements = statements.scalars().all()
    if not statements:
        set_cache_value(url, [], redis_client)
        return []
    res = []
    for statement in statements:
        field = {"id": statement.id, "type": statement.type, "status": statement.status}
        res.append(field)

    return res


@app.get("digital_university/api/v1/statements/{statement_id}")
async def get_statement_status(
    statement_id: int,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
):
    url = f"digital_university/api/v1/statements/{statement_id}"

    if redis_client:
        status = get_cache_value(url, redis_client)
        if status:
            return status

    status = await db.execute(
        select(Statements.status).where(Statements.id == statement_id)
    )
    status = status.scalar_one_or_none()

    if status:
        return {"status": status}
    raise HTTPException(404, "No statement was found")


@app.put("digital_university/api/v1/statements/{statement_id}/{status}")
async def change_statement_status(
    statement_id: int,
    status: str,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
):
    url = f"digital_university/api/v1/statements/{statement_id}"

    await db.execute()


@app.post("/digital_university/api/v1/schedule/", status_code=status.HTTP_201_CREATED)
async def create_schedule(
    req: schemas.ScheduleRequest,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
):
    """Добавить расписание по группе"""
    result = await db.execute(select(Schedules).where(Schedules.group == req.group))
    existing_schedule = result.scalar_one_or_none()

    if existing_schedule:
        LOG.error(f"Schedule for group {req.group} already exists")
        raise HTTPException(
            status_code=400, detail="Schedule for this group already exists"
        )

    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(
            f"Object of type {obj.__class__.__name__} is not JSON serializable"
        )

    db_schedule = Schedules(
        group=req.group,
        schedule_data=json.loads(
            json.dumps(req.schedule.model_dump(), default=json_serializer)
        ),
    )
    db.add(db_schedule)
    await db.commit()
    await db.refresh(db_schedule)

    if redis_client:
        delete_cache_value(req.group, redis_client)

    LOG.info(f"Schedule created for group {req.group}")
    return {"status": "created", "schedule_id": db_schedule.id}


@app.put(
    "/digital_university/api/v1/schedule/group/{group_name}",
    status_code=status.HTTP_200_OK,
)
async def update_schedule(
    group_name: str,
    schedule_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
):
    """Изменить расписание по группе"""
    result = await db.execute(select(Schedules).where(Schedules.group == group_name))
    db_schedule = result.scalar_one_or_none()

    if not db_schedule:
        LOG.error(f"Schedule for group {group_name} not found")
        raise HTTPException(status_code=404, detail="Schedule not found")

    db_schedule.schedule_data = schedule_data
    await db.commit()
    await db.refresh(db_schedule)

    if redis_client:
        delete_cache_value(group_name, redis_client)

    LOG.info(f"Schedule updated for group {group_name}")
    return {"status": "updated", "schedule_id": db_schedule.id}


@app.get(
    "/digital_university/api/v1/projects",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ProjectsResponse,
)
async def get_projects(
    db: AsyncSession = Depends(get_db), redis_client: redis.Redis = Depends(get_redis)
):
    result = await db.execute(select(Projects.name))
    try:
        result = result.scalars().all()
    except:
        raise HTTPException(404, "no projects was found")
    if not result:
        return schemas.ProjectsResponse(projects=[])
    return schemas.ProjectsResponse(projects=result)


@app.delete(
    "/digital_university/api/v1/schedule/group/{group_name}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_schedule(group_name: str, db: AsyncSession = Depends(get_db)):
    """Удалить расписание по группе"""
    result = await db.execute(select(Schedules).where(Schedules.group == group_name))
    db_schedule = result.scalar_one_or_none()

    if not db_schedule:
        LOG.error(f"Schedule for group {group_name} not found")
        raise HTTPException(status_code=404, detail="Schedule not found")

    await db.delete(db_schedule)
    await db.commit()

    LOG.info(f"Schedule deleted for group {group_name}")


@app.get(
    "/digital_university/api/v1/group/{group_id}/students",
    status_code=status.HTTP_200_OK,
)
async def get_students_by_group(group_id: int, db: AsyncSession = Depends(get_db)):
    """Получить расписание по группе"""
    students = await db.execute(select(Groups.students).where(Groups.id == group_id))
    students = students.scalar_one_or_none()
    if not students:
        raise HTTPException(404, "group_not_found")
    return students


@app.get(
    "/digital_university/api/v1/professor/{professor_id}/students",
    status_code=status.HTTP_200_OK,
)
async def get_students_by_teacher(
    professor_id: int, db: AsyncSession = Depends(get_db)
):
    """Получить список студентов по преподавателю"""
    groups = await db.execute(
        select(Professors.groups).where(Professors.id == professor_id)
    )
    students_list = []
    groups = groups.scalar_one_or_none()
    if not groups:
        raise HTTPException(404, "professor not found")
    for group_id in groups:
        students = await db.execute(
            select(Groups.students).where(Groups.id == group_id)
        )
        students = list(students)
        students_list.extend(students)

    return students_list


@app.patch(
    "/digital_university/api/v1/add/student/{student_id}/group/{group_id}",
    status_code=status.HTTP_200_OK,
)
async def add_student_to_group(
    student_id: int, group_id: int, db: AsyncSession = Depends(get_db)
):
    """Добавить студента в группу"""
    students_list = await db.execute(
        select(Groups.students).where(Groups.id == group_id)
    )
    students_list = students_list.scalar_one_or_none()
    if not students_list:
        raise HTTPException(404, "group not found")
    is_valid_student = await db.execute(
        select(Students).where(Students.id == student_id)
    )
    is_valid_student = is_valid_student.scalar_one_or_none()
    if not is_valid_student:
        raise HTTPException(404, "student not found")
    students_list.append(student_id)
    await db.execute(
        update(Groups).where(Groups.id == group_id).values(students=students_list)
    )
    await db.commit()


@app.delete(
    "/digital_university/api/v1/move/student/{student_id}/group/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_student_from_group(
    student_id: int, group_id: int, db: AsyncSession = Depends(get_db)
):
    """Удалить студента из группы"""
    students_list = await db.execute(
        select(Groups.students).where(Groups.id == group_id)
    )
    students_list = students_list.scalar_one_or_none()
    if not students_list:
        raise HTTPException(404, "student not found")
    students_list.remove(student_id)
    await db.execute(
        update(Groups).where(Groups.id == group_id).values(students=students_list)
    )
    await db.commit()
@app.get("digital_university/api/v1/student/{max_id}/role")
async def get_role(max_id: int, db: AsyncSession = Depends(get_db), redis_client: redis.Redis = Depends(get_redis)):
    url =f"digital_university/api/v1/student/{max_id}/role"
    if redis_client:
        role = get_cache_value(url)
        if role:
            return {"role": role}
    role = await db.execute(select(Users.role).where(Users.max_id == max_id))
    role = role.scalar_one_or_none()
    if role:
        set_cache_value(url, {"role": role}, redis_client=redis_client)
        return {"role": role}
    
@app.get(
    "/digital_university/api/v1/student/{student_id}/grades",
    status_code=status.HTTP_200_OK,
)
async def get_student_grades(student_id: int, db: AsyncSession = Depends(get_db)):
    """Получить все оценки по student_id"""
    student_result = await db.execute(select(Students).where(Students.id == student_id))
    student = student_result.scalar_one_or_none()

    if not student:
        LOG.error(f"Student with id {student_id} not found")
        raise HTTPException(status_code=404, detail="Student not found")

    grades_result = await db.execute(
        select(Grades).where(Grades.student_id == student_id)
    )
    try:
        grades = grades_result.scalars().all()
    except:
        raise HTTPException(404, "no grades was found")

    return grades


@app.get("/digital_university/api/v1/student/{student_id}/grades/subject/{subject_id}")
async def get_student_grades_for_subject(
    student_id: int, subject_id: int, db: AsyncSession = Depends(get_db)
):
    """Получить оценки студента по предмету"""
    grades = await db.execute(
        select(Grades.grades).where(Grades.student_id == student_id)
    )
    grades = grades.scalar_one_or_none()
    if not grades:
        raise HTTPException(404, "student not found")

    subject_name = await db.execute(
        select(Subjects.name).where(Subjects.id == subject_id)
    )
    subject_name = subject_name.scalar_one_or_none()
    if not subject_name:
        raise HTTPException(404, "subject not found")

    subject_grades = grades.get(subject_name, [])
    return subject_grades


@app.patch(
    "/digital_university/api/v1/grades/{grade_id}", status_code=status.HTTP_200_OK
)
async def update_grade(
    grade_id: int, grades_update: Dict[str, Any], db: AsyncSession = Depends(get_db)
):
    """Изменение отдельной оценки по grade_id"""
    result = await db.execute(select(Grades).where(Grades.id == grade_id))
    db_grade = result.scalar_one_or_none()

    if not db_grade:
        LOG.error(f"Grade with id {grade_id} not found")
        raise HTTPException(status_code=404, detail="Grade not found")

    for key, value in grades_update.items():
        if hasattr(db_grade, key):
            setattr(db_grade, key, value)

    await db.commit()
    await db.refresh(db_grade)

    LOG.info(f"Grade {grade_id} updated successfully")
    return {"status": "updated", "grade_id": grade_id}


@app.post(
    "/digital_university/api/v1/group/{group_id}/tasks",
    status_code=status.HTTP_201_CREATED,
)
async def create_tasks_for_group(
    group_id: int,
    description: str,
    max_points: int,
    professor_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Добавление задания для всех учеников в группе"""
    group_result = await db.execute(select(Groups).where(Groups.id == group_id))
    group = group_result.scalar_one_or_none()

    if not group:
        LOG.error(f"Group with id {group_id} not found")
        raise HTTPException(status_code=404, detail="Group not found")

    professor_result = await db.execute(
        select(Professors).where(Professors.id == professor_id)
    )
    professor = professor_result.scalar_one_or_none()

    if not professor:
        LOG.error(f"Professor with id {professor_id} not found")
        raise HTTPException(status_code=404, detail="Professor not found")

    created_tasks = []
    for student_id in group.students:
        task = Tasks(
            description=description,
            max_points=max_points,
            student_points=0,
            student_id=student_id,
            professor_id=professor_id,
        )
        db.add(task)
        created_tasks.append({"student_id": student_id, "task_id": task.id})

    await db.commit()

    LOG.info(f"Created {len(created_tasks)} tasks for group {group_id}")
    return {
        "status": "created",
        "tasks_count": len(created_tasks),
        "tasks": created_tasks,
    }


@app.patch(
    "/digital_university/api/v1/tasks/{task_id}/grade", status_code=status.HTTP_200_OK
)
async def grade_task(
    task_id: int, student_points: int, db: AsyncSession = Depends(get_db)
):
    """Выставление оценки за работу по task_id"""
    result = await db.execute(select(Tasks).where(Tasks.id == task_id))
    db_task = result.scalar_one_or_none()

    if not db_task:
        LOG.error(f"Task with id {task_id} not found")
        raise HTTPException(status_code=404, detail="Task not found")

    if student_points > db_task.max_points:
        LOG.error(
            f"Student points {student_points} exceed max points {db_task.max_points}"
        )
        raise HTTPException(
            status_code=400, detail="Student points cannot exceed max points"
        )

    db_task.student_points = student_points
    await db.commit()
    await db.refresh(db_task)

    LOG.info(f"Task {task_id} graded with {student_points} points")
    return {"status": "graded", "task_id": task_id, "points": student_points}


@app.get(
    "/digital_university/api/v1/professor/{professor_id}/tasks",
    status_code=status.HTTP_200_OK,
)
async def get_professor_tasks(professor_id: int, db: AsyncSession = Depends(get_db)):
    """Получение всех заданий по professors.id"""
    result = await db.execute(select(Tasks).where(Tasks.professor_id == professor_id))
    try:
        tasks = result.scalars().all()
    except:
        raise HTTPException(404, "no tasks was found")
    return tasks


@app.get(
    "/digital_university/api/v1/student/{student_id}/tasks",
    status_code=status.HTTP_200_OK,
)
async def get_student_tasks(student_id: int, db: AsyncSession = Depends(get_db)):
    """Получение всех заданий по students.id"""
    student_result = await db.execute(select(Students).where(Students.id == student_id))
    student = student_result.scalar_one_or_none()

    if not student:
        LOG.error(f"Student with id {student_id} not found")
        raise HTTPException(status_code=404, detail="Student not found")

    result = await db.execute(select(Tasks).where(Tasks.student_id == student_id))
    try:
        tasks = result.scalars().all()
    except:
        raise HTTPException(404, "No tasks was found")
    return tasks


@app.get(
    "/digital_university/api/v1/student/{student_id}/achievments",
    status_code=status.HTTP_200_OK,
)
async def get_achievements(student_id: int, db: AsyncSession = Depends(get_db)):
    """Получение достижений студента по students.id"""
    achievements = await db.execute(
        select(Students.achievments).where(Students.id == student_id)
    )
    achievements = achievements.scalar_one_or_none()
    if not achievements:
        raise HTTPException(404, "student not found")
    return achievements


@app.get("/digital_university/api/v1/student/{student_id}/average_grade/")
async def get_average_grade(student_id: int, db: AsyncSession = Depends(get_db)):
    """Получение общего среднего балла по students.id"""
    avg = await db.execute(
        select(Students.average_grade).where(Students.id == student_id)
    )
    avg = avg.scalar_one_or_none()
    if not avg:
        raise HTTPException(404, "student not found")
    return avg


@app.get(
    "/digital_university/api/v1/student/{student_id}",
    response_model=schemas.StudentResponse,
)
async def get_student_by_id(student_id: int, db: AsyncSession = Depends(get_db)):
    """Получение данных о студенте по id"""
    student = await db.execute(select(Students).where(Students.id == student_id))
    student = student.scalar_one_or_none()
    if not student:
        raise HTTPException(404, "student not found")
    return student


@app.get(
    "/digital_university/api/v1/societes/student/{student_id}",
    response_model=schemas.SocietesResponse,
)
async def get_student_societies(student_id: int, db: AsyncSession = Depends(get_db)):
    """Получить список сообществ в которых состоит студент"""
    societies = await db.execute(
        select(Students.societes).where(Students.id == student_id)
    )
    societies = societies.scalar_one_or_none()
    if not societies:
        raise HTTPException(404, "student not found")
    return societies


@app.post("/digital_university/api/v1/societes/add")
async def add_student_to_society(name: str, last_name: str):
    pass


@app.get(
    "/digital_university/api/v1/student/{student_id}/subject/{subject_id}/average",
    status_code=status.HTTP_200_OK,
)
async def get_student_subject_average(
    student_id: int, subject_id: int, db: AsyncSession = Depends(get_db)
):
    """Получение среднего балла по предмету по students.id и subjects.id"""
    student_result = await db.execute(select(Students).where(Students.id == student_id))
    student = student_result.scalar_one_or_none()

    if not student:
        LOG.error(f"Student with id {student_id} not found")
        raise HTTPException(status_code=404, detail="Student not found")

    subject_result = await db.execute(select(Subjects).where(Subjects.id == subject_id))
    subject = subject_result.scalar_one_or_none()

    if not subject:
        LOG.error(f"Subject with id {subject_id} not found")
        raise HTTPException(status_code=404, detail="Subject not found")

    grades_result = await db.execute(
        select(Grades).where(Grades.student_id == student_id)
    )
    try:
        grades_records = grades_result.scalars().all()
    except:
        raise HTTPException(404, "No average grade was found")

    subject_grades = []
    subject_name = subject.name

    for grade_record in grades_records:
        if grade_record.grades and subject_name in grade_record.grades:
            subject_grades.append(grade_record.grades[subject_name])

    if not subject_grades:
        return {
            "student_id": student_id,
            "subject_id": subject_id,
            "average_grade": 0,
            "message": "No grades found for this subject",
        }

    average_grade = sum(subject_grades) / len(subject_grades)

    LOG.info(
        f"Calculated average grade {average_grade:.2f} for student {student_id} in subject {subject_id}"
    )
    return {
        "student_id": student_id,
        "subject_id": subject_id,
        "subject_name": subject_name,
        "average_grade": round(average_grade, 2),
        "grades_count": len(subject_grades),
    }
