from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Text, String
from pydantic import BaseModel, field_validator
from typing import Optional

Base = declarative_base()


class Vacancy(Base):
    __tablename__ = 'Vacancies'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    experience = Column(String(255), nullable=True)
    employment = Column(String(255), nullable=True)
    working_hours = Column(String(255), nullable=True)
    work_format = Column(String(255), nullable=True)
    salary = Column(String(255), nullable=True)


class VacancySchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    experience: Optional[str] = None
    work_format: Optional[str] = None
    working_hours: Optional[str] = None
    employment: Optional[str] = None
    salary: Optional[str] = None

    @field_validator('description', 'experience', 'work_format', 'working_hours', 'employment', mode='before')
    @classmethod
    def empty_string_to_none(cls, value):
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        else:
            return value
