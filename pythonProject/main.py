import openai
import csv
import re


# Set up OpenAI API credentials
openai.api_key = "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"

# Context for generator
#messages = "role: system, content: You are an AI program that extract information from a email given next and fill this" \
#           " camps and anything else if is not found put null and not change following tags -> company_name: , job_description:, email_intention_description:(classified between rejection, no rejection, futher action, no related to job application)"

messages = """Role: Analista, contexto: es una encuesta para analisar la satifaccion gastronomica del cliente.
            Se requiere analisar el comentario y clasificarlo en una de las siguientes
            Categorías relevantes:

            Temperatura de los alimentos
            Variedad en el menú
            variedad de las ensaladas y verduras
            Variedad en la preparación de proteínas
            Atención y servicio al cliente es Positivo
            Atención y servicio al cliente es Negativo
            Tamaño y consistencia de las porciones de comida
            Calidad en la comida
            No hay opciones vegetarianas
            No hay opciones de comida de mar
            Ventilación del lugar
            Porción inadecuada de sopa en el almuerzo.
            Porción inadecuada de cebolla
            
            Nota: indicar solo la categoria relevate a la que pertenece el comentario,si pertenece a mas de una categoria separar con comas """


def read_csv():

    # Open the CSV file and loop through each row
    with open(r'C:\Users\sebas\Desktop\Workspace\JobSearchNinja\My_Staff\pythonProject\comments.csv') as csvfile:
        reader = csv.reader(csvfile)
        next(reader) # skip the headers
        with open(r'C:\Users\sebas\Desktop\Workspace\JobSearchNinja\My_Staff\pythonProject\output.csv', mode='w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(['comment', 'response']) # write the headers
            for row in reader:
                comment = ""
                # Get the value in the first column of the row and append it to email_body
                comment += row[0] + "\n"
                response = generate_response(messages, comment)
                categorias= extraer_categorias(response)
                #company_name, job_description, email_intention = extract_info_from_string(response)
                print("-----------------comment-------------------")
                print(comment)
                print("-----------------Generated Data-------------------")
                print(response)
                print("-----------------Extracted data-------------------")
                print(categorias[0])
                print(categorias[1])
                print(categorias[2])
                print(categorias[3])
                print(categorias[4])
                print(categorias[5])
                print(categorias[6])
                print(categorias[7])
                print(categorias[8])
                print(categorias[9])
                print("-----------------New data-------------------")
                writer.writerow([comment, response, categorias[0], categorias[1], categorias[2], categorias[3],
                                 categorias[4], categorias[5], categorias[6], categorias[7], categorias[8], categorias[9]])  # write the data to the output file


# Define function to generate response to user message
def generate_response(messages, comment):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=messages+" "+comment,
        temperature=0,
        max_tokens=100,
        top_p=0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    return response.choices[0].text

# Example usage

def extraer_categorias(texto):

    categorias = texto.split(",")[:10]  # Separar las categorías por coma y tomar las primeras 10
    categorias = [cat.strip() for cat in
                  categorias]  # Eliminar espacios en blanco al inicio y final de cada categoría
    if len(categorias) < 10:  # Si hay menos de 10 categorías, agregar "N/A" hasta completar 10
        categorias += ["N/A"] * (10 - len(categorias))
    return categorias





#testing_email_body()
read_csv()

