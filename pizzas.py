import pandas as pd
import calendar
import re
from statistics import mode 



def extract():
    data = {}
    csvs = ['pizzas.csv', 'pizza_types.csv', 'orders.csv', 'order_details.csv', 'data_dictionary.csv']
    names = ['pizzas', 'pizza_types', 'orders', 'order_details', 'data_dictionary']
    
    for file in csvs:
        index = csvs.index(file)
        df = pd.read_csv(file, encoding='latin')
        data[names[index]] = df
  
    return data

def pasar_str(lista):

    semana = []
    
    for date in lista:
        cadena = ''
        
        if int(date.day) < 10 :
            dia = '0'+ str(date.day)
        else:
            dia = str(date.day)

        if int(date.month) < 10 :
            mes = '0' + str(date.month)
        else:
            mes = str(date.month)
            
        
        cadena += dia + '/' + mes + '/' + str(date.year)
        semana.append(cadena)

    return semana

def crear_calendar():

    cal = calendar.Calendar()
    cal.setfirstweekday(0)
    año_tmp = []
    año_fin = {}
    count = 1

    for mes in range(1,13):

        sem_list = cal.monthdatescalendar(2015,mes)

        for semana in sem_list:

            sem_final = pasar_str(semana)

            año_tmp.append(sem_final)
    
    '''
    Quitamos la primera y última semana del año ya que contienen
    datos de otros años y, por tanto, no son comparables las modas
    a calcular del resto de semanas
    '''
    año_tmp.pop(0)
    año_tmp.pop(-1)


    for index in range(0,len(año_tmp)):

        if index != len(año_tmp)-1:

            if año_tmp[index] != año_tmp[index+1]:

                año_fin[count] = año_tmp[index]
                count += 1

    '''
    for key in año_fin.keys():
        print(f' {key} -> {año_fin[key]}')
    '''      
    return año_fin

def create_df(names,columns):

    df = pd.DataFrame()
    for a in range(0,len(names)):
        df[names[a]] = columns[a]

    return df


def transform(data,año):
    '''
    Vamos a analizar los datos dados de la siguiente manera:
    Analizaremos los pedidos por semanas, calculando para cada una de ellas el número de pizzas 
    pedidas por cada tipo. Posteriormente, calcularemos la moda de entre los valores calculados para cada pizza
    y así elaboraremos nuestra predicción semanal

    En cuanto a la separación por semanas, partimos de la base de que conocemos
    que el 1 de enero de 2015(fecha de inicio de los datos) es jueves, por lo que comenzaremos a tener en cuenta 
    semanas completas desde el día 5 (lunes, incluido)

    '''

    # Cargamos datos
    
    df_types = data['pizza_types']
    df_orders = data['orders']
    df_odetails = data['order_details']

    semanas = list(año.values())

    # Creamos el diccionario por tipo de pizzas para guardar las modas por semanas en una lista

    modas_pizzas={}

    for tipo in df_types['pizza_type_id']:
        modas_pizzas[tipo] = [0 for x in range(0,len(semanas))]

    
    # Hacemos los cálculos para cada semana

    for sem_index in range(0,len(semanas)):
        semana = semanas[sem_index]
        order_ids = []

        for index in range(0,len(df_orders['order_id'])):

            if df_orders['date'][index] in semana:

                order_ids.append(df_orders['order_id'][index])
        
        # Ahora obtendremos las cantidades pedidas por pizzas

        for index in range(0,len(df_odetails['order_id'])):

            if df_odetails['order_id'][index] in order_ids:

                '''
                Asumimos las siguientes ponderaciones para tener en cuenta los tamaños 
                en el número de pizzas pedidas por tipo:

                Si se pide una pizza de tamaño s -> El nº de pizzas pedidas aumenta en 1
                Si se pide una pizza de tamaño m -> El nº de pizzas pedidas aumenta en 1,5
                Si se pide una pizza de tamaño l -> El nº de pizzas pedidas aumenta en 2
                Si se pide una pizza de tamaño xl -> El nº de pizzas pedidas aumenta en 2,5
                Si se pide una pizza de tamaño xxl -> El nº de pizzas pedidas aumenta en 3

                Para calcular la moda posteriormente aplicaremos el casteo a int
                
                '''
                pizza = str(df_odetails['pizza_id'][index])

                tamaño = re.findall('[a-z]+$',pizza)

                separador = '_' + tamaño[0]

                pizza_datos = re.split(separador+'$' , pizza )
                pizza_filtrada = pizza_datos[0]

                if tamaño[0] == 's':
                    (modas_pizzas[pizza_filtrada])[sem_index] += 1

                elif tamaño[0] == 'm':
                    (modas_pizzas[pizza_filtrada])[sem_index] += 2
                    
                elif tamaño[0] == 'l':
                    (modas_pizzas[pizza_filtrada])[sem_index] += 3
                    
                elif tamaño[0] == 'xl':
                    (modas_pizzas[pizza_filtrada])[sem_index] += 4
                    
                elif tamaño[0] == 'xxl':
                    (modas_pizzas[pizza_filtrada])[sem_index] += 5 

    # Calculamos las modas anuales de cada pizza
    modas = []
    for value in modas_pizzas.values():
        moda = mode(value)
        modas.append(moda)

    # Trabajamos en la creación del dataframe que elaboraremos junto a la predicción
    tipos = list(df_types['pizza_type_id'])
    

    names = ['Tipo_pizza' , 'Moda_anual' ]
    columns = [tipos, modas]

    # Sacamos los valores por semanas

    for index in range(0,len(semanas)):
        semana = []
        for key in modas_pizzas.keys():
            semana.append(int(modas_pizzas[key][index]))

        names.append(f'Semana {index}')
        columns.append(semana)

    df = create_df(names,columns)

    return df,tipos

