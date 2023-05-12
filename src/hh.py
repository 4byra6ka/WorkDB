import re
import requests
from utl.utils import check_salary


class HeadHunterAPI:

    def __init__(self):
        self.currency_rate = self.get_api_cbr()

    @staticmethod
    def get_api_cbr():
        """загрузка курса валют"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
        }
        url = f"https://www.cbr-xml-daily.ru/daily_json.js"
        cbr_request = requests.get(url=url, headers=headers)
        if cbr_request.status_code != 200:
            raise NameError(f"Удаленный сервер не отвечает {cbr_request.status_code}")
        return cbr_request.json()['Valute']

    @staticmethod
    def get_api_hh(search, text_url="employers"):
        """ Формирование запроса на HeadHunter"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
        }
        url = f"https://api.hh.ru/" + text_url
        hh_request = requests.get(url=url, headers=headers, params=search)
        if hh_request.status_code != 200:
            raise NameError(f"Удаленный сервер не отвечает {hh_request.status_code}")
        return hh_request.json()

    def get_search_employers(self, employer: str):
        """Поиск организации на HH"""
        search = {
            'text': employer,
            'per_page': 100,
            'only_with_vacancies': True,
            'page': 0
        }
        # end_page = True
        data_employers = []
        while True:
            hh_employers = self.get_api_hh(search)
            for employer in hh_employers['items']:
                data_employers.append({
                    'id': employer['id'],
                    'name': employer['name']
                })
            if hh_employers['page'] + 1 < hh_employers['pages']:
                search['page'] += 1
            else:
                break
        return data_employers

    def get_insert_vacancies(self, employer_id: int):
        """Поиск вакансий на HH"""
        data_vacancies = []
        search = {'employer_id': employer_id,
                  'per_page': 100,
                  'only_with_salary': True,
                  'page': 0}
        while True:
            hh_vacancies = self.get_api_hh(search, 'vacancies')
            for vacancy in hh_vacancies['items']:
                salary_min = check_salary(vacancy['salary']['from'])
                salary_max = check_salary(vacancy['salary']['to'])
                if salary_min == 0:
                    salary_min = salary_max
                elif salary_max == 0:
                    salary_max = salary_min
                if vacancy['salary']['currency'] != 'RUR':
                    salary_min = int((salary_min * self.currency_rate[vacancy['salary']['currency']]['Value']) / self.currency_rate[vacancy['salary']['currency']]['Nominal'])
                    salary_max = int((salary_max * self.currency_rate[vacancy['salary']['currency']]['Value']) / self.currency_rate[vacancy['salary']['currency']]['Nominal'])
                data_vacancies.append((vacancy['id'],
                                       vacancy['employer']['id'],
                                       vacancy['name'],
                                       salary_min,
                                       salary_max,
                                       vacancy['alternate_url'],
                                       str(vacancy['snippet']['requirement']) +
                                       str(vacancy['snippet']['responsibility'])
                                       ))
            if hh_vacancies['page'] + 1 < hh_vacancies['pages']:
                search['page'] += 1
            else:
                break
        return data_vacancies

    @staticmethod
    def get_experience_vacancy(url_vacancy):
        """
        Запрос вакансии страницы для HH в json формате. При большом количестве запросов возможно блокировка по DDos
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'}
        hh_request = requests.get(url=url_vacancy, headers=headers)
        if hh_request.status_code != 200:
            raise NameError(f"Удаленный сервер не отвечает {hh_request.status_code}")
        return hh_request.json()
