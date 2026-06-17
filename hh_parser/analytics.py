import re
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from nltk.corpus import stopwords
from hh_parser.Db import SessionLocal, init_db
from hh_parser.DataService import DataService


def load_data_from_bd(db_service: DataService) -> pd.DataFrame:
    df = db_service.get_vacancies_df()
    df['salary'] = pd.to_numeric(df['salary'], errors='coerce')
    print(df['salary'])
    df.dropna(subset=['salary'], inplace=True)
    return df


def plot_salary_distribution(df: pd.DataFrame,show_plot=False):
    plt.figure(figsize=(12, 7))
    sns.histplot(x=df['salary'], bins=30, kde=True, color='skyblue')
    plt.title('Распределение зарплат: ')
    plt.xlabel('Зарплата')
    plt.ylabel('Кол-во вакансий')
    if show_plot:
        plt.show()
    else:
        plt.close()


def plot_depending_from_salary_experience(df: pd.DataFrame,show_plot=False):
    plt.figure(figsize=(12, 7))
    sns.boxplot(x='experience', y='salary', data=df.sort_values('experience'))
    plt.title('Распределение зарплат в зависимости от опыта работы')
    plt.xlabel('Опыт')
    plt.ylabel('Зарплата')
    plt.tight_layout()
    if show_plot:
        plt.show()
    else:
        plt.close()


def get_top_words_vacancy(df: pd.DataFrame, top_n=10):
    all_words = ''.join(df['description'].dropna()).lower()
    words = [word for word in re.findall(r'\b[a-zа-я]+\b', all_words) if len(word) > 2]
    stop_words = set(stopwords.words('russian') + stopwords.words('english'))
    words_without_stop = [word for word in words if word not in stop_words]

    return Counter(words_without_stop).most_common(top_n)
