
import pandas as pd
from sqlalchemy import  insert
from sqlalchemy.dialects.mysql import insert
from sqlalchemy import select
from hh_parser.VacancyModel import Vacancy, VacancySchema


class DataService:
    def __init__(self, session):
        self.session = session

    def get_vacancies(self):
        return self.session.query(Vacancy).all()

    def get_vacancies_df(self):
        vacancies = select(Vacancy)
        return pd.read_sql(vacancies, self.session.bind)

    def create_vacancy(self, **kwargs):
        validate_vacancy = VacancySchema(**kwargs)
        val_dic = validate_vacancy.model_dump()

        value = insert(Vacancy).values(val_dic)
        nondup_values = value.on_duplicate_key_update(id=value.inserted.id)

        self.session.execute(nondup_values)
        self.session.commit()
        return val_dic
