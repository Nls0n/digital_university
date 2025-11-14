from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    ARRAY,
    Float,
)
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.sql import func
from .database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    max_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    username = Column(String, nullable=True)
    role = Column(String)
    phone_number = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class Subjects(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    name = Column(String, nullable=True)
    department = Column(Integer, nullable=True)  # id факультета
    department_dean = Column(Integer, nullable=True)  # id декана факультета
    type = Column(String, nullable=True)  # тип: зачет\диф зачет\экзамен
    courses = Column(
        ARRAY(Integer), nullable=True
    )  # предполагается что может быть предмет который еще не введен в программу


class Students(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    max_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    patronymic = Column(String, nullable=True)
    birth_date = Column(DateTime, nullable=True)
    hashed_password = Column(String, nullable=True)
    is_listed = Column(Boolean, default=True)  # числится в университете или отчислен
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    achievments = Column(ARRAY(String), nullable=True, default=None)
    has_scholarship = Column(Boolean, default=True)  # наличие стипендии
    in_dormitory = Column(Boolean, nullable=True)  # живет ли в общежитии
    course = Column(
        Integer, nullable=True
    )  # если отчислен - номер последнего пройденного курса
    group = Column(
        String, nullable=True
    )  #  если отчислен - id группы в которой числился
    department = Column(String, nullable=True)  # кафедра
    achievements_points = Column(Integer, default=0)  # баллы за достижения
    average_grade = Column(Integer, default=None)
    societes = Column(
        ARRAY(Integer), nullable=True, default=None
    )  # в каких студенческих обществах состоит (массив id)
    joined_at = Column(DateTime, default=func.now())  # дата поступления в УНИВЕРСИТЕТ!!
    skips_count = Column(Integer, nullable=True, default=0)  # количество пропусков
    visits_percent = Column(Float, nullable=True, default=100)  # процент посещаемости
    debts = Column(Integer, nullable=True, default=0)  # долги по учебе
    academic_vacation = Column(Boolean, default=False)  # в академе?
    academic_vacation_start = Column(DateTime, nullable=True, default=None)
    academic_vacation_end = Column(DateTime, nullable=True, default=None)
    roles = Column(ARRAY(String))  # роли юзера


class Grades(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    student_max_id = Column(Integer, ForeignKey("students.max_id"))
    group = Column(Integer, nullable=True)
    course = Column(Integer, nullable=True)
    grades = Column(JSONB)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Professors(Base):
    __tablename__ = "professors"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    max_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    patronymic = Column(String, nullable=True)
    birth_date = Column(DateTime, nullable=True)
    hashed_password = Column(String, nullable=True)
    groups = Column(ARRAY(String))  # массив груп которые закреплены за преподом
    subjects = Column(ARRAY(String))  # массив дисциплин которые ведет препод
    post = Column(String, nullable=True)  # должность
    joined_at = Column(DateTime, nullable=True)
    department = Column(Integer, nullable=True)  # id факультета
    roles = Column(ARRAY(String))  # роли юзера


class Schedules(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True)
    professor = Column(Integer)  # max_id
    group = Column(String, nullable=True)
    schedule_data = Column(JSONB)


class Projects(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    name = Column(String, nullable=True)
    people = Column(ARRAY(Integer), default=None)  # массив id участвующих в проекте


class Departments(Base):  # факультеты
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    name = Column(String, nullable=True)
    code = Column(
        String, nullable=True, primary_key=True, unique=True
    )  # код направления, например 09.03.02 и тд
    dean = Column(Integer, nullable=True)  # id декана факультета


class Groups(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    name = Column(String, nullable=True)
    course = Column(Integer, nullable=True)  # курс
    subjects = Column(ARRAY(Integer))  # предметы
    code = Column(
        String,
        nullable=True,
    )  # код направления, например 09.03.02 и тд
    tutor = Column(Integer)  # id старшего куратора группы
    young_tutor = Column(Integer)  # id младшего кураторы группы
    students = Column(ARRAY(Integer))  # массив id студентов
    elder = Column(Integer)  # id старосты группы


class Societies(Base):
    __tablename__ = "societes"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    name = Column(String, nullable=True)
    chairman = Column(Integer, ForeignKey("students.id"))  # председатель
    students = Column(ARRAY(Integer))


class Applicants(Base):
    __tablename__ = "applicants"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    max_id = Column(Integer, primary_key=True, unique=True, nullable=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True, unique=True)
    phone_number = Column(String, nullable=True, unique=True)
    patronymic = Column(String, nullable=True)  #
    insurance_policy = Column(String, nullable=True)  #  СНИЛС
    role = Column(String)  


class Tasks(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    description = Column(String)
    max_points = Column(Integer)
    student_points = Column(Integer)
    student_id = Column(Integer, ForeignKey("students.id"))
    professor_id = Column(Integer, ForeignKey("professors.id"))


class Roles(Base):
    __tablename__ = "roles"

    students = Column(ARRAY(Integer), primary_key=True)  # массив id студентов
    professors = Column(ARRAY(Integer))  # массив id преподавателей
    applicants = Column(ARRAY(Integer))  # массив id абитуриентов
    admins = Column(ARRAY(Integer))  # массив id админов


class OpenDoorDays(Base):
    __tablename__ = "opendoordays"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    name = Column(String, nullable=True)
    date = Column(String, nullable=True)
    students = Column(ARRAY(Integer))  # max_id


class Statements(Base):
    __tablename__ = "statements"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    max_id = Column(Integer, nullable=False)
    type = Column(String)
    status = Column(String, nullable=True)


class Guests(Base):
    __tablename__ = "guests"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    patronymic = Column(String, nullable=True)


class ProjectSuggestions(Base):
    __tablename__ = "projectsuggestions"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    max_id = Column(Integer)
    name = Column(String, nullable=True)
    description = Column(String, nullable=True)
