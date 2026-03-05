import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
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




def h_to_minutes(t_str):  # перевод в минуты
    h, m = map(int, t_str.split(':'))
    return h * 60 + m


def add_route(df, num_route, transport_type, dep_point, arr_point, dep_time, arr_time,
              price, total_seats, free_seats): #функция добавления маршрута

    # проверка формата
    try:
        dep_m = h_to_minutes(dep_time)
        arr_m = h_to_minutes(arr_time)
    except:
        print("Ошибка формата времени.")
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


def remove_route(df, num_route): # удаление маршрута
    mask = df['Номер маршрута'] == num_route
    delete = df[mask]
    if delete.empty:
        print('Маршрут не найден')
        return df

    df = df.drop(delete.index).reset_index(drop=True)
    print('Маршрут удалён')
    return df

def search_routes(df): #реализация функции поиска
    print("\nПоиск маршрутов:")
    print("1 - По пункту отправления")
    print("2 - По пункту прибытия")
    print("3 - По типу транспорта")
    choice = input("Ваш выбор: ")
    if choice == "1":
        print('Список городов:', city_list)
        city = input("Введите пункт отправления: ")
        result = df[df['Пункт отправления'] == city]
    if choice == "2":
        print('Список городов:', city_list)
        city = input("Введите пункт прибытия: ")
        result = df[df['Пункт прибытия'] == city]
    if choice == "3":
        print("Виды транспорта:", transport_type_list)
        t = input("Введите тип транспорта (Поезд/Автобус/Электричка/Трамвай): ")
        result = df[df['Тип транспорта'] == t]
    if (choice != "1") & (choice != "2") & (choice != "3") & (choice != "0"):
        print('Неизвестная команда')
        return

    if result.empty:
        print('Маршруты по заданным условиям отсутствуют')
    else:
        print ('Найденные маршруты:')
        print(result)

def buy_ticket(df): #функция покупки билетов
    try:
        num_route = int(input("Номер маршрута: "))
    except ValueError:
        print("Номер маршрута должен быть числом.")
        return df
    mask = (df['Номер маршрута'] == num_route)
    c = df[mask]
    if c.empty:
        print("Маршрут с такими параметрами не найден.")
        return df

    i=c.index[0]

    if df.at[i, 'Свободно мест'] > 0:
        df.at[i, 'Свободно мест'] -= 1
        price = df.at[i, 'Цена билета']
        print("Билет куплен. Цена билета - ", price)
        print(df.loc[[i]])
        return df

    if df.at[i, 'Свободно мест'] == 0:
        print("Свободных мест на выбранный маршрут нет.")
        dep_point = df.at[i, 'Пункт отправления']
        arr_point = df.at[i, 'Пункт прибытия']
        alt = df[
        (df['Пункт отправления'] == dep_point) &
        (df['Пункт прибытия'] == arr_point) &
        (df['Свободно мест'] > 0) &
        (df.index != i)
            ]
        if alt.empty:
            print("Альтернативные маршруты отсутствуют.")
        else:
            print("Доступные альтернативные маршруты:")
            print(alt)
        return df

def move_routes(df):
    t_str = input("Введите время (HH:MM): ")
    try:
        t = h_to_minutes(t_str)
    except:
        print("Ошибка формата времени.")
        return

    dep_m = df['Время отправления'].apply(h_to_minutes)
    arr_m = df['Время прибытия'].apply(h_to_minutes)

    arr_m1 = arr_m.copy()
    mask1 = arr_m1 <= dep_m
    arr_m1[mask1] = arr_m1[mask1] + 1440

    mask = (dep_m <= t) & (t < arr_m1)
    result = df[mask]

    if result.empty:
        print('В указанный момент времени ни один из маршрутов не находится в движении')
    else:
        print('Маршруты, которые находятся в пути:')
        print(result)

def stats (df): #выводим статистику
    print ('Статистика:')
    #1
    print ('Среднее время в пути по виду транспорта:')
    avg = df.groupby('Тип транспорта')['Продолжительность, мин'].mean()
    for i, j in avg.items(): # убрал стандартный принт, чтобы не выводилась справочная информация из модуля Pandas
        print(i, "-", j)

    #2
    print ('Средняя цена за маршрут:')
    avg = df['Цена билета'].mean()
    print ('Средняя цена билета:', avg)

    #3
    print ('Маршруты с наполненостью <X%:')
    try:
        x = float(input("Введите X: "))
    except ValueError:
        print("Некорректное значение X")
        return
    full = (df['Количество мест'] - df['Свободно мест']) / df['Количество мест'] * 100
    low = df[full<x]
    if low.empty:
        print("Маршрутов с заполненностью <", x, "% нет")
    else:
        print("Маршруты с заполненностью <", x, "%:")
        print(low)

    #4
    print('Самый частый вид транспорта за день:')
    k=df['Тип транспорта'].value_counts()
    if k.empty:
        print("Самый частый вид транспорта за день отсутствует")
    else:
        print("Самый частый вид транспорта:", k.idxmax())

    #5
    print ("Топ-3 самых долгих маршрута")
    top = df.sort_values('Продолжительность, мин', ascending=False).head(3)
    print(top)

