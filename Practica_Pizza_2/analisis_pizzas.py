import pandas as pd
import re
from datetime import datetime
from dateutil.parser import parse
from difflib import SequenceMatcher
import csv


def analizar_df(df: pd.DataFrame) -> None:
    '''Función para evaluar la calidad del dato
    '''
    print("Tipología del dataframe:")
    print(df.info())
    print("\n")
    print("Nans del dataframe:")
    print(df.isna().sum())
    print("Nulls del dataframe:")
    print(df.isnull().sum())


def clear_df(df: pd.DataFrame):
    '''Formatea el df
    '''
    df = df.rename(columns={"order_id": "date", "tiem": "order_id "})

    # Puesto que los tipos no están del todo bien (aparece un object)
    # vamos a especificar el tipo de cada columna
    df = df.astype({"date": "string"})
    df = df.dropna()

    return df


def formatear_fechas(tiempos: pd.DataFrame):
    '''Las fechas están en un formato totalmente erróneo.
    esta función las organizará en un mismo formato
    '''
    dates = tiempos["date"].to_list()

    for date in dates:
        idx = tiempos.index[tiempos["date"] == date].to_list()
        try:
            new_date = datetime.strftime(parse(date).date(),
                                        "%Y, %m, %d")
            tiempos.at[idx[0], "date"] = new_date
        except ValueError:  # Caso especial: timestamp en segundos
            # "since epoch"
            new_date = datetime.strftime(datetime.fromtimestamp(float(date)).date(),
                                        "%Y, %m, %d")
            tiempos.at[idx[0], "date"] = new_date
    return tiempos


def guardar_en_csv(df: pd.DataFrame):
    '''función Para guardar el dataframe tiempos a csv
    '''
    df.to_csv("tiempos.csv", index=False)


def partir_df(df: pd.DataFrame):
    '''Secciona el df por meses
    '''
    lista_months = ["02", "03", "04", "05", "06", "07", "08",
                    "09", "10", "11", "12", "13"]
    j = 6247  # Label de la primera fila del df
    dfs = []
    for month in lista_months:
        if month != "13":
            k = df.index[df["Month"] == month].to_list()
        else:
            k = [9498]  # Última fila del df
        # print("J: ", j)
        # print("K: ", k[0])
        new_df = df.loc[j:k[0]]

        if month != "13":
            new_df.drop(new_df.tail(1).index,inplace=True) # drop last n rows
        new_df = new_df.sort_values(by=["order_id"])
        dfs.append(new_df)
        j = int(k[0])
    return dfs


def sacar_ing(string: str) -> list:
    '''Dada una cadena, usa Regex para obtener los ingredientes individuales

    Parameters
    ----------
    string:
        str; Cadena del tipo "Cheese, Chorizo, Sauce..."

    Returns
    -------
    list:
        Contiene todos los ingredientes en forma de cadenas
    '''
    lista_ingredientes = re.split(", ", string)
    for ing in lista_ingredientes:
        for mes in dict_ing:
            dict_ing_mes = dict_ing[mes]
            if ing not in dict_ing_mes:
                dict_ing_mes[ing] = 0  # Inicializamos a 0 su cantidad necesaria
    return lista_ingredientes


def corregir_nombres_pizzas():
    '''Así como las fechas, también los nombres de las pizzas tienen caracteres
    incorrectos. Esta función usará un método de similitud entre cadenas para saber
    a cuál de los nombres correctos se parece más el incorrecto, sustituyéndolo
    '''
    lista_pizzas = pizzas["pizza_type_id"].to_list()
    for i in range(38139):
        row = details.iloc[i]
        nombre_mal = row[0]
        ratios = []
        if nombre_mal not in lista_pizzas:
            for name in lista_pizzas:
                # Buscamos, con Sequence Matcher, el nombre de la pizza al
                # que más se parece el incorrecto
                ratio = SequenceMatcher(None, nombre_mal, name).ratio()
                if ratio > 0.8:
                    nombre = name
                    break
                ratios.append(ratio)
            if not nombre:
                nombre = lista_pizzas[ratios.index(max(ratios))]
            details.iat[i, 0] = nombre  # Actualizamos el nombre al correcto

    # Guardamos este csv para uso posterior, ya que el algoritmo
    # creado en esta función es muy costoso como hacerlo cada vez
    # que tengamos que correrlo en las pruebas
    details.to_csv("details1.csv")


