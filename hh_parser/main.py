import argparse
from hh_parser.DataService import DataService
from hh_parser.Db import init_db, SessionLocal
from hh_parser.analytics import (
    load_data_from_bd,
    plot_salary_distribution,
    plot_depending_from_salary_experience,
    get_top_words_vacancy
)
from hh_parser.parser import Parser

init_db()
session = SessionLocal()
service = DataService(session)


def build_args():
    p = argparse.ArgumentParser(description="HH парсер и анализатор")
    p.add_argument('-q', '--query', type=str, default='ML Engineer AND NLP', help='Текст запроса')
    p.add_argument('-n', '--items', type=int, default=50, help='Вакансий на страницу')
    p.add_argument('--show-plot', action='store_true', help='Показать график после парсинга')
    p.add_argument('--only-analyze', action='store_true', help='Только анализ без парсинга')
    return p.parse_args()


def analys(show_plot:bool):
    df_vacancies = load_data_from_bd(service)
    print(f'Кол-во вакансий:{len(df_vacancies)}')
    print('График распределения ЗП и кол-во вакансий: ')
    plot_salary_distribution(df_vacancies,show_plot=show_plot)
    print('График распределения Зп от Опыта')
    plot_depending_from_salary_experience(df_vacancies,show_plot=show_plot)
    print(f'Топ-10 самых часто встречающихся слов в описании вакансии: {get_top_words_vacancy(df_vacancies)}')
    print("\nСредняя зарплата:", df_vacancies['salary'].mean())
    print("Медианная зарплата:", df_vacancies['salary'].median())


def main():
    args = build_args()
    base_url = "https://moscow.hh.ru/search/vacancy"
    params = {
        'text': args.query,
        'items_on_page': args.items,
        'label': 'with_salary'


    }
    # Создаем словарь с заголовками. Мы говорим серверу, что мы — обычный Chrome на Windows
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.1 Safari/537.36'
    }

    pars = Parser(base_url, headers=headers, params=params, db_service=service)
    result = pars.parse()
    print(f'Успешно собранных вакансий: {len(result)}')
    if result:
        print(f'Пример вакансии: {result[0]}')

    analys(show_plot=args.show_plot)


if __name__ == '__main__':
    main()

