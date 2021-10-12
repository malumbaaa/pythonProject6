from pymongo import MongoClient
import pymongo
from config import MONGO_CONNECTION_STRING

from datetime import date
import calendar
import locale


from collections import Counter


locale.setlocale(locale.LC_ALL, 'ru_RU')

def get_database():
    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(MONGO_CONNECTION_STRING)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client['VanderTest']


def reserve_table(table_number, date, people_count, telegram_id):
    user = find_user_by_telegramid(telegram_id)
    reserve_data = {
        "user_name": user["name"],
        "user_phone": user["phone"],
        "date": date,
        "table_number": table_number,
        "people_count": people_count,
        "telegram_id": str(telegram_id)
    }
    db = get_database()
    reservations = db["Reservations"]
    reservations.insert_one(reserve_data)
    print(reserve_data)


def get_reservations(date: str) -> list:
    db = get_database()
    reservations_collection = db["Reservations"]
    reservations = list(reservations_collection.find({'date': date}))
    return reservations


def register_new_user(name: str, phone: str, telegram_id: str) -> bool:
    user_data = {
        "name": name,
        "phone": phone,
        "telegram_id": telegram_id
    }
    if not is_registered(telegram_id):
        db = get_database()
        users = db["Users"]
        users.insert_one(user_data)
        print(user_data)
        return True
    return False


def find_user_by_telegramid(telegram_id: str):
    db = get_database()
    users = db["Users"]
    uid = users.find_one({"telegram_id": f"{telegram_id}"})
    return uid


def is_registered(telegram_id: str) -> bool:
    db = get_database()
    users = db["Users"]
    uid = users.find_one({"telegram_id" : f"{telegram_id}"})
    if uid is not None:
        return True
    else:
        return False


def get_all_users():
    db = get_database()
    users_collection = db["Users"]
    users = list(users_collection.find())
    return users


def get_all_orders():
    db = get_database()
    reservation_collection = db["Reservations"]
    reservations = list(reservation_collection.find())
    return reservations


def get_stat_order():  # можно соеденить 2 функции
    db = get_database()
    reservation_collection = db["Reservations"]
    reservations = list(reservation_collection.find())
    all_stat = {
        "В среднем людей": [],
        "days": []
    }
    for reservation in reservations:
        all_stat['В среднем людей'].append(int(reservation['people_count']))
        date_res = reservation['date'].split('-')
        all_stat['days'].append((date(int(date_res[0]), int(date_res[1]), int(date_res[2])).strftime('%A')))
    all_stat['Общее количество заказов'] = len(all_stat['В среднем людей'])
    all_stat['В среднем людей'] = sum(all_stat['В среднем людей'])/len(all_stat['В среднем людей'])
    max = -1
    for weekday in calendar.day_name:
        count = all_stat['days'].count(weekday)
        all_stat[weekday] = count
        if max < count:
            all_stat['Самый популярный день'] = weekday
            max = count
    del all_stat['days']
    data = ''
    for key, value in all_stat.items():
        data += f'{key}: {value}\n'
    return data


def get_stat_users():
    db = get_database()
    users = get_all_users()
    reservations = get_all_orders()
    users = dict.fromkeys([tg['telegram_id'] for tg in users], [])
    print(users)
    for reservation in reservations:
        date_res = reservation['date'].split('-')
        reservation['date'] = (date(int(date_res[0]), int(date_res[1]), int(date_res[2])).strftime('%A'))
        print(users[reservation['telegram_id']])
        users[reservation['telegram_id']] = users[reservation['telegram_id']]+[reservation,]
    stat_users = []
    for key, value in users.items():
        print(key)
        print(value)
        # stat_users.append({
        #     'Количество заказов: ': len(value),
        #     'Любимый столик: ': Counter([i['table_number'] for i in value]).most_common()[0],
        #     'Любимый день недели:': Counter([i['date'] for i in value]).most_common()[0],
        #     'Среднее кол-во людей: ': sum([int(i['people_count']) for i in value])/len(value),
        #     'Имя': value[0]['user_name'],
        #     'Телефон': value[0]['user_phone']  на случай, если нам всё-таки понадобится вид слловаря
        # })
        stat_users.append(
            f'Количество заказов:  {len(value)}\n'+
            f"Любимый столик:  {Counter([i['table_number'] for i in value]).most_common()[0][0]}\n"+
            f"Любимый день недели: {Counter([i['date'] for i in value]).most_common()[0][0]}\n"+
            f"Среднее кол-во людей:  {sum([int(i['people_count']) for i in value]) / len(value)}\n"+
            f"Имя: {value[0]['user_name']}\n"+
            f"Телефон: {value[0]['user_phone']}\n"
        )
    return stat_users





