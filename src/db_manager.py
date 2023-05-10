from utl.utils import config
import psycopg2


class DBManager:

    def __init__(self):
        self.db_name = "hh"
        self.params = config()
        self.check_create_database(config())

    def check_create_database(self, params: dict):
        """Проверка и создание базы данных и таблиц для сохранения данных"""
        conn = psycopg2.connect(dbname='postgres', **params)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(f"SELECT EXISTS (SELECT * FROM pg_database where datname = '{self.db_name}')")
        if not cur.fetchone()[0]:
            cur.execute(f"CREATE DATABASE {self.db_name}")
        conn.close()

        conn = psycopg2.connect(dbname=self.db_name, **params)
        cur = conn.cursor()
        cur.execute(f"SELECT EXISTS (SELECT * FROM pg_tables WHERE tablename = 'employers')")
        if not cur.fetchone()[0]:
            with conn.cursor() as cur:
                cur.execute("""
                        CREATE TABLE public.employers (
                            id int,
                            name varchar(200) NOT NULL,
                            CONSTRAINT pk_public_employers_id PRIMARY KEY (id))
                        """)
        conn.commit()
        cur = conn.cursor()
        cur.execute(f"SELECT EXISTS (SELECT * FROM pg_tables WHERE tablename = 'vacancies')")
        if not cur.fetchone()[0]:
            with conn.cursor() as cur:
                cur.execute("""
                        CREATE TABLE public.vacancies (
                            id int,
                            employer_id int,
                            name varchar(100) NOT NULL,
                            salary_from int NOT NULL,
                            salary_to int NOT NULL,
                            url varchar(255) NOT NULL,
                            description text,
                            CONSTRAINT pk_vacancies PRIMARY KEY (id),
                            CONSTRAINT fk_employers_vacancies FOREIGN KEY(employer_id) REFERENCES public.employers(id))
                        """)

        conn.commit()
        conn.close()

    def add_companies_and_vacancies(self, employer_data: dict, vacancies_data: list):
        with psycopg2.connect(dbname=self.db_name, **self.params) as connection:
            with connection.cursor() as cur:
                cur.execute('INSERT INTO public.employers VALUES (%s, %s)', (employer_data['id'], employer_data['name'])
                            )
                cur.executemany('INSERT INTO public.vacancies VALUES (%s, %s, %s, %s, %s, %s, %s)', vacancies_data)

    def get_companies_and_vacancies_count(self):
        """Получает список всех компаний и количество вакансий у каждой компании"""
        conn = psycopg2.connect(dbname=self.db_name, **self.params)
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT employers.name, COUNT(*), employers.id "
                                "FROM employers "
                                "join vacancies ON employers.id = vacancies.employer_id "
                                "GROUP BY employers.name, employers.id "
                                "ORDER BY COUNT(employers.name) DESC")
                    return cur.fetchall()
                    pass
        finally:
            conn.close()

    def del_companies_and_vacancies(self, employers_id: int):
        sql_query = """
        DELETE FROM vacancies WHERE employer_id = %s;
        DELETE FROM employers WHERE id = %s;
        """
        conn = psycopg2.connect(dbname=self.db_name, **self.params)
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql_query, [employers_id])
                    return cur.fetchall()
                    pass
        finally:
            conn.close()

    def get_all_vacancies(self, employers_id: int):
        """Получает список всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на
        вакансию"""
        sql_query = """
        SELECT employers.name, vacancies.name, vacancies.salary_from, vacancies.salary_to, vacancies.url, 
        vacancies.description
        FROM employers
        join vacancies ON employers.id=vacancies.employer_id
        where employers.id = %s
        """
        conn = psycopg2.connect(dbname=self.db_name, **self.params)
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql_query, [employers_id])
                    return cur.fetchall()
                    pass
        finally:
            conn.close()

    def get_avg_salary(self):
        """Получает среднюю зарплату по вакансиям"""
        pass

    def get_vacancies_with_higher_salary(self):
        """Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям"""
        pass

    def get_vacancies_with_keyword(self):
        """Получает список всех вакансий, в названии которых содержатся переданные в метод слова, например “python”"""
        pass
