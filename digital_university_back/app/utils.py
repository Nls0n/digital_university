from datetime import datetime
import json
import asyncpg
import structlog
import redis.asyncio as redis
from typing import Optional, Dict, Any, Literal

LOG = structlog.get_logger()

def get_cache_value(key: str, redis_client: redis.Redis) -> Optional[Dict]:
    """Получить значение из кэша"""
    try:
        cached = redis_client.get(key)
        if cached:
            LOG.info(f"get cached value from {key}, - {cached}")
            return cached
    except Exception as e:
        LOG.error(f"Error getting value from cache: {str(e)}")
    LOG.error(f"Error getting value from cache for key {key}")
    return None

def set_cache_value(key: str, value: Any, redis_client: redis.Redis):
    """Сохранить значение в кэш"""
    try:
        if type(value) is list:
            redis_client.setex(
            key,
            3600,
            json.dumps(value).encode("utf-8")
        )
        redis_client.setex(
            key,
            3600,
            value
        )
        LOG.info(f"Value for key {key} cached successfully")
    except Exception as e:
        LOG.error(f"Error caching value: {str(e)}")

async def delete_cached_value(key: str, redis_client: redis.Redis):
    """Удалить значение из кэша"""
    try:
        await redis_client.delete(key)
        LOG.info(f"Value deleted for key {key}")
    except Exception as e:
        LOG.error(f"Error invalidating value from cache: {str(e)}")


class Task:
    def __init__(self, name: str, max_points: int, description: str, deadline: datetime, student_id: int, subject_id: int):
        self._name = name
        self._max_points = max_points
        self._description = description
        self._deadline = deadline
        self._student_id = student_id
        self._subject_id = subject_id
        self._student_points: float = None
    
    @property
    def student_points(self, value: float):
        self._student_points = value
    
    @property
    def deadline(self, value: datetime):
        self._deadline = value
class GradesJSONConstructor:
    def __init__(self):
        self._grades: dict[str, dict[int, int]] = {}
        self._student_id: int = 0
        self._tasks: list[Task] = []
        
    @property
    def assign_student(self, value: int):
        self._student_id = value
        
    def make_json_report(self):
        grades = {}
        for index, task in enumerate(self._tasks, start=1):
            grades[f"task_{index}"] = {
            "subject_id": task._subject_id,
            "task": {
                    "description": task._description,
                    "max_points": task._max_points,
                    "student_id": task._student_id,
                    "student_points": task._student_points,
                    "deadline": task._deadline,
                }
            }
        return json.dumps(grades)
    
class DatabaseIdEncoder:
    def __init__(
            self,
            student_id: int | None = None,
            society_id: int | None = None,
            task_id: int | None = None,
            professor_id: int | None = None,
            subject_id: int | None = None,
            group_id: int | None = None,
            grade_id: int | None = None,
            department_id: int | None = None
    ):
        self._student_id: int | None = student_id
        self._society_id: int | None = society_id
        self._task_id: int | None = task_id
        self._professor_id: int | None = professor_id
        self._subject_id: int | None = subject_id
        self._group_id: int | None = group_id
        self._grade_id: int | None = grade_id
        self._department_id: int | None = department_id
    
    
