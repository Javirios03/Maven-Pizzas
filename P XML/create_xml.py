from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom
import pandas as pd

def prettify(elem: Element):
    '''Return a pretty-printed XML string for the element
    '''
    # print(str(elem))
    rough_string = tostring(elem, encoding='latin1')
    print(rough_string.decode())
    print()
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ")


def generateXML(tipos_actuales: dict, tipos_deseados: dict) -> None:
    # Create the network XML file tree
    top = Element('types')
    cadena = 'Este archivo XML presenta los tipos de dato presentes '
    cadena += 'en las columnas de los 3 dataframes usados en '
    cadena += 'la practica de Pizzas Maven'
    comment = Comment(cadena)
    top.append(comment)
    for i in range(3):
        df = SubElement(top, str(nombres[i]))
        dict_tipos = tipos_actuales[nombres[i]]
        dict_deseados = tipos_deseados[nombres[i]]
        for column in dict_tipos.keys():
            dtype_org = dict_tipos[column]
            dtype_deseado = dict_deseados[column]
            comment = "Columna '" + str(column)
            df.append(Comment(comment))
            tipo_org = SubElement(df, "Actual")
            tipo_org.text = dtype_org
            tipo_des = SubElement(df, "Deseado")
            tipo_des.text = dtype_deseado

    print(prettify(top))


if __name__ == "__main__":
    tiempos = pd.read_csv("orders.csv", sep=";", encoding="latin1")
    pizzas = pd.read_csv("order_details.csv", sep=";", encoding="latin1")
    tipos = pd.read_csv("pizza_types.csv", sep=",", encoding="latin1")

    nombres = ["orders.csv", "order_details.csv", "pizza_types.csv"]
    dfs = [tiempos, pizzas, tipos]
    tipos_columna = {}
    querido = {}
    # Extraemos todos los dtypes y los ponemos en un diccionario
    # para mayor facilidad a la hora del manejo
    for i in range(len(dfs)):
        df = dfs[i]
        name = nombres[i]
        tipos_columna[name] = df.dtypes.astype(str).to_dict()
        querido[name] = df.dtypes.astype(str).to_dict()
    
    # print(tipos_columna)

    
    querido["orders.csv"]["order_id"] = "str"
    querido["orders.csv"]["date"] = "str"
    querido["order_details.csv"]["pizza_id"] = "str"
    querido["order_details.csv"]["quantity"] = "int64"
    querido["pizza_types.csv"]["pizza_type_id"] = "str"
    querido["pizza_types.csv"]["name"] = "str"
    querido["pizza_types.csv"]["category"] = "str"
    querido["pizza_types.csv"]["ingredients"] = "str"
    generateXML(tipos_columna, querido)
