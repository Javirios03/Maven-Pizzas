import pandas as pd
import matplotlib.pyplot as plt
import csv


def hacer_graficas():
    '''Obtiene las gráficas que se usarán posteriormente
    en el reporte ejecutivo. Para ello, usará csv's y plt,
    exportándolos como imágenes .png
    '''
    # Gráfica pizzas vendidas
    with open("pizzas_vendidas.csv") as f:
        pizzas_vendidas = csv.DictReader(f)

        for row in pizzas_vendidas:
            pizzas_vendidas = row
            print(pizzas_vendidas)

    for key, value in row.items():
        pizzas_vendidas[key] = int(value)

    plt.figure(figsize=(14, 8))
    plt.plot(list(pizzas_vendidas.keys()), list(pizzas_vendidas.values()),
             marker='o')
    plt.xlabel("Mes")
    plt.ylabel("Número de pizzas vendidas")
    plt.title("Pizzas vendidas a lo largo de 2016")
    plt.savefig("Evolución_mensual.png")

    # 10 pizzas más vendidas
    with open("tipos_pizza.csv") as f:
        tipos_pizza = csv.DictReader(f)

        for row in tipos_pizza:
            tipos_pizza = row

    for key, value in tipos_pizza.items():
        tipos_pizza[key] = int(value)

    diez_pizzas = [[], []]
    keys, values = list(tipos_pizza.keys()), list(tipos_pizza.values())
    while len(diez_pizzas[0]) < 10:
        idx = values.index(max(values))
        name = keys[idx]
        diez_pizzas[0].append(name)
        diez_pizzas[1].append(tipos_pizza[name])
        keys.pop(idx)
        values.pop(idx)

    plt.figure(figsize=(16, 8))
    plt.bar(diez_pizzas[0], diez_pizzas[1])
    plt.title("10 pizzas más vendidas")
    plt.xlabel("Tipo de pizza")
    plt.ylabel("Número total de ventas")
    plt.savefig("Top10Pizzas.png")


def reporte_ejecutivo():
    '''Se encarga de gestionar las acciones necesarias para crear
    la página 'Reporte Ejecutivo', compuesta por gráficas que
    determinan cómo ha ido 2016 en Maven
    '''
    workbook = writer.book
    workbook.add_worksheet("Reporte Ejecutivo")
    worksheet = writer.sheets['Reporte Ejecutivo']
    worksheet.insert_image('A2', 'Evolución_mensual.png')

    cell_format = workbook.add_format()
    cell_format.set_bold()
    cell_format.set_font_color('red')
    worksheet.write("J42", "Evolución mensual de las ventas - 2016",
                    cell_format)
    worksheet.insert_image("A46", "Top10Pizzas.png")
    worksheet.write("K87", "10 pizzas más vendidas a lo largo del año",
                    cell_format)


def get_col_widths(dataframe):
    '''Función que se usará para cambiar el tamaño de las
    celdas en el excel, tomando el tamaño de las cadenas en
    cada columna y cambiando el tamaño de esas columnas
    '''
    # First we find the maximum length of the index column
    idx_max = max([len(str(s)) for s in dataframe.index.values] +
                  [len(str(dataframe.index.name))])
    # Then, we concatenate this to the max of the lengths of column
    #  name and its values for each column, left to right
    return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] +
                            [len(col)]) for col in dataframe.columns]


def reporte_ingredientes():
    '''Función que llevará a cabo los comandos necesarios
    para crear la página 'Reporte Ingredientes' del Excel,
    concerniente a la necesidad de stock para cada mes
    '''
    df = pd.read_csv("Ingredientes_Meses.csv")
    df.rename(columns={"Unnamed: 0": "Ingredients/Months"}, inplace=True)
    df.set_index("Ingredients/Months", inplace=True)

    workbook = writer.book
    workbook.add_worksheet("Reporte Ingredientes")
    worksheet = writer.sheets['Reporte Ingredientes']
    df.to_excel(writer, sheet_name="Reporte Ingredientes")
    (max_row, max_col) = df.shape
    worksheet.conditional_format(1, 1, max_row, max_col,
                                 {'type': '3_color_scale'})
    for i, width in enumerate(get_col_widths(df)):
        worksheet.set_column(i, i, width)
    for i in range(1, 13):
        worksheet.set_column(i, i, 10)


def reporte_pedidos():
    '''Empleada para escribir en el Excel los datos
    concernientes a la página "Reporte Pedidos", datos
    relacionados con lo temporal de los pedidos en Maven
    '''
    workbook = writer.book
    workbook.add_worksheet("Reporte Pedidos")
    worksheet = writer.sheets['Reporte Pedidos']

    tiempos = pd.read_csv("tiempos.csv")
    tiempos.rename(columns={"order_id ": "order_id"}, inplace=True)
    tiempos.set_index("order_id", inplace=True)
    tiempos.sort_index(inplace=True)
    details = pd.read_csv("details1.csv")
    details.set_index("order_id", inplace=True)

    lista_details = list(details.index)
    lista_tiempos = list(tiempos.index)
    diff = list(set(set(lista_tiempos).difference(lista_details)))
    for i in diff:
        # Eliminamos aquellos pedidos de tiempos que no estén
        # contemplados en details
        tiempos.drop(i, inplace=True)

    tiempos[["Year", "Month", "Day"]] = tiempos.date.str.split(", ",
                                                               expand=True)
    # Eliminamos las columnas que no nos sirven de nada
    del tiempos["date"]
    del tiempos["Year"]
    del tiempos["Day"]

    dict_meses = {"01": {}, "02": {}, "03": {}, "04": {}, "05": {}, "06": {},
                  "07": {}, "08": {}, "09": {}, "10": {}, "11": {}, "12": {}}

    for i in range(details.shape[0]):
        row = details.iloc[i]
        mes = tiempos.loc[row.name].Month
        amount = row.quantity
        if row.pizza_id not in dict_meses[mes]:
            dict_meses[mes][row.pizza_id] = 0
        dict_meses[mes][row.pizza_id] += amount

    # Filas: meses, columnas: Pizzas
    df = pd.DataFrame(data=dict_meses)
    df = df.T
    df.to_excel(writer, sheet_name="Reporte Pedidos")

    for i, width in enumerate(get_col_widths(df)):
        worksheet.set_column(i, i, width)

    max_por_mes = []
    for mes in list(dict_meses.values()):
        valores = list(mes.values())
        max_por_mes.append(max(valores))

    format1 = workbook.add_format({'bg_color': '#87ceeb'})
    worksheet.conditional_format(7, 0, 7, 32, {'type': 'cell',
                                               'criteria': '>=',
                                               'value': 0,
                                               'format': format1})

    format2 = workbook.add_format({'bold': 1, 'italic': 1,
                                   'bg_color': '#fa8072'})
    for i in range(1, 13):
        value = max_por_mes[i-1]
        worksheet.conditional_format(i, 1, i, 32, {'type':     'cell',
                                                   'criteria': '>=',
                                                   'value': value,
                                                   'format': format2})
    cell_format = workbook.add_format({'font_size': 14, "underline": 1})
    worksheet.write("G16", "Esta tabla muestra las ventas de cada pizza a lo" +
                    "largo del año. En rojo, se pueden observar las pizzas" +
                    " más vendidas en cada mes. Adicionalmente, la fila " +
                    "en azul es el mes con más ventas en general", cell_format)


if __name__ == "__main__":
    with pd.ExcelWriter("Maven_Pizzas.xlsx", engine="xlsxwriter") as writer:
        hacer_graficas()
        reporte_ejecutivo()
        reporte_ingredientes()
        reporte_pedidos()
