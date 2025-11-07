from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, ARRAY, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Subjects(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    subject_name = Column(String, nullable=False)
    department = Column(Integer, nullable=False)  # id факультета
    department_dean = Column(Integer, nullable=False)  # id декана факультета
    courses = Column(ARRAY(Integer), nullable=True)  # предполагается что может быть предмет который еще не введен в программу 
    
    grades = relationship("Grades", back_populates="owner")

class Students(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    last_name = Column(String, nullable=False) 
    birth_date = Column(DateTime, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_listed = Column(Boolean, default=True)  # числится в университете или отчислен 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    achievments = Column(ARRAY(String), nullable=True, default=None)
    has_scholarship = Column(Boolean, default=True)  # наличие стипендии
    in_dormitory = Column(Boolean, nullable=False)  # живет ли в общежитии
    course = Column(Integer, nullable=False)  # если отчислен - номер последнего пройденного курса
    group = Column(String, nullable=True) #  если отчислен - название группы в которой числился
    department = Column(String, nullable=False)  # кафедра
    achievments_points = Column(Integer, default=0)  # баллы за достижения
    average_grade = Column(Integer, default=None)
    societes = Column(ARRAY(String), nullable=True, default=None)  # в каких студенческих обществах состоит
    joined_at = Column(DateTime, default=func.now())  # дата поступления в УНИВЕРСИТЕТ!!
    skips_count = Column(Integer, nullable=False, default=0)  # количество пропусков
    visits_percent = Column(Float, nullable=False, default=100)  # процент посещаемости
    debts = Column(Integer, nullable=False, default=0)  # долги по учебе
    academic_vacation = Column(Boolean, default=False)  # в академе?
    academic_vacation_start = Column(DateTime, nullable=True, default=None)
    academic_vacation_end = Column(DateTime, nullable=True, default=None)
class Grades(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    group = Column(String, nullable=False) 
    course = Column(Integer, nullable=False)
    subject_name = Column(String, nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    grade = Column(Integer)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Professors(Base):
    __tablename__ = "professors"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    last_name = Column(String, nullable=False) 
    birth_date = Column(DateTime, nullable=False)
    hashed_password = Column(String, nullable=False)
    groups = Column(ARRAY(String))  # массив груп которые закреплены за преподом
    subjects = Column(ARRAY(String))  # массив дисциплин которые ведет препод
    post = Column(String, nullable=False)  # должность 
    joined_at = Column(DateTime, nullable=False)
    department = Column(Integer, nullable=False)  # id факультета


class Subjects(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    department = Column(Integer, nullable=False)  # id факультета
    teaching_staff = Column(ARRAY(String))  # пед состав

class Schedules(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    group = Column(String, nullable=True)
    monday1 = Column(ARRAY(String), default=None)
    tuesday1 = Column(ARRAY(String), default=None)
    wednesday1 = Column(ARRAY(String), default=None)
    thursday1 = Column(ARRAY(String), default=None)
    friday1 = Column(ARRAY(String), default=None)
    saturday1 = Column(ARRAY(String), default=None)
    sunday1 = Column(ARRAY(String), default=None)
    monday2 = Column(ARRAY(String), default=None)
    tuesday2 = Column(ARRAY(String), default=None)
    wednesday2 = Column(ARRAY(String), default=None)
    thursday2 = Column(ARRAY(String), default=None)
    friday2 = Column(ARRAY(String), default=None)
    saturday2 = Column(ARRAY(String), default=None)
    sunday2 = Column(ARRAY(String), default=None)

class Societies(Base):
    __tablename__ = "societies"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    people = Column(ARRAY(Integer), default=None)  # массив id людей состоящих в кружках

class Projects(Base):
    __tablename__ = "projects"

    
    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    people = Column(ARRAY(Integer), default=None)  # массив id участвующих в проекте

class Departments(Base):  # факультеты 
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)  # код направления, например 09.03.02 и тд
    dean = Column(Integer, nullable=False)  # id декана факультета
