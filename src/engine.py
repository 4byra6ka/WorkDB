from src.db_manager import DBManager
from src.hh import HeadHunterAPI


class Engine(DBManager, HeadHunterAPI):
    def __init__(self):
        print("Привет, я помогу тебе найти вакансию по площадкам HeadHunter")
        super().__init__()
        self.menu = []
        self.employers = self.get_companies_and_vacancies_count()

    def engine_menu(self):
        """Меню действий в выбранном запросе вакансий"""
        text_menu_first = ["Добавить организацию и вакансии с HH в БД", "Завершить сессию"]
        text_menu_second = ["Добавить организацию и вакансии с HH в БД", "Вывести среднюю зарплату по всем вакансиям",
                            "Вывести список всех вакансий, у которых зарплата выше средней",
                            "Вывести список всех вакансий, в названии которых содержатся ваше ключевое слово",
                            "Вывести список всех вакансий", "Завершить сессию"]
        while True:
            position_menu = 1
            if len(self.employers) > 0:
                print('*' * 100)
                for employer in self.employers:
                    print(f'{position_menu}: "{employer[0]}" Кол-во вакансий:{employer[1]}')
                    position_menu += 1
                print('*' * 100)
                for menu_second in text_menu_second:
                    print(f'{position_menu}: {menu_second}')
                    position_menu += 1
            else:
                print('*' * 100)
                for menu_first in text_menu_first:
                    print(f'{position_menu}: {menu_first}')
                    position_menu += 1
                print('*' * 100)
            position_name = int(input("Введи номер:"))
            if position_name in range(1, len(self.employers) + 1):
                self.engine_submenu(self.employers[position_name - 1])
            elif position_name == len(self.employers) + 1:
                if len(self.employers) != 10:
                    employer_name = input("Введи название организации:")
                    self.search_add_bd_employers(employer_name)
                else:
                    print("\nПревышен лимит. Не может быть больше 10 организаций. Удалите!!!\n")
            elif position_name == len(self.employers) + 2 and len(self.employers) > 0:
                print('*' * 100)
                for vacancy in self.get_avg_salary():
                    print(f"Организация:{vacancy[0]}, Должность:{vacancy[1]}, Зарплата {vacancy[2]}₽, "
                          f"Ссылка на вакансию:{vacancy[3]}")
                    print('*' * 100)
                continue
            elif position_name == len(self.employers) + 3 and len(self.employers) > 0:
                print('*' * 100)
                for vacancy in self.get_vacancies_with_higher_salary():
                    if vacancy[2] == vacancy[3]:
                        salary = f" {vacancy[2]}₽"
                    else:
                        salary = f" от {vacancy[2]}₽ до {vacancy[3]}₽"
                    print(f"Организация:{vacancy[0]}, Должность:{vacancy[1]}, Зарплата{salary}, "
                          f"Ссылка на вакансию:{vacancy[4]}")
                    print('*' * 100)
                continue
            elif position_name == len(self.employers) + 4 and len(self.employers) > 0:
                word = input("Введи слово для поиска подходящих вакансий:")
                print('*' * 100)
                for vacancy in self.get_vacancies_with_keyword(word):
                    if vacancy[2] == vacancy[3]:
                        salary = f" {vacancy[2]}₽"
                    else:
                        salary = f" от {vacancy[2]}₽ до {vacancy[3]}₽"
                    print(f"Организация:{vacancy[0]}, Должность:{vacancy[1]}, Зарплата{salary}, "
                          f"Ссылка на вакансию:{vacancy[4]}")
                    print('*' * 100)
                continue
            elif position_name == len(self.employers) + 5 and len(self.employers) > 0:
                print('*' * 100)
                for vacancy in self.get_all_vacancies():
                    if vacancy[2] == vacancy[3]:
                        salary = f" {vacancy[2]}₽"
                    else:
                        salary = f" от {vacancy[2]}₽ до {vacancy[3]}₽"
                    print(f"Организация:{vacancy[0]}, Должность:{vacancy[1]}, Зарплата{salary}, "
                          f"Ссылка на вакансию:{vacancy[4]}")
                    print('*' * 100)
                continue
            elif (position_name == len(self.employers) + 6 and len(self.employers) > 0) or \
                    (position_name == len(self.employers) + 2 and len(self.employers) == 0):
                break
            else:
                print("\nВведи цифру из списка")

    def engine_submenu(self, employer):
        """Подменю действий в выбранном запросе вакансий"""
        text_menu_query = '1: Вывести список всех вакансий данной организации\n' \
                          '2: Удалить данную организацию из списка\n' \
                          '3: Назад\n'
        while True:
            print(f'\n"{employer[0]}" Кол-во вакансий:{employer[1]}')
            print('*' * 100)
            print(text_menu_query)
            position_name = int(input("Введи номер:"))
            if position_name == 1:
                print('*' * 100)
                for vacancy in self.get_one_employer_all_vacancies(employer[2]):
                    if vacancy[2] == vacancy[3]:
                        salary = f" {vacancy[2]}₽"
                    else:
                        salary = f" от {vacancy[2]}₽ до {vacancy[3]}₽"
                    print(f"Организация:{vacancy[0]}, Должность:{vacancy[1]}, Зарплата{salary}, "
                          f"Ссылка на вакансию:{vacancy[4]}")
                    print('*' * 100)
                continue
            elif position_name == 2:
                self.del_companies_and_vacancies(employer[2])
                self.employers = self.get_companies_and_vacancies_count()
                break
            elif position_name == 3:
                break
            else:
                print("Данного запроса нету. Повторите попытку")
            pass

    def search_add_bd_employers(self, name):
        """Меню для выбора организации"""
        data_employers = self.get_search_employers(name)
        i = 0
        end_search = True
        direction_point = True  # False - назад, True - вперёд
        course_point = 0
        while end_search:
            print(f'Найдено по вашему запросу {len(data_employers)} организаций')
            while True:
                if i < 20 and direction_point and 0 <= course_point < len(data_employers):
                    print(f'{course_point + 1}: {data_employers[course_point]["name"]}')
                    i += 1
                    if not course_point == len(data_employers) - 1:
                        course_point += 1
                    else:
                        i = 0
                        break
                elif i < 20 and not direction_point and 0 <= course_point < len(data_employers):
                    print(f'{course_point + 1}: {data_employers[course_point]["name"]}')
                    i += 1
                    if not course_point == 0:
                        course_point -= 1
                    else:
                        i = 0
                        break
                else:
                    i = 0
                    break
            point_employers = input(f'n - посмотреть следующие 20 компаний\nb - посмотреть предыдущие 20 компаний\n'
                                    f'q - назад в меню\n'
                                    f'Введите выбранную организацию для отслеживания вакансии: ')
            try:
                if point_employers.strip() == 'n':
                    direction_point = True
                    continue
                elif point_employers.strip() == 'b':
                    direction_point = False
                    continue
                elif point_employers.strip() == 'q':
                    break
                else:
                    hh_employer_vacancies = self.get_insert_vacancies(data_employers[int(point_employers) - 1]['id'])
                    self.add_companies_and_vacancies(data_employers[int(point_employers) - 1], hh_employer_vacancies)
                    # end_search = False
                    break
            except:
                print("\nВведи цифру или букву из списка")
                course_point = 0

        self.employers = self.get_companies_and_vacancies_count()
