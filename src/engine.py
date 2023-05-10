from src.db_manager import DBManager
from src.hh import HeadHunterAPI


class Engine(DBManager, HeadHunterAPI):
    def __init__(self):
        print("Привет, я помогу тебе найти вакансию по площадкам HeadHunter")
        super().__init__()
        self.menu = []
        self.employers = self.get_companies_and_vacancies_count()
        # self.db = DBManager()

    def create_menu(self):
        pass

    def engine_menu(self):
        """Меню действий в выбранном запросе вакансий"""
        text_menu_query = '11: "Вывести среднюю зарплату по всем вакансиям"\n' \
                          '12: "Вывести список всех вакансий, у которых зарплата выше средней"\n' \
                          '13: "Вывести список всех вакансий, в названии которых содержатся ваше ключевое слово"\n' \
                          '14: "Найти организацию на HH по ключевому слову"\n' \
                          '15: "Завершить сессию"\n'
        i = 1
        while True:
            print('*' * 100)
            # while True:
            for employer in self.employers:
                print(f'{i}: "{employer[0]}" Кол-во вакансий:{employer[1]}')
                i += 1
            print('*' * 100)
            print(text_menu_query)
            position_name = int(input("Введи номер:"))
            if position_name in range(1, len(self.employers) + 1):
                self.engine_submenu(self.employers[position_name - 1])
            elif position_name == 11:
                pass
            elif position_name == 12:
                pass
            elif position_name == 13:
                pass
            elif position_name == 14:
                if len(self.employers) != 10:
                    employer_name = input("Введи название организации:")
                    self.search_add_bd_employers(employer_name)
                else:
                    print("\nПревышен лимит. Не может быть больше 10 организаций. Удалите!!!\n")
            elif position_name == 15:
                break
            else:
                print("\nВведи цифру из списка")
            i = 1

    def engine_submenu(self, employer):
        """Подменю действий в выбранном запросе вакансий"""
        text_menu_query = '1: Вывести список всех вакансий\n' \
                          '2: Удалить данную организацию из списка\n' \
                          '3: Назад\n'
        while True:
            print(f'\n"{employer[0]}" Кол-во вакансий:{employer[1]}')
            print('*' * 100)
            print(text_menu_query)
            position_name = int(input("Введи номер:"))
            if position_name == 1:
                print('*' * 100)
                for vacancy in self.get_all_vacancies(employer[2]):
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
            elif position_name == 3:
                break
            else:
                print("Данного запроса нету. Повторите попытку")
            pass

    def search_add_bd_employers(self, name):
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
                                    f'Введите выбранную организацию для отслеживания вакансии: ')
            if point_employers.strip() == 'n':
                direction_point = True
                continue
            elif point_employers.strip() == 'b':
                direction_point = False
                continue
            else:
                hh_employer_vacancies = self.get_insert_vacancies(data_employers[int(point_employers) - 1]['id'])
                self.add_companies_and_vacancies(data_employers[int(point_employers) - 1], hh_employer_vacancies)
                # end_search = False
                break
        self.employers = self.get_companies_and_vacancies_count()
