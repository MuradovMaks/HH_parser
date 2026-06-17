from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from hh_parser.VacancyModel import Base


username = 'bestuser'
password = 'bestuser'
host = '127.0.0.1:3306'
db_name = 'vacancies'

db_url = f'mysql+pymysql://{username}:{password}@{host}/{db_name}'

engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)
