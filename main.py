import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import logging
import os
import random

#настройка логирования
def log_action(message):
    with open('log.txt', 'a', encoding='utf-8') as f:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f'{now} — {message}\n')

# настройка отображения в консоли
pd.set_option('display.width', 200)
pd.set_option('display.max_columns', None)

n = 10  # кол-во маршрутов
log_action("Запуск программы. Начальное количество маршрутов - " + str(n))
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

log_action("Исходная таблица маршрутов создана")

def h_to_minutes(t_str):  # перевод в минуты
    h, m = map(int, t_str.split(':'))
    return h * 60 + m


def add_route(df, num_route, transport_type, dep_point, arr_point, dep_time, arr_time,
              price, total_seats, free_seats): #функция добавления маршрута
    log_action(
        print('Запрос на добавление маршрута: номер = ' + str(num_route) + ', тип = ' + transport_type +
              ', откуда = ' + dep_point + ', куда = ' + arr_point + ', выезд = ' +  str(dep_time) + ', приезд = ' + str(arr_time) +
              ', цена = ' +  str(price) + ', мест = ' + str(total_seats) + ', свободно = '+ str(free_seats))
    )
    # проверка формата
    try:
        dep_m = h_to_minutes(dep_time)
        arr_m = h_to_minutes(arr_time)
    except:
        print("Ошибка формата времени.")
        log_action('Ошибка: введен неправильный формат времени при добавлении маршрута')
        return df


    # учёт возможного перехода через сутки
    if arr_m <= dep_m:
        arr_m += 24 * 60

    if arr_m - dep_m < 10:
        print('Дельта отправления должна быть МИНИМУМ 10 минут')
        log_action('Попытка добавить маршрут с длительностью ' + str(arr_m-dep_m) + 'минут')
        return df

    # проверка свободного слота
    busy = df[
        (df['Пункт отправления'] == dep_point) &
        (df['Время отправления'] == dep_time)
    ]
    if not busy.empty:
        print('Ошибка: временной слот уже занят')
        log_action('Попытка добавить маршрут в занятый слот. Номер маршрута = ' + str(num_route) + ', откуда = ' + dep_point + ', время = ' + str(dep_time))
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
    log_action('Маршрут добавлен. Текущее количество строк: ' + str(len(df)))
    return df


def remove_route(df, num_route): # удаление маршрута
    log_action('Поступил запрос на удаление маршрута: номер = ' + str(num_route))
    mask = df['Номер маршрута'] == num_route
    delete = df[mask]
    if delete.empty:
        print('Маршрут не найден')
        log_action('Поступил запрос на удаление несуществующего маршрута')
        return df

    df = df.drop(delete.index).reset_index(drop=True)
    print('Маршрут удалён')
    log_action('Маршрут ' + str(num_route) + ' удалён')
    return df

def search_routes(df): #реализация функции поиска
    log_action('Начат поиск маршрутов')
    print("Поиск маршрутов:")
    print("1 - По пункту отправления")
    print("2 - По пункту прибытия")
    print("3 - По типу транспорта")
    choice = input("Ваш выбор: ")
    if choice == "1":
        print('Список городов:', city_list)
        city = input("Введите пункт отправления: ")
        result = df[df['Пункт отправления'] == city]
        log_action('Выполнен поиск по пункту отправления: ' + city + '. Найдено строк: ' + str(len(result)))
    if choice == "2":
        print('Список городов:', city_list)
        city = input("Введите пункт прибытия: ")
        result = df[df['Пункт прибытия'] == city]
        log_action('Выполнен поиск по пункту прибытия: ' + city + '. Найдено строк: ' + str(len(result)))
    if choice == "3":
        print("Виды транспорта:", transport_type_list)
        t = input("Введите тип транспорта (Поезд/Автобус/Электричка/Трамвай): ")
        result = df[df['Тип транспорта'] == t]
        log_action('Выполнен поиск по виду транспорта: ' + t + '. Найдено строк: ' + str(len(result)))
    if (choice != "1") & (choice != "2") & (choice != "3") & (choice != "0"):
        print('Неизвестная команда')
        log_action('Поступил запрос на выполнение неизвестной команды: ' + choice)
        return

    if result.empty:
        print('Маршруты по заданным условиям отсутствуют')
    else:
        print ('Найденные маршруты:')
        print(result)

def buy_ticket(df): #функция покупки билетов
    log_action('Запущена функция для покупки билетов')
    try:
        num_route = int(input("Номер маршрута: "))
    except ValueError:
        print("Номер маршрута должен быть числом.")
        log_action('ОШИБКА. Введен неверный номер маршрута (нечисловой параметр)')
        return df
    mask = (df['Номер маршрута'] == num_route)
    c = df[mask]
    if c.empty:
        print("Маршрут с такими параметрами не найден.")
        log_action('При попытке покупки билета был введен маршрут ' + str(num_route) + ', который отсутствует в расписании')
        return df

    i=c.index[0]

    if df.at[i, 'Свободно мест'] > 0:
        df.at[i, 'Свободно мест'] -= 1
        price = df.at[i, 'Цена билета']
        print("Билет куплен. Цена билета - ", price)
        print(df.loc[[i]])
        log_action('Ккуплен билет. Цена билета - ' + str(price) + '. Номер маршрута - ' + str(num_route))
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
            log_action('При попытке покупки билета мест и альтернативных маршрутов не оказалось')
        else:
            print("Доступные альтернативные маршруты:")
            print(alt)
            log_action('При попытке покупки билета места отсутствовали, но были найдены альтернативы')
        return df

