from database import Base, engine
from dotenv import load_dotenv
import os 
from models import *

load_dotenv()


Base.metadata.create_all(bind=engine)

