from pydantic import BaseModel
from datetime import datetime

class Roles:
    STUDENT = "student" # студент
    ADMIN = "admin" # админ 
    UNI_STAFF = "uni_staff" # сотрудники 
    UNI_MANAGER_STAFF = "manager_staff" # руководящий персонал
    APPLICANT = "applicant" # абитуриент

# ROLES_LIST = (
#     STUDENT 
#     | ADMIN
#     | TEACHING_STAFF
#     | MANAGER_STAFF
#     | APPLICANT  
# )
class Permission(BaseModel):
    pass


class BaseUser(BaseModel):
    role: str
    permissions: list[Permission]
    name: str
    last_name: str
    is_bot: bool
    age: int | None
    username: str | None
    last_seen: int
    created_at: datetime

class StudentUser(BaseUser):
    pass

class AdminUser(BaseUser):
    pass

class TeacherStaffUser(BaseUser):
    pass

class ManagerStaffUser(BaseUser):
    pass

class ApplicantUser(BaseUser):
    pass

class AdminUser(BaseUser):
    pass