def move_routes(df):
    log_action("Выполнен запрос на поиск маршрутов, находящихся в движении в момент запроса")
    t_str = input("Введите время (HH:MM): ")
    try:
        t = h_to_minutes(t_str)
    except:
        print("Ошибка формата времени.")
        log_action('Ошибка. Введен неверный формат времени')
        return

    dep_m = df['Время отправления'].apply(h_to_minutes)
    arr_m = df['Время прибытия'].apply(h_to_minutes)

    arr_m1 = arr_m.copy()
    mask1 = arr_m1 <= dep_m
    arr_m1[mask1] = arr_m1[mask1] + 1440

    mask = (dep_m <= t) & (t < arr_m1)
    result = df[mask]

    log_action('Найдено маршрутов в движении на ' + t_str + ':' + str(len(result)))

    if result.empty:
        print('В указанный момент времени ни один из маршрутов не находится в движении')
    else:
        print('Маршруты, которые находятся в пути:')
        print(result)

def stats (df): #выводим статистику
    log_action('Был выполнен запрос на вывод статистики по расписанию')
    print ('Статистика:')
    #1
    print ('Среднее время в пути по виду транспорта:')
    avg = df.groupby('Тип транспорта')['Продолжительность, мин'].mean()
    for i, j in avg.items(): # убрал стандартный принт, чтобы не выводилась справочная информация из модуля Pandas
        print(i, "-", j)
    log_action("Рассчитано среднее время в пути по видам транспорта")

    #2
    print ('Средняя цена за маршрут:')
    avg = df['Цена билета'].mean()
    print ('Средняя цена билета:', avg)
    log_action("Рассчитана средняя цена билета и составила - " + str(avg))

    #3
    print ('Маршруты с наполненостью <X%:')
    try:
        x = float(input("Введите X: "))
    except ValueError:
        print("Некорректное значение X")
        log_action('Введено некорректное значение X во время запроса статистики')
        return
    full = (df['Количество мест'] - df['Свободно мест']) / df['Количество мест'] * 100
    low = df[full<x]
    if low.empty:
        print("Маршрутов с заполненностью <", x, "% нет")
    else:
        print("Маршруты с заполненностью <", x, "%:")
        print(low)
    log_action('Маршруты с заполненностью <' + str(x) + '%: найдено - ' + str(len(low)))

    #4
    print('Самый частый вид транспорта за день:')
    k=df['Тип транспорта'].value_counts()
    if k.empty:
        print("Самый частый вид транспорта за день отсутствует")
        log_action("Самый частый вид транспорта: нет данных")
    else:
        print("Самый частый вид транспорта:", k.idxmax())
        log_action("Самый частый вид транспорта: " + k.idxmax())

    #5
    print ("Топ-3 самых долгих маршрута")
    top = df.sort_values('Продолжительность, мин', ascending=False).head(3)
    print(top)
    log_action("Выведен топ-3 самых долгих маршрутов")

def sortirovka (df): #сортировка по возрастанию/убыванию
    log_action('Был выполнен запрос на сортировку расписания по возрастанию/убыванию')
    print ('Выберите вариант сортировки')
    print ('1 - по возрастанию')
    print ('2 - по убыванию')
    choice = input('Ваш выбор:')

    if (choice == "1"):
        sorted = df.sort_values('Продолжительность, мин', ascending=True)
        log_action('Был выполнен запрос на сортировку по возрастанию')
    if (choice == "2"):
        sorted = df.sort_values('Продолжительность, мин', ascending=False)
        log_action('Был выполнен запрос на сортировку по убыванию')
    if (choice != "1") & (choice != "2"):
        print ('Выбрана неизвестная команда')
        log_action('Была введена неверная команда - ' + choice)
        return df

    print (sorted)
    return df

def show_trans(df):
    log_action('Был составлен запрос на вывод маршрутов, отсортированный по типу транспорта')
    print("Виды транспорта:", transport_type_list)
    t = input("Введите тип транспорта: ")
    log_action('Был введен тип транспорта - ' + t)
    if t not in transport_type_list:
        print("Такой вид транспорта отсутствует")
        log_action('Был введен тип транспорта - ' + t + ', который отсутствует в списке')
        return
    result = df[df['Тип транспорта'] == t]
    log_action('Маршруты по типу транспорта ' + t + ' найдено - ' + str(len(result)))
    if result.empty:
        print("Маршрутов с выбранным видом транспорта нет.")
    else:
        print("Маршруты с выбранным видом транспорта: ")
        print(result)

