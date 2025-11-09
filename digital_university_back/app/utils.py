from datetime import datetime
import json
import asyncpg
import structlog
import redis.asyncio as redis
from typing import Optional, Dict

LOG = structlog.get_logger()

async def get_cached_schedule(group_name: str, redis_client: redis.Redis) -> Optional[Dict]:
    """Получить расписание из кэша"""
    try:
        cached = await redis_client.get(f"schedule:{group_name}")
        if cached:
            LOG.info(f"Schedule for group {group_name} found in cache")
            return json.loads(cached)
    except Exception as e:
        LOG.error(f"Error getting schedule from cache: {str(e)}")
    return None

async def set_cached_schedule(group_name: str, schedule_data: Dict, redis_client: redis.Redis):
    """Сохранить расписание в кэш"""
    try:
        await redis_client.setex(
            f"schedule:{group_name}",
            3600,
            json.dumps(schedule_data)
        )
        LOG.info(f"Schedule for group {group_name} cached successfully")
    except Exception as e:
        LOG.error(f"Error caching schedule: {str(e)}")

async def invalidate_schedule_cache(group_name: str, redis_client: redis.Redis):
    """Удалить расписание из кэша"""
    try:
        await redis_client.delete(f"schedule:{group_name}")
        LOG.info(f"Schedule cache invalidated for group {group_name}")
    except Exception as e:
        LOG.error(f"Error invalidating schedule cache: {str(e)}")


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
    
    
