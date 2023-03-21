from dadata import Dadata
import sqlite3
import httpx


conn = sqlite3.connect('settings_software.db')
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS settings(
   id INTEGER PRIMARY KEY,
   API TEXT NOT NULL,
   language TEXT NOT NULL);
""")
conn.commit()


def checking_API():
    """Проверка API ключа"""
    API = input("Введитесвой API ключ: ")
    try:
        dadata = Dadata(API)  
        dadata.suggest("address", "Москва") # запрос к сервису для проверки API ключа.
        return API
    except (httpx.HTTPStatusError, httpx.LocalProtocolError, UnicodeEncodeError):
        print("API не действителен или введён не коректно")


def is_valid_data():
    """Проверка валидности языка"""
    language = str()
    language_dict = {"1": "en", "2": "ru"}
    while language not in language_dict:
        language = input("Выберите язык, введя цифру en-1/ru-2: ")
        if language in language_dict:
            language = language_dict.get(language)
            return language
        elif not language:
            return "ru"
        print("введены не коректные данные, попробуйте ещё раз")


# проверяем бд на наличие данных настроек
cur.execute("SELECT * FROM settings WHERE id = ?", ('1'))
if cur.fetchone() is None:
    API_KEY = checking_API()
    while not API_KEY:
        API_KEY = checking_API()
    data = (API_KEY, is_valid_data())
    cur.execute("INSERT INTO settings(API, language) VALUES (?,?)", (data))
    conn.commit()


def finding_coordinates():
    """Поиск координат по заданному адресу"""
    token = cur.execute(f'SELECT API FROM settings WHERE id ={1}').fetchone()
    token = token[0]
    language = cur.execute(f'SELECT language FROM settings WHERE id ={1}').fetchone()
    language = language[0]
    parameters = {
            "language": language,
            "Content-Type": "application/json",
            "Accept": "application/json",
            }
    address = input('Введите адрес: ').lower()
    list_address = [None, ]  # Список городов
    while address != 'стоп':
        try:
            dadata = Dadata(token)
            result = dadata.suggest("address", address, **parameters)
            if not result:
                print("Адрес введён не коректно попробуйте ещё раз")
                continue
            count = 0
            for elem in result:
                count += 1
                list_address.append(elem)
                print(str(count) + ")", elem.get('value', None))
            number = int(
                input('Введите номер города который для вывода координат: '))
            geo_lat = list_address[number]['data']['geo_lat']
        except Exception:
            print("Данные номер не коректно попробуйте ещё раз")
            finding_coordinates()  # Вызываем функцию повторно в случаи исключения
        else:
            geo_lat = list_address[number]['data']['geo_lat']
            geo_lon = list_address[number]['data']['geo_lon']
            name = list_address[number]['value']
            print(name,": ", geo_lat, "*", geo_lon)
            list_address = [None, ]
            address = input('Введите адрес: ').lower()

finding_coordinates()

