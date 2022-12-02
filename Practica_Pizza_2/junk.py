from datetime import datetime
import pandas as pd
from dateutil.parser import parse
from difflib import SequenceMatcher

# date = "May 29 2016"
# print(parse(date), type(parse(date)))
# date = "1468533600"
# print(datetime.fromtimestamp(int(date)).date())
# try:
#     print(parse(date))
# except ValueError:
#     print("Hey!")
# idx = df.index[df["Name"] == "Andrés"].to_list()
# df.at[idx[0], "Name"] = "Fran"
# print(df)

# string = "2016, 09, 17"
# print(string[6:8])
# val = df.index[df["Name"] == "Javi"].to_list()[0]
# print(val, type(val))
# df[['First','Last']] = df.Name.str.split(" ",expand=True,)
# print(len(df))
# pizzas = pd.read_csv("pizza_types.csv", sep=",", usecols=["pizza_type_id", "ingredients"], encoding="latin1")
# pizzas = pizzas.astype({"pizza_type_id": "string", "ingredients": "string"})
# lista_pizzas = pizzas["pizza_type_id"].to_list()

# s = []
# print(lista_pizzas)

# for pizza in lista_pizzas:
#     s.append(SequenceMatcher(None, pizza, "ckn @lfredo m").ratio())
# print(s)

tiempos = [1,2,3,4]
print(tiempos[-3:])

