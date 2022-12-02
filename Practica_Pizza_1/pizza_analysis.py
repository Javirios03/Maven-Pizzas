import pandas as pd
import re
import csv


def analizar_tipologia(df: pd.DataFrame) -> None:
    '''Dado un dataframe, muestra los tipos de cada columna

    Parameters
    ----------
    df:
        pd.DataFrame

    Returns
    -------
    Nothing
    '''
    print(f"Esta es la tabla de tipos del dataframe {df.name}")
    print(df.info())


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
        if ing not in dict_ing:
            dict_ing[ing] = 0  # Inicializamos a 0 su cantidad necesaria
    return lista_ingredientes


def calculo_ingredientes() -> None:
    '''Se encargará de calcular el número de unidades de cada ingrediente
    que hará falta. Para ello, irá iterando por el dataframe de las "órdenes"

    Parameters
    ----------
    None

    Returns
    -------
    None
    '''
    # Iteramos por las listas que creamos anteriormente
    for i in range(len(lista_pizzas)):
        # pizza_name = re.sub("_[a-z]^_$", "", row["pizza_id"])  # Eliminamos
        # toda ocurrencia de '_"lo que sea"final de cadena' del nombre
        # pizza_name = re.sub("_[a-z][a-z]^_$", "", pizza_name)
        # pizza_name = re.sub("_[a-z][a-z][a-z]^_$", "", pizza_name)
        amount = lista_cantidades[i]

        # Queremos quedarnos sólo con el nombre de la pizza;
        # el tamaño no importa 😉. Por eso, usaremos Regex
        # Partiremos la cadena por _ y nos desharemos de la última parte
        # (aquella que tiene el tamaño)
        lista_cadena = re.split("_", lista_pizzas[i])

        string = ""
        for i in range(len(lista_cadena)-1):
            string += lista_cadena[i] + "_"

        # Quitamos la última barra baja, que no hace falta
        pizza_name = string[:-1]

        for ingredient in dict_pizza_ing[pizza_name]:
            dict_ing[ingredient] += amount


def panel_ingredientes(dict_ing: dict) -> str:
    '''Dado un diccionario de todos los ingredientes,
    construirá la cadena que muestra la cantidad

    Parameters
    ----------
    dict_ing:
        dict; Sus claves son cadenas (nombre ingrediente)
        y los valores enteros (unidades de tal ingrediente)

    Returns
    -------
    string:
        str; Cadena que se visualizará
    '''
    string = "Cada semana, harán falta:\n"
    # El cálculo que se hizo anteriormente fue con datos de todo un año.
    # Dado que el cliente quiere conocer la necesidad semanal, tenemos dos
    # opciones: O bien lo hacemos correctamente, separando cada semana,
    # o bien, como voy a hacer, lo hacemos de forma chapucera sacando la media

    for key in dict_ing.keys():
        # Dado que hay una media de 52,1429 semanas en un año:
        string += f"\t- {str(key)}: {int(dict_ing[key]//52.1429)}\n"
    return string


def write_csv():
    keys = list(dict_ing.keys())
    values = list(dict_ing.values())
    data = []
    for i in range(len(keys)):
        data.append([keys[i], int(values[i]//52.1429)])
    with open("compras_semana.csv", "w", newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Ingredient", "amount"])
        writer.writerows(data)


if __name__ == "__main__":
    # details has the order details (pizza_id and quantity)
    # We will only save the relevant information of the dataset.
    # In this case, it is the pizza_id and the quantity
    details = pd.read_csv("order_details.csv")[["pizza_id", "quantity"]]
    details.name = "details"

    # El acceso a un dataframe es muy costoso computacionalmente, por lo que
    # lleva mucho tiempo. Para evitar esto, jugaremos con listas de los datos,
    # cuyo acceso es más simple???
    lista_pizzas = details["pizza_id"].to_list()
    lista_cantidades = details["quantity"].to_list()

    # data_dict = pd.read_csv("data_dictionary.csv")
    # data_dict.name = "data_dict"

    orders = pd.read_csv("orders.csv")

    # pizza_types specifies the category and ingredients info
    # We will only save the relevant information of the dataset.
    # In this case, it is the pizza_id and the ingredients
    pizza = pd.read_csv("pizza_types.csv")[["pizza_type_id", "ingredients"]]
    pizza.name = "pizza"

    pizzas = pd.read_csv("pizzas.csv")

    print("Una vez cargados los datasets, procedemos a evaluar la calidad de",
          "los datos proporcionados\n")

    analizar_tipologia(details)
    print("\nComo podemos ver, la tabla de tipos no es del todo correcta, ya",
          "que pandas no ha podido determinar el tipo de pizza_id, a pesar de",
          "que debería de ser string. Por ello, vamos a cambiarlo manualmente\n")
    details = details.astype({"pizza_id": "string", "quantity": "int64"})

    analizar_tipologia(pizza)
    print("En este caso, ha tenido problemas reconociendo ambos. Como podemos",
          "comprobar en el csv original, ambos deberían ser strings\n")
    pizza = pizza.astype({"pizza_type_id": "string", "ingredients": "string"})

    print("Ahora, comprobemos si existen valores anómalos en los datasets")
    print(f"Nans del dataset details:\n {details.isnull().sum()}\n")
    print(f"Nans del dataset pizza:\n {pizza.isnull().sum()}")
    print("Asimismo, este es el número de nulls en cada dataset:",
          f"\n{details.isna().sum()}\n{pizza.isna().sum()}")
    print("Este resultado es satisfactorio, ya que podemos afirmar que toda",
          "la información es válida")

    # A partir de aquí, se procederá a interpretar la información
    # para obtener los ingredientes

    dict_pizza_ing = {}  # Diccionario que relacionará cada tipo de pizza
    # con los ingredientes necesarios para prepararlos
    dict_ing = {}  # Diccionario que relacionará cada ingrediente
    # con la cantidad necesaria

    for row in pizza.index:  # Iteramos por cada fila (pizza) del dataset
        tipo = pizza.loc[row]  # df.Series de la pizza en cuestión
        ingredientes = sacar_ing(tipo["ingredients"])
        dict_pizza_ing[tipo["pizza_type_id"]] = ingredientes

    # Ahora, se calcularán los ingredientes
    calculo_ingredientes()
    write_csv()
    print("\nA continuación, se mostrará la lista de ingredientes necesarios para stock\n")
    print(panel_ingredientes(dict_ing))
