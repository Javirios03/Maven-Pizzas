from fpdf import FPDF
import pandas as pd


class PDF(FPDF):
    def header(self):
        # Logo
        self.image('LOGO_NUEVO_WEB.jpg', 10, 8, 33)
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(15, 10, 'Reporte Ejecutivo Mavens Pizza', 0, 0, 'C')
        # Line break
        self.ln(30)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')


if __name__ == "__main__":
    # Instantiation of inherited class
    pdf = PDF()

    ingredientes = pd.read_csv("Ingredientes_Meses.csv")
    ingredientes.rename(columns={"Unnamed: 0": "Ingredients"}, inplace=True)
    ingredientes.set_index("Ingredients", inplace=True)

    lista_ingredientes = ingredientes.index.values.tolist()
    # print(lista_ingredientes)
    meses = [ingredientes.columns.tolist()[i] for i in range(12)]
    strings = []

    ingredientes_meses = {}  # Contendrá la cantidad de todos los ingredientes
    for mes in meses:
        ingredientes_meses[mes] = ingredientes[mes].tolist()
        string = ""
        for i in range(len(lista_ingredientes)):
            string += lista_ingredientes[i] + ": " + str(
                ingredientes_meses[mes][i]) + ", "
        string = string[:-2]+"\n\n"
        strings.append(string)

    pdf.add_page()
    for i in range(len(strings)):
        string = strings[i]
        mes = meses[i]
        pdf.set_font("Times", "B", 14)
        # cell(width, height, string, border)
        pdf.cell(0, 0, mes, align="C")
        pdf.set_font("Times", "", 12)
        pdf.write(6, string)

    pdf.alias_nb_pages()

    pdf.output("yourfile.pdf", "F")
