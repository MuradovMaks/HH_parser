import re
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from typing import List, Optional, Dict
from hh_parser.DataService import DataService
from hh_parser.selector import pages_quantity, title, work_experience, description, hours_quantity, working_hours, work_format, \
    link, cards_of_vacancy, salary

SALARY_RE = re.compile(r"(\d[\d\s\u00A0]*)", re.UNICODE)


def safe_get_text(soup_obj, selector, split_by=None) -> str:
    element = soup_obj.find(attrs=selector)
    if not element:
        return "Не указано"
    if selector is salary:
        pure_salary = SALARY_RE.findall(element.getText().strip())
        if len(pure_salary) == 1:
            return str(int(re.sub(r"\D+", "", pure_salary[0])))
        else:
            avg = (int(re.sub(r"\D+", "", pure_salary[0])) + (int(re.sub(r"\D+", "", pure_salary[1])))) / 2
            return str(avg)

    text = element.getText().strip()
    if split_by and split_by in text:
        return text.split(split_by)[1].strip()
    return text


class Parser:
    def __init__(self, base_url: str, params: dict, headers: dict, db_service: DataService):
        self.base_url = base_url
        self.headers = headers
        self.db_service = db_service
        self.params = params

    def _get_soup(self, url: str, params: Optional[dict] = None) -> Optional[BeautifulSoup]:
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()

            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f'Ошибка при запросе к {url} + {e}')
            return None

    def get_pages_count(self):
        soup = self._get_soup(self.base_url, params=self.params)
        if not soup:
            return 0
        else:
            pages = soup.find_all(attrs=pages_quantity)
            return len(pages)

    def parse(self) -> List[Dict]:
        pages = self.get_pages_count()
        all_vacancies = []
        if pages is not None:
            page_params = self.params.copy()

            for i in tqdm(range(pages + 1)):
                page_params['page'] = i
                response_of_page = self._get_soup(f'{self.base_url}', params=page_params)
                cards = response_of_page.find_all(attrs=cards_of_vacancy)
                if cards is not None:
                    try:

                        for _ in tqdm(range(len(cards))):
                            link_tag = cards[_].find(attrs=link)
                            if not link_tag:
                                continue

                            href = link_tag.get('href')
                            response_of_description = self._get_soup(href)
                            id = cards[_].find('div', class_='vacancy-card--n77Dj8TY8VIUF0yM font-inter').get('id')
                            vacancy_data = {
                                'id': id,
                                'name': safe_get_text(response_of_description, title),
                                'description': safe_get_text(response_of_description, description),
                                'salary': safe_get_text(response_of_description, salary),
                                'experience': safe_get_text(response_of_description, work_experience, split_by=":"),
                                'employment': safe_get_text(response_of_description, hours_quantity, split_by=":"),
                                "working_hours": safe_get_text(response_of_description, working_hours, split_by=":"),
                                "work_format": safe_get_text(response_of_description, work_format, split_by=":")

                            }

                            self.db_service.create_vacancy(**vacancy_data)
                            all_vacancies.append(vacancy_data)
                    except Exception as e:
                        print(f'Ошибка при обработке вакансии: {e}')
                        continue

        return all_vacancies
