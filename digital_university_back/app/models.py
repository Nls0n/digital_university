from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, ARRAY, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Subjects(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    department = Column(Integer, nullable=False)  # id факультета
    department_dean = Column(Integer, nullable=False)  # id декана факультета
    courses = Column(ARRAY(Integer), nullable=True)  # предполагается что может быть предмет который еще не введен в программу 
    

class Students(Base):
    __tablename__ = "students"

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
    group = Column(Integer, nullable=True) #  если отчислен - id группы в которой числился
    department = Column(String, nullable=False)  # кафедра
    achievements_points = Column(Integer, default=0)  # баллы за достижения
    average_grade = Column(Integer, default=None)
    societes = Column(ARRAY(Integer),nullable=True, default=None)  # в каких студенческих обществах состоит (массив id)
    joined_at = Column(DateTime, default=func.now())  # дата поступления в УНИВЕРСИТЕТ!!
    skips_count = Column(Integer, nullable=False, default=0)  # количество пропусков
    visits_percent = Column(Float, nullable=False, default=100)  # процент посещаемости
    debts = Column(Integer, nullable=False, default=0)  # долги по учебе
    academic_vacation = Column(Boolean, default=False)  # в академе?
    academic_vacation_start = Column(DateTime, nullable=True, default=None)
    academic_vacation_end = Column(DateTime, nullable=True, default=None)
    role = Column(String, nullable=False)
class Grades(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    group = Column(Integer, nullable=False) 
    course = Column(Integer, nullable=False)
    grades = Column(JSON)
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
    role = Column(String, nullable=False)



class Schedules(Base):
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True)
    group = Column(String, nullable=True)
    schedule_data = Column(JSON)  

class Projects(Base):
    __tablename__ = "projects"

    
    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    people = Column(ARRAY(Integer), default=None)  # массив id участвующих в проекте

class Departments(Base):  # факультеты 
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False, primary_key=True, unique=True)  # код направления, например 09.03.02 и тд
    dean = Column(Integer, nullable=False)  # id декана факультета

class Groups(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False,)  # код направления, например 09.03.02 и тд
    tutor = Column(Integer)  # id старшего куратора группы
    young_tutor = Column(Integer)  # id младшего кураторы группы
    students = Column(ARRAY(Integer))  # массив id студентов
    elder = Column(Integer)  # id старосты группы  
    
class Societies(Base):
    __tablename__ = "societes"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    chairman = Column(Integer, ForeignKey("students.id"))  # председатель
    students = Column(ARRAY(Integer)) 

class Applicants(Base):
    __tablename__ = "applicants"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone_number = Column(String, nullable=False, unique=True)

class Tasks(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    description = Column(String)
    max_points = Column(Integer)
    student_points = Column(Integer)
    student_id = Column(Integer, ForeignKey("students.id"))
    professor_id = Column(Integer, ForeignKey("professors.id"))
