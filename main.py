import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import logging
import os
import random

# настройка отображения в консоли
pd.set_option('display.width', 200)
pd.set_option('display.max_columns', None)

n = 10  # кол-во маршрутов
route_number = np.arange(1, 101)
transport_type_list = ['Поезд', 'Автобус', 'Электричка', 'Трамвай']
city_list = ['Москва', 'Санкт-Петербург', 'Казань', 'Нижний Новгород', 'Новосибирск', 'Екатеринбург', 'Ростов-на-Дону']

route = np.random.choice(route_number, size=n)
transport = np.random.choice(transport_type_list, size=n)
departure = np.random.choice(city_list, size=n)
arrival = np.random.choice(city_list, size=n)

# проверка и замена до тех пор, пока города отправления и прибытия перестанут совпадать
for i in range(n):
    while arrival[i] == departure[i]:
        arrival[i] = np.random.choice(city_list)

departure_time = np.random.randint(0, 1440, size=n)
delta = np.random.randint(30, 1440, size=n)  # длительность поездки
arrival_time = departure_time + delta
next_sutki = arrival_time % 1440

def min_to_time(m):
    h = m // 60
    m2 = m % 60
    return f"{h:02d}:{m2:02d}"

departure_time2 = [min_to_time(m) for m in departure_time]
arrival_time2 = [min_to_time(m) for m in next_sutki]

ticket_price = np.random.randint(200, 10000, size=n)
total_seats = np.random.randint(20, 200, size=n)
free_seats = np.random.randint(0, total_seats + 1)

df = pd.DataFrame({
    'Номер маршрута': route,
    'Тип транспорта': transport,
    'Пункт отправления': departure,
    'Пункт прибытия': arrival,
    'Время отправления': departure_time2,
    'Время прибытия': arrival_time2,
    'Продолжительность, мин': delta,
    'Цена билета': ticket_price,
    'Количество мест': total_seats,
    'Свободно мест': free_seats
})




def h_to_minutes(t_str):  # перевод из "HH:MM" в минуты
    h, m = map(int, t_str.split(':'))
    return h * 60 + m


def add_route(df, num_route, transport_type, dep_point, arr_point, dep_time, arr_time,
              price, total_seats, free_seats): #функция добавления маршрута

    # проверка формата
    try:
        dep_m = h_to_minutes(dep_time)
        arr_m = h_to_minutes(arr_time)
    except:
        print("Ошибка формата времени. Используйте HH:MM (например, 09:30).")
        return df

    # учёт возможного перехода через сутки
    if arr_m <= dep_m:
        arr_m += 24 * 60

    if arr_m - dep_m < 10:
        print('Дельта отправления должна быть МИНИМУМ 10 минут')
        return df

    # проверка свободного слота
    busy = df[
        (df['Пункт отправления'] == dep_point) &
        (df['Время отправления'] == dep_time)
    ]
    if not busy.empty:
        print('Ошибка: временной слот уже занят')
        return df

    duration = arr_m - dep_m

    new_row = {
        'Номер маршрута': num_route,
        'Тип транспорта': transport_type,
        'Пункт отправления': dep_point,
        'Пункт прибытия': arr_point,
        'Время отправления': dep_time,
        'Время прибытия': arr_time,
        'Продолжительность, мин': duration,
        'Цена билета': price,
        'Количество мест': total_seats,
        'Свободно мест': free_seats
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    print('Новый маршрут добавлен')
    return df


def remove_route(df, num_route):
    mask = df['Номер маршрута'] == num_route
    delete = df[mask]
    if delete.empty:
        print('Маршрут не найден')
        return df

    df = df.drop(delete.index).reset_index(drop=True)
    print('Маршрут удалён')
    return df


def menu(df):  # меню
    while True:
        print("\nМеню:")
        print("1 - Показать расписание")
        print("2 - Добавить маршрут")
        print("3 - Удалить маршрут")
        print("0 - Выход")
        choice = input("Ваш выбор: ")

        if choice == "1":
            print("\nТекущее расписание:")
            print(df)

        if choice == "2":
            try:
                num_route = int(input("Номер маршрута (целое число): "))
            except ValueError:
                print("Номер маршрута должен быть числом.")
                continue

            print("Виды транспорта:", transport_type_list)
            transport_type = input("Тип транспорта: ")
            if transport_type not in transport_type_list:
                print('Такой вид транспорта отсутствует')
                continue
            print('Список городов:', city_list)
            dep_point = input("Пункт отправления: ")
            if dep_point not in city_list:
                print ('Такой город отсутствует в списке')
                continue
            arr_point = input("Пункт прибытия: ")
            if arr_point not in city_list:
                print ('Такой город отсутствует в списке')
                continue
            if dep_point == arr_point:
                print("Город прибытия не может совпадать с городом отправления")
                continue

            dep_time = input("Время отправления (HH:MM): ")
            arr_time = input("Время прибытия (HH:MM): ")

            try:
                price = int(input("Цена билета (целое число): "))
                total_s = int(input("Количество мест (целое число): "))
                free_s = int(input("Свободно мест: "))
            except ValueError:
                print("Цена и количество мест должны быть целыми числами.")
                continue

            if free_s > total_s:
                print("Свободных мест не может быть больше, чем всего мест.")
                continue

            df = add_route(df, num_route, transport_type, dep_point, arr_point,
                           dep_time, arr_time, price, total_s, free_s)

        if choice == "3":
            try:
                num_route = int(input("Номер маршрута для удаления: "))
            except ValueError:
                print("Номер маршрута должен быть числом.")
                continue

            df = remove_route(df, num_route)

        if choice == "0":
            print("Выход")
            break
            
        if (choice != "1") & (choice != "2") & (choice != "3") & (choice != "0"):
            print('Неизвестная команда')

    return df


df = menu(df)

print(df)