def sortirovka (df): #сортировка по возрастанию/убыванию
    print ('Выберите вариант сортировки')
    print ('1 - по возрастанию')
    print ('2 - по убыванию')
    choice = input('Ваш выбор:')

    if (choice == "1"):
        sorted = df.sort_values('Продолжительность, мин', ascending=True)
    if (choice == "2"):
        sorted = df.sort_values('Продолжительность, мин', ascending=False)
    if (choice != "1") & (choice != "2"):
        print ('Выбрана неизвестная команда')
        return df

    print (sorted)
    return df

def show_trans(df):
    print("Виды транспорта:", transport_type_list)
    t = input("Введите тип транспорта: ")
    if t not in transport_type_list:
        print("Такой вид транспорта отсутствует")
        return
    result = df[df['Тип транспорта'] == t]
    if result.empty:
        print("Маршрутов с выбранным видом транспорта нет.")
    else:
        print("Маршруты с выбранным видом транспорта: ")
        print(result)

def diag_1(df):
    avg = df.groupby('Тип транспорта')['Продолжительность, мин'].mean()
    if avg.empty:
        print("Нет данных для построения диаграммы")
        return
    plt.figure(figsize=(7, 3))
    plt.bar(avg.index, avg.values, color='red')
    plt.xlabel('Тип транспорта')
    plt.ylabel('Средняя продолжительность, мин')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig("diag1.png")
    print("Диаграмма сохранена в файл")
    plt.show()

def diag_2(df):
    full = (df['Количество мест'] - df['Свободно мест']) / df['Количество мест'] * 100
    if full.empty:
        print("Нет данных для построения диаграммы")
        return
    plt.figure(figsize=(7, 3))
    x = range(len(df))
    plt.bar(x, full.values, color='red')
    plt.xlabel('Индекс маршрута')
    plt.ylabel('Заполненность, %')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig("diag2.png")
    print("Диаграмма сохранена в файл")
    plt.show()

def gr_1(df):
    print("Список городов:", city_list)
    a = input("Введите пункт отправления: ")
    if a not in city_list:
        print("Такого города нет в списке")
        return
    a1 = df[df['Пункт отправления'] == a]
    if a1.empty:
        print("Маршрутов из этого пункта отправления нет")
        return
    k=a1['Пункт прибытия'].value_counts()

    plt.figure(figsize=(7, 4))
    plt.bar(k.index, k.values, color='red')
    plt.xlabel('Пункт прибытия')
    plt.ylabel('Количество маршрутов')
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    plt.savefig("gr1.png")
    print("График сохранен в файл")
    plt.show()

def menu(df):  # меню
    while True:
        print("\nМеню:")
        print("1 - Показать расписание")
        print("2 - Добавить маршрут")
        print("3 - Удалить маршрут")
        print("4 - Выполнить поиск маршрутов")
        print('5 - Купить билет')
        print('6 - Найти маршруты в движении')
        print ('7 - Показать статистику')
        print ('8 - Сортировка')
        print ('9 - Показать маршруты по виду транспорта')
        print ('10 - Вывести диаграмму средней продолжительности по видам транспорта')
        print ('11 - Вывести диаграмму заполненности маршрутов в процентах')
        print ('12 - Вывести график пунктов приема для конкретного пункта отправки')
        print("0 - Выход")
        choice = input("Ваш выбор: ")

        if choice == "1":
            print("Текущее расписание:")
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

        if choice == "4":
            search_routes(df)

        if choice == "5":
            df = buy_ticket(df)

        if choice == "6":
            move_routes(df)

        if choice == "7":
            stats(df)

        if choice == "8":
            df = sortirovka(df)

        if choice == "9":
            show_trans(df)

        if choice == "10":
            diag_1(df)

        if choice == '11':
            diag_2(df)

        if choice == '12':
            gr_1(df)

        if choice == "0":
            print("Выход")
            break

        if (choice != "1") & (choice != "2") & (choice != "3") & (choice!="4") & (choice!="5") & (choice!="6") &\
                (choice!="7") & (choice!="8") & (choice!="9") & (choice!="10")  & (choice!="11")  & (choice!="12") & (choice != "0"):
            print('Неизвестная команда')

    return df


df = menu(df)

print(df)