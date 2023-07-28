from datetime import datetime

import pandas as pd
import numpy as np

date_format = '%d.%m.%Y'


d1_date = datetime.strptime("01.01.2020", date_format)
d1 = [
    ["Глутатионпероксидаза (селен)", "9888", "Ед/л", "4 171 - 10 881"],
    ["Общий антиоксидантный статус", "2.30", "ммоль/л", "1.50 - 2.80"],
]

d2_date = datetime.strptime("02.01.2020", date_format)
d2 = [
    ["Глутатионпероксидаза (селен)", "8999", "Ед/л", "4 171 - 10 881"],
    ["СОД (супероксиддисмутаза) ", "234", "Ед/мл", "164 - 240"],
]

dic = {d1_date: d1, d2_date: d2}

analisys = []

for date, value in dic.items():
    analisys = analisys + [item[0] for item in value]

print(analisys)

analisys_dict = dict.fromkeys(analisys)

print(analisys_dict.keys())

dates = [date.strftime(date_format) for date in dic]

cols = dates + ["Ед. измерения", "Референсное значение"]
print(cols)

df = pd.DataFrame(index=analisys_dict.keys(), columns=cols)

for date, value in dic.items():
    for item in value:
        df.at[item[0], date.strftime(date_format)] = item[1]
        df.at[item[0], "Ед. измерения"] = item[2]
        df.at[item[0], "Референсное значение"] = item[3]

print(df)