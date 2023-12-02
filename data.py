import psycopg2
import json
from api_client import HeadHunterApi, DeletionFiles
from main import DBManager
from config import config

"""Задаем стартовые параметры соединения, имя базы данных и таблицы"""

params = config()
db_name = 'hh_vacancies'

connection = psycopg2.connect(**params)
cur = connection.cursor()
connection.autocommit = True

"""Создаем базу данных с заданным именем, разрываем соединение"""

cur.execute(f'DROP DATABASE IF EXISTS {db_name};')
cur.execute(
    f'CREATE DATABASE {db_name} WITH OWNER = postgres ENCODING = "utf8" CONNECTION LIMIT = -1 IS_TEMPLATE = False;')
connection.commit()
cur.close()
connection.close()
params.update(database=db_name)

"""Создаем экземпляр класса DBManager для подключения к БД и работы с ней"""

db = DBManager(**params)
db.create_companies_table()
db.create_vacancies_table()

"""Список id заранее выбраных компаний"""

employers_id = ['9498120', '9418714', '1491512', '1272486', '816144', '797671', '592442', '15478', '39305', '2180']

"""Для каждого id получаем 20 открытых вакансий  и добавляем их в таблицу"""

for emp_id in employers_id:
    hh_vacancies = HeadHunterApi(emp_id)
    data = hh_vacancies.get_vacancies_list()
    hh_vacancies.add_to_json(data)
    id_list = []
    with open(hh_vacancies.filename, encoding='utf8') as f:
        data = json.load(f)
        for dict_ in data:
            """В программе выполняется проверка наличия значения зарплаты (salary). 
            Если работодатель не указал данные о зарплате, то значение приравнивается к нулю. 
            Это делается для обеспечения возможности проведения дальнейших сравнений."""
            if not dict_['salary']:
                salary_from = 0
                salary_to = 0
                currency = 'нет'
            else:
                salary_from = dict_['salary']['from'] if dict_['salary']['from'] else 0
                salary_to = dict_['salary']['to'] if dict_['salary']['to'] else 0
                currency = dict_['salary']['currency']

            company_id = dict_['company_id']

            """Создаем временные списки для добавления данных в таблицы"""

            if company_id not in id_list:
                temp_company_list = [company_id, dict_['company']]
                db.insert_companies_table(temp_company_list)
                id_list.append(company_id)

            temp_vacancy_list = [company_id, dict_['employee'], dict_['city'], salary_from, salary_to, currency,
                                 dict_['url'], dict_['requirement']]
            db.insert_vacancies_table(temp_vacancy_list)


def data_base_usage(db_object):
    """Функция для выполнения запросов к базе данных
    В качестве аргумента получает объект класса DBManager"""

    while True:
        print()
        print("Выберите действие:")
        print("1 - Получить список всех компаний и количество вакансий у каждой компании")
        print("2 - Получить список всех вакансий")
        print("3 - Получить среднюю зарплату по вакансиям")
        print("4 - Получить список вакансий с зарплатой выше средней по всем вакансиям")
        print("5 - Получить вакансии по ключевому слову")
        print("6 - Закончить работу")

        answer = input()
        if answer == '6':
            print('До встречи')
            DeletionFiles.delition_file = DeletionFiles('hh_vacancies.json')
            DeletionFiles.delition_file.delition()
            break
        elif answer == '1':
            db_object.get_companies_and_vacancies_count()
        elif answer == '2':
            db_object.get_all_vacancies()
        elif answer == '3':
            db_object.get_avg_salary()
        elif answer == '4':
            db_object.get_vacancies_with_higher_salary()
        elif answer == '5':
            keyword = input('Введите ключевое слово\n')
            db_object.get_vacancies_with_keyword(keyword)
        else:
            print('Некорректный ввод')


data_base_usage(db)
db.connection.close()
