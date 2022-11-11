import pandas as pd
import re

def extract():

    data = {}
    csvs = ['pizzas.csv', 'pizza_types.csv', 'orders.csv', 'order_details.csv', 'data_dictionary.csv']
    names = ['pizzas', 'pizza_types', 'orders', 'oder_details', 'data_dictionary']
    
    for file in csvs:
        index = csvs.index(file)
        df = pd.read_csv(file, encoding='latin')
        data[names[index]] = df
  
    return data

    
def analizar(title,df):
    '''
    Accedo a los datos y los voy escribiendo en un txt 
    '''
    file.write(f'\n\nAnalisis del dataframe {title}.csv :\n\n') 
    file.write(f'\nNombre del documento : {title}.csv ')
    columnas = df.columns.values
    num_c = len(columnas)

    file.write(f'\nNumero de columnas : {num_c}')
    file.write('\n--Analisis por columnas--')
    

    tipos = df.dtypes

    for columna in columnas:

        nans = df.isnull().sum()
        file.write(f'\n     Columna "{columna}"\n     Numero de NaN : {nans[columna]}')
        file.write(f'\n     Tipo de datos : {tipos[columna]}\n')
    return

if __name__ == '__main__':

    data = extract()

    with open(f'analisis', 'w') as file:

        file.write('\nAnalisis de la tipologia de datos presente en los csvs dados\n')
        file.write('\nEn este archivo de texto reflejaremos la informacion mas relevante sobre los csvs\n')
        file.write('utilizados para desarrollar el proyecto de recomendaciones a la empresa Maeven Pizzas.')
        file.write('\nEl analisis contendra una definicion exhaustiva de la tipologia del dato de cada columna por archivo.\n')

        for key in data.keys():
            df = data[key]
            analizar(key,df)