def dict_to_csv(dictionary: dict, name: str):
    '''Función que guarda un diccionario como csv
    '''
    columns = list(dictionary.keys())
    with open(name, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        writer.writerow(dictionary)


def exportar_ingredientes(df_ing: pd.DataFrame):
    '''Dado un diccionario de todos los ingredientes,
    construirá la cadena que muestra la cantidad

    Parameters
    ----------
    dict_ing:
        dict; Sus claves son cadenas (nombre ingrediente)
        y los valores enteros (unidades de tal ingrediente)

    Returns
    -------
    None, just creates a txt file
    '''
    with open("stock_semanal.txt", "w", encoding="latin-1") as file:
        file.write("        ****Panel de ingredientes para cada mes****\n")
        for i in range(df_ing.shape[0]):
            row = df.iloc[i]
            mes = dict_meses[row.name]
            file.write(f"\n{mes}")
            file.write("\nCada semana, harán falta:\n")

            for ingrediente in list(df_ing.columns):
                
                # Dado que hay una media de 4,33 semanas en un mes:
                file.write(f"   {ingrediente}: {int(row[ingrediente]//4.33)}\n")


if __name__ == "__main__":
    tiempos = pd.read_csv("orders.csv", sep=";")[["tiem", "order_id"]]

    print(analizar_df(tiempos))
    tiempos = clear_df(tiempos)
    print("Trabajando. Por favor, no pare el proceso. Podría tardar bastante")

    # Parece que el principal problema son las fechas que están en distintos formatos
    # Por ello, formateamos cada fecha
    tiempos = formatear_fechas(tiempos)
    # Ahora, ya tenemos todas las fechas en un mismo formato, por lo que
    # podemos manejarlas sin problemas
    tiempos.rename(columns={"order_id ": "order_id"}, inplace=True)

    # Ordenamos el df poniendo los pedidos más "antiguos" los primeros
    tiempos = tiempos.sort_values(by=["date"])
    # Separamos el campo date en año, mes y día
    tiempos[["Year", "Month", "Day"]] = tiempos.date.str.split(", ", expand=True)
    # Eliminamos las columnas que no nos sirven de nada
    del tiempos["date"]
    del tiempos["Year"]
    del tiempos["Day"]

    details = pd.read_csv("order_details.csv", sep=";", usecols=["order_id", "pizza_id", "quantity"])
    # Usamos order_id como índice en el dataframe
    details.set_index("order_id", inplace=True)
    # Ahora, ordenamos el dataframe para que sea más estético
    details.sort_values(by=["order_id"], inplace=True)
    details = details[details["pizza_id"].notna()][:-1]
    print(analizar_df(details))

    tiempos.set_index("order_id", inplace=True)
    tiempos.sort_values(by=["order_id"], inplace=True)

    indices_tiempos = list(tiempos.index)
    indices_details = list(details.index)
    lista = []
    for index in indices_details:
        if index in indices_tiempos and index not in lista:
            lista.append(index)
    details = details.loc[lista]

    # Podemos ver que hay más filas en details, ya que cada pedido
    # puede contener más de una pizza

    # Como hemos visto, este df tiene gran cantidad de datos que faltan, por lo que
    # deberemos rellenar estos o bien deshacernos de las filas no-fiables

    details["quantity"].replace({"one": 1, "One": 1, "two": 2, "Two": 2, "-1": 1, "-2": 2}, inplace=True)
    details.fillna(1, inplace=True)
    details = details.astype({"pizza_id": "string", "quantity": "int64"})

    # # Ahora, recuperemos los tipos de pizza
    pizzas = pd.read_csv("pizza_types.csv", sep=",", usecols=["pizza_type_id", "ingredients"], encoding="latin1")
    pizzas = pizzas.astype({"pizza_type_id": "string", "ingredients": "string"})
    print("Este dataframe no tiene ningún valor anómalo, lo cual nos permite no tener que limpiarlo")
    print("Sigue trabajando. Este intervalo será mayor, por favor no desista")

    dict_meses = {"01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril", "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto", "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"}

    dict_pizza_ing = {}  # Diccionario que relacionará cada tipo de pizza
    # con los ingredientes necesarios para prepararlos
    dict_ing = {}  # Diccionario que relacionará cada ingrediente
    # con la cantidad necesaria en cada mes. Tendrá 12 items, cada uno con
    # el número del mes como key y otro diccionario como valor
    for key in dict_meses.keys():
        dict_ing[key] = {}

    pizza_types = []

    for row in pizzas.index:  # Iteramos por cada fila (pizza) del dataset
        tipo = pizzas.loc[row]  # df.Series de la pizza en cuestión
        ingredientes = sacar_ing(tipo["ingredients"])
        pizza_types.append(tipo["pizza_type_id"])
        dict_pizza_ing[tipo["pizza_type_id"]] = ingredientes

    # Los nombres en details tienen algunos caracteres incorrectos
    # por lo que usaremos una función para formatearlos a nombres
    # presentes en el df pizzas
    corregir_nombres_pizzas()

    # Leemos el csv con los datos correctos
    # details = pd.read_csv("details1.csv")
    # details.rename(columns={"order_id ": "order_id"}, inplace=True)
    # print(details)
    # details.set_index("order_id", inplace=True)

    lista_details = list(details.index)
    lista_tiempos = list(tiempos.index)

    # Como podemos ver, hay elementos en tiempos que no están en details
    # Puesto que la necesidad más restrictiva es que estén en details (ya que
    # necesitamos ante todo el tipo de pizza que se ha pedido), eliminaremos
    # los elementos con índices que no aparezcan en details dentro de tiempo

    # Consigamos los elementos de tiempos que no están en details
    diff = list(set(set(lista_tiempos).difference(lista_details)))
    for i in diff:
        # Eliminamos aquellos pedidos de tiempos que no estén
        # contemplados en details
        tiempos.drop(i, inplace=True)

    # Ahora, ya tenemos los df con valores coincidentes.
    # Podemos trabajar con ellos
    pizzas_vendidas = {}  # #Pizzas vendidas cada mes
    tipos_pizza = {}  # #Pizzas de cada tipo
    # print(dict_pizza_ing)

    for i in range(details.shape[0]):
        row = details.iloc[i]
        order_id = row.name
        pizza = row[0]
        amount = row[1]
        mes = tiempos.loc[order_id][0]
        if dict_meses[mes] not in pizzas_vendidas.keys():
            pizzas_vendidas[dict_meses[mes]] = 0
        if pizza not in tipos_pizza.keys():
            tipos_pizza[pizza] = 0
        pizzas_vendidas[dict_meses[mes]] += amount
        tipos_pizza[pizza] += amount
        ing_mes = dict_ing[mes]
        for ing in dict_pizza_ing[pizza]:
            ing_mes[ing] += amount

    df = pd.DataFrame(dict_ing).T
    exportar_ingredientes(df)
    print("Se han exportado el stock semanal a un archivo",
          "de texto denominado stock_semanal.txt")
