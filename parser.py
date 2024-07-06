import requests
from bs4 import BeautifulSoup
import mysql.connector
import time

# Конфигурация базы данных
db_config = {
    'user': 'your_user',
    'password': 'your_password',
    'host': 'db',  # Docker-compose использует имя сервиса в качестве хоста
    'database': 'job_database',
    'port': '3306'
}


# Функция для создания соединения с базой данных
def create_connection(config):
    max_retries = 5
    retry_delay = 5
    conn = None
    for attempt in range(max_retries):
        try:
            conn = mysql.connector.connect(**config)
            break
        except mysql.connector.Error as err:
            print(f"Attempt {attempt + 1} failed: {err}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise
    return conn


# Функция для создания таблицы (выполните один раз)
def create_table(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vacancies (
        id INT AUTO_INCREMENT PRIMARY KEY,
        fio VARCHAR(255),
        job_title VARCHAR(255),
        skills TEXT,
        work_format VARCHAR(255)
    )
    """)


# Функция для сохранения данных в базу
def save_to_db(cursor, conn, data):
    query = """
    INSERT INTO vacancies (fio, job_title, skills, work_format)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (data['fio'], data['job_title'], data['skills'], data['work_format']))
    conn.commit()


# Функция для парсинга данных с hh.ru
def parse_hh(cursor, conn):
    url = "https://api.hh.ru/vacancies"
    response = requests.get(url)
    vacancies = response.json()['items']
    for vacancy in vacancies:
        data = {
            'fio': vacancy['employer']['name'],
            'job_title': vacancy['name'],
            'skills': ', '.join([skill['name'] for skill in vacancy['key_skills']]),
            'work_format': vacancy['employment']['name']
        }
        save_to_db(cursor, conn, data)


# Функция для парсинга данных с avito.ru
def parse_avito(cursor, conn):
    url = "https://www.avito.ru/all/vakansii"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    items = soup.select('.iva-item-content-m2FiN')
    for item in items:
        job_title = item.select_one('.title-root-zZCwT a').text.strip()
        fio = item.select_one('.link-link-MbQDP').text.strip() if item.select_one('.link-link-MbQDP') else 'Не указано'
        skills = 'Не указано'  # Avito не всегда предоставляет навыки в открытом доступе
        work_format = item.select_one('.params-paramsList-x-_L-').text.strip() if item.select_one(
            '.params-paramsList-x-_L-') else 'Не указано'

        data = {
            'fio': fio,
            'job_title': job_title,
            'skills': skills,
            'work_format': work_format
        }
        save_to_db(cursor, conn, data)


# Функция для парсинга данных с career.habr.com
def parse_habr(cursor, conn):
    url = "https://career.habr.com/vacancies?type=all"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    items = soup.select('.job')
    for item in items:
        job_title = item.select_one('.title').text.strip()
        fio = item.select_one('.company_name a').text.strip()
        skills = item.select_one('.description').text.strip()
        work_format = 'Не указано'  # Habr Карьера не всегда предоставляет формат работы

        data = {
            'fio': fio,
            'job_title': job_title,
            'skills': skills,
            'work_format': work_format
        }
        save_to_db(cursor, conn, data)


def main():
    conn = create_connection(db_config)
    with conn:
        with conn.cursor() as cursor:
            create_table(cursor)
            parse_hh(cursor, conn)
            parse_avito(cursor, conn)
            parse_habr(cursor, conn)


if __name__ == "__main__":
    main()