def load(df,tipos):

    '''
    Vamos a calcular la predicción de ingredientes para Maeven Pizzas 
    basándonos en que, semanalmente, debería pedir los ingredientes 
    que sirven para hacer el número de pizzas de cada tipo que indica 
    la moda de dicho tipo.

    Para ello primero extraemos los ingredientes a un diccionario con
    su tipo de pizza como clave y luego multiplicamos por la moda de cada
    tipo. 

    Finalmente, crearemos un nuevo dataframe que incluya la predicción
    '''

    ing_por_tipos = data['pizza_types']['ingredients']

    ing_dict = {}
    mozzarella = 'Mozzarella Cheese'
    t_sauce = 'Tomato Sauce'

    ing_dict[mozzarella] = 0
    ing_dict[t_sauce] = 0

    for index in range(len(tipos)):
        not_sauce = 0
        lista = re.split(', ',ing_por_tipos[index])

        for ingrediente in lista:
                
            if re.search('sauce', ingrediente, re.I):
                not_sauce = 1

            if ingrediente not in ing_dict.keys():
                ing_dict[ingrediente] = df['Moda_anual'][index]

            else:
                ing_dict[ingrediente] += df['Moda_anual'][index]

            # Controlamos el hecho de que todas lleven mozzarella y salsa de tomate (si no se especifica otra)

        if mozzarella not in lista:
            ing_dict['Mozzarella Cheese'] += df['Moda_anual'][index]

        if not_sauce == 0:
            ing_dict['Tomato Sauce'] += df['Moda_anual'][index]

    names_i = ['Ingredientes','Unidades a comprar']
    columns_i = [ing_dict.keys(),ing_dict.values()]

    df_recom = create_df(names_i,columns_i)
    print(df_recom)

    df_recom.to_csv('recomendacion_ingredientes.csv')
    df.to_csv('analisis_pedidos_semanales.csv')

    return df, df_recom


if __name__ == '__main__':

    print('\nProcedemos a calcular el calendario')
    año_dic = crear_calendar()
    
    print('\nVamos a analizar los datos')
    data = extract()

    df , tipos= transform(data,año_dic)
    print('Se ha procesado el primer df')

    df , df_recom = load(df , tipos)


        


