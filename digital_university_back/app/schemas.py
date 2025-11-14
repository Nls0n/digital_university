from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Literal
from enum import StrEnum


class Roles(StrEnum):
    STUDENT = "student"  # студент
    ADMIN = "admin"  # админ
    UNI_STAFF = "uni_staff"  # сотрудники
    UNI_MANAGER_STAFF = "manager_staff"  # руководящий персонал
    APPLICANT = "applicant"  # абитуриент
    GUEST = "guest"  #  гость


# ROLES_LIST = (
#     STUDENT
#     | ADMIN
#     | TEACHING_STAFF
#     | MANAGER_STAFF
#     | APPLICANT
# )
class CacheRequest(BaseModel):
    value: str
    expire: int = 3600


class ScheduleReponse(BaseModel):
    id: int
    group: str
    schedule_data: dict


class ProjectsResponse(BaseModel):
    projects: list[str]


class Pair(BaseModel):
    subject: str
    professor: str
    audience: str
    start: datetime
    end: datetime


class Schedule(BaseModel):
    monday: list[Pair]
    tuesday: list[Pair]
    wednesday: list[Pair]
    thursday: list[Pair]
    friday: list[Pair]
    saturday: list[Pair]
    sunday: list[Pair]


class ScheduleRequest(BaseModel):
    group: str
    schedule: Schedule


class BaseUser(BaseModel):
    role: Literal[
        Roles.STUDENT,
        Roles.ADMIN,
        Roles.UNI_MANAGER_STAFF,
        Roles.UNI_STAFF,
        Roles.APPLICANT,
    ]
    permissions: list
    name: str
    last_name: str
    is_bot: bool
    age: int | None
    email: EmailStr
    created_at: datetime


class StudentResponse(BaseUser):
    avg_grade: int
    schedule: list[str]
    academic_vacation: bool
    academic_vacation_start: datetime
    academic_vacation_end: datetime
    has_scholarship: bool
    in_dormitory: bool
    debts: int
    skips_count: int
    achievements_points: int
    visit_percent: float
    group: int


class ProfessorUserResponse(BaseUser):
    name: str
    last_name: str
    groups: list[int]
    department: int


class SocietesResponse(BaseModel):
    societes_list: list[int]


class ManagerStaffUser(BaseUser):
    pass


class ApplicantUser(BaseUser):
    pass


class AdminUser(BaseUser):
    pass
