import re
import requests
from utl.utils import check_salary


class HeadHunterAPI:

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
                hh_vacancy = self.get_experience_vacancy(vacancy['url'])
                salary_min = check_salary(hh_vacancy['salary']['from'])
                salary_max = check_salary(hh_vacancy['salary']['to'])
                if salary_min == 0:
                    salary_min = salary_max
                elif salary_max == 0:
                    salary_max = salary_min
                data_vacancies.append((hh_vacancy['id'],
                                       hh_vacancy['employer']['id'],
                                       hh_vacancy['name'],
                                       salary_min,
                                       salary_max,
                                       hh_vacancy['alternate_url'],
                                       ' '.join(re.sub(r'\<[^>]*\>', ' ', hh_vacancy['description']).split())
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
