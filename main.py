import pandas as pd
import numpy as np


#настройка отображения в консоли
pd.set_option('display.width', 200)
pd.set_option('display.max_columns', None)

n=10 # кол-во маршрутов
route_number = np.arange(1,101)
transport_type = ['Поезд', 'Автобус', 'Электричка', 'Трамвай']
city = ['Москва', 'Санкт-Петербург', 'Казань', 'Нижний Новгород', 'Новосибирск', 'Екатеринбург', 'Ростов-на-Дону']
route = np.random.choice(route_number, size=n)
transport = np.random.choice(transport_type, size=n)
departure = np.random.choice(city,size=n)
arrival = np.random.choice(city,size=n)
for i in range(n):
    while arrival[i] == departure[i]:
        arrival[i] = np.random.choice(city) #проверка и замена до тех пор, пока город отправления и прибытия перестанут совпадать
departure_time = np.random.randint(0,1440,size=n)
delta = np.random.randint(30,1440,size=n) #длительность поездки
arrival_time = departure_time + delta
next_sutki = arrival_time % (1440)

def min_to_time(m):
    h = m // 60
    min = m % 60
    return f"{h:02d}:{min:02d}"

departure_time2 = [min_to_time(m) for m in departure_time]
arrival_time2 = [min_to_time(m) for m in next_sutki]

ticket_price = np.random.randint (200,10000,size=n)
total_seats = np.random.randint (20,200,size=n)
free_seats = np.random.randint (0, total_seats+1)
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

print(df)