def diag_1(df):
    log_action('Поступил запрос на построение диаграммы средней продолжительности по видам транспорта')
    avg = df.groupby('Тип транспорта')['Продолжительность, мин'].mean()
    if avg.empty:
        print("Нет данных для построения диаграммы")
        log_action("После запроса выяснилось, что данные для построения диаграммы отсутствуют")
        return
    plt.figure(figsize=(7, 3))
    plt.bar(avg.index, avg.values, color='red')
    plt.xlabel('Тип транспорта')
    plt.ylabel('Средняя продолжительность, мин')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig("diag1.png")
    print("Диаграмма сохранена в файл")
    log_action("Диаграмма diag1.png сохранена")
    plt.show()

def diag_2(df):
    log_action("Поступил запрос на построение диаграммы заполненности маршрутов")
    full = (df['Количество мест'] - df['Свободно мест']) / df['Количество мест'] * 100
    if full.empty:
        print("Нет данных для построения диаграммы")
        log_action("После запроса выяснилось, что данные для построения диаграммы отсутствуют")
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
    log_action("Диаграмма diag2.png сохранена")
    plt.show()

def gr_1(df):
    log_action("Поступил запрос на построение графика пунктов прибытия для города")
    print("Список городов:", city_list)
    a = input("Введите пункт отправления: ")
    if a not in city_list:
        print("Такого города нет в списке")
        log_action('Был введен город, которого нет в списке')
        return
    a1 = df[df['Пункт отправления'] == a]
    if a1.empty:
        print("Маршрутов из этого пункта отправления нет")
        log_action('Нет маршрутов из пункта отправления ' + a)
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
    log_action('График gr1.png сохранен')
    plt.show()

def save_csv(df):
    filename='result.csv'
    df.to_csv(filename,index=False)
    print('Данные сохранены в файл result.csv')
    log_action('Состояние базы данных сохранено в файл result.csv')

def menu(df):  # меню
    log_action("Открыто главное меню")
    while True:
        print("Меню:")
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
        print ('13 - Сохранить текущее расписание в CSV')
        print("0 - Выход")
        choice = input("Ваш выбор: ")

        log_action('Выбран пункт меню - ' + choice)

        if choice == "1":
            print("Текущее расписание:")
            print(df)
            log_action('Показано расписание')

        if choice == "2":
            try:
                num_route = int(input("Номер маршрута (целое число): "))
            except ValueError:
                print("Номер маршрута должен быть числом.")
                log_action("Возникла ошибка после ввода номера маршрута. Введенное значение не является числом")
                continue

            print("Виды транспорта:", transport_type_list)
            transport_type = input("Тип транспорта: ")
            if transport_type not in transport_type_list:
                print('Такой вид транспорта отсутствует')
                log_action('Был введен несуществующий тип транспорта - ' + transport_type)
                continue
            print('Список городов:', city_list)
            dep_point = input("Пункт отправления: ")
            if dep_point not in city_list:
                print ('Такой город отсутствует в списке')
                log_action('Был введен несуществующий в списке город отправления - ' + dep_point)
                continue
            arr_point = input("Пункт прибытия: ")
            if arr_point not in city_list:
                print ('Такой город отсутствует в списке')
                log_action('Был введен несуществующий в списке город привятия - ' + arr_point)
                continue
            if dep_point == arr_point:
                print("Город прибытия не может совпадать с городом отправления")
                log_action('Было введено два одинаковых города - ' + dep_point)
                continue

            dep_time = input("Время отправления (HH:MM): ")
            arr_time = input("Время прибытия (HH:MM): ")

            try:
                price = int(input("Цена билета (целое число): "))
                total_s = int(input("Количество мест (целое число): "))
                free_s = int(input("Свободно мест: "))
            except ValueError:
                print("Цена и количество мест должны быть целыми числами.")
                log_action('Возникла ошибка при вводе цены и/или кол-ва мест')
                continue

            if free_s > total_s:
                print("Свободных мест не может быть больше, чем всего мест.")
                log_action('Попытка ввести количество свободных мест, превышающее общее количество мест')
                continue

            df = add_route(df, num_route, transport_type, dep_point, arr_point,
                           dep_time, arr_time, price, total_s, free_s)

        if choice == "3":
            try:
                num_route = int(input("Номер маршрута для удаления: "))
            except ValueError:
                print("Номер маршрута должен быть числом.")
                log_action('Возникла ошибка при удалении маршрута: введенное значение не является числом')
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

        if choice == '13':
            save_csv(df)

        if choice == "0":
            print("Выход")
            log_action('Совершен выход из программы пользователем')
            break

        if (choice != "1") & (choice != "2") & (choice != "3") & (choice!="4") & (choice!="5") & (choice!="6") &\
                (choice!="7") & (choice!="8") & (choice!="9") & (choice!="10")  & (choice!="11")  & (choice!="12")  & (choice!="13") & (choice != "0"):
            print('Неизвестная команда')
            log_action('При открытии меню была введена неизвестная команда - ' + choice)

    return df


df = menu(df)

print(df)
log_action('Программа завершена. Итоговое количество маршрутов - ' + str(len(df)))