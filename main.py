import psycopg2


class DBManager:
    """класс, который подключаеться к БД PostgreSQL """

    def __init__(self, database='hh_vacancies', host='localhost', user='postgres', password='2004', port='5432'):
        self.connection = psycopg2.connect(host=host, database=database, user=user, password=password, port=port)
        self.cur = None
        self.sql = ''

    def run_query(self):
        """Выполняет запрос"""
        self.cur = self.connection.cursor()
        self.cur.execute(self.sql)
        self.connection.commit()

    def query_result(self):
        """Выводит результат запрос"""
        item = self.cur.fetchall()
        if item:
            for i in item:
                print(*i)
        else:
            print("По вашему запросу ничего не найдено")
        self.cur.close()

    def create_companies_table(self) -> None:
        """Создает таблицу компаний"""

        self.sql = (f'CREATE TABLE companies '
                    f'(company_id int PRIMARY KEY,'
                    f'company_name varchar);')
        self.run_query()
        self.cur.close()

    def create_vacancies_table(self) -> None:
        """Создает таблицу вакансий"""

        self.sql = (f'CREATE TABLE vacancies '
                    f'(company_id int REFERENCES companies (company_id),'
                    f'employee varchar,'
                    f'city varchar, '
                    f'salary_from int,'
                    f'salary_to varchar(10),'
                    f'currency varchar(5),'
                    f'url varchar,'
                    f'description text);')
        self.run_query()
        self.cur.close()

    def insert_companies_table(self, params):
        """Заполняет данными таблицу компаний"""
        self.sql = "INSERT INTO companies VALUES(%s, '%s')" % tuple(params)
        self.run_query()
        self.cur.close()

    def insert_vacancies_table(self, params):
        """Заполняет данными таблицу вакансий"""
        self.sql = "INSERT INTO vacancies VALUES(%s, '%s', '%s', %s, %s, '%s', '%s', '%s')" % tuple(params)
        self.run_query()
        self.cur.close()

    def get_companies_and_vacancies_count(self):
        """получает список всех компаний и количество вакансий у каждой компании."""
        self.sql = (f'SELECT company_name, COUNT (*) FROM vacancies JOIN companies USING (company_id) '
                    f'GROUP BY company_name;')
        self.run_query()
        self.query_result()

    def get_all_vacancies(self):
        """получает список всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на
        вакансию."""
        self.sql = (f'SELECT company_name, employee, salary_from, salary_to, url FROM vacancies '
                    f'JOIN companies USING (company_id);')
        self.run_query()
        self.query_result()

    def get_avg_salary(self):
        """получает среднюю зарплату по вакансиям."""
        self.sql = 'SELECT AVG(salary_from) FROM vacancies;'
        self.run_query()
        self.query_result()

    def get_vacancies_with_higher_salary(self):
        """получает список всех вакансий, у которых зарплата выше средней по всем вакансиям."""
        self.sql = 'SELECT * FROM vacancies WHERE salary_from > (SELECT AVG(salary_from) FROM vacancies);'
        self.run_query()
        self.query_result()

    def get_vacancies_with_keyword(self, keyword=None):
        """получает список всех вакансий, в названии которых содержатся переданные в метод слова, например python."""
        self.sql = f"SELECT * FROM vacancies WHERE employee LIKE '%{keyword}%';"
        self.run_query()
        self.query_result()
