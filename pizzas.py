import pandas as pd
import re

def create_df(names,columns):

    df = pd.DataFrame()
    for a in range(0,len(names)):
        df[names[a]] = columns[a]

    return df

def extract():
    
    df_pizzas = pd.read_csv('pizzas.csv', encoding='latin')
    df_ptypes= pd.read_csv('pizza_types.csv', encoding='latin')
    df_orders = pd.read_csv('orders.csv', encoding='latin')
    df_odetails = pd.read_csv('order_details.csv', encoding='latin')
    df_dict = pd.read_csv('data_dictionary.csv', encoding='latin')
    

    return df_pizzas,df_ptypes,df_orders,df_odetails,df_dict

def transform(df_pizzas,df_ptypes,df_orders,df_odetails,df_dict):
    '''
    Vamos a tomar como base la última semana completa del dataset de pedidos, es decir, la 
    semana del 21 al 27 de diciembre de 2015 (ambos incluidos)
    
    '''

    ## Saco los order_id de los orders de la semana a estudiar

    filas = []
    chosen_week = [f'2{x}/12/2015' for x in range(1,8)]
    

    for i in range(len(df_orders['date'])):
        if df_orders['date'][i] in chosen_week :
            filas.append(i)

    df_week = df_orders.iloc[filas[0] : filas[len(filas)-1]]
    orders_id = list(df_week['order_id'])
    

    ## Saco los tipos de pizza generales y sus ingredientes ( coinciden en índice ) 

    p_types = list(df_ptypes['pizza_type_id'])


    p_ingredients = []
    temporal_ingredients = list(df_ptypes['ingredients'])

    for lista in temporal_ingredients:
        ingredientes = re.split(', ', lista)
        p_ingredients.append(ingredientes)

    ## Creo un diccionario con los tipos de pizza que incluyan el tamaño de esta

    p_types_tam_dict = {}

    for type in df_pizzas['pizza_id']:
        p_types_tam_dict[type] = 0
    
    
    ## Saco el número de pizzas de cada tipo pedidas en las fechas seleccionadas y las meto en el diccionario
    
    for a in range(len(df_odetails['order_id'])):

        if df_odetails['order_id'][a] in orders_id:

            for pizza in p_types_tam_dict.keys():

                if df_odetails['pizza_id'][a] == pizza:
                    
                    p_types_tam_dict[pizza] += df_odetails['quantity'][a]


    ''' 
    En este punto tenemos :

    orders_id -> Lista con los orders_id de los pedidos de la semana
    p_types -> Lista con los tipos de pizza generales
    p_ingredients -> Lista de listas en las que tenemos los ingredientes por tipo genérico de pizza
    p_types_tam_dict -> Diccionario con el número de pizzas por tipo y tamaño pedidas en el periodo estudiado

    Para simplificar el acceso al número de pizzas creamos diferentes columnas para unirlo en un único dataset

    columna1 = p_types
    columna2 = ingredientes por tipo
    columna3 = cantidad de S
    columna4 = cantidad de m
    columna5 = cantidad de l
    columna6 = cantidad de xl
    columna7 = cantidad de xxl
    columna8 = cantidad total

    '''

    cantidad_s = []
    cantidad_m = []
    cantidad_l = []
    cantidad_xl = []
    cantidad_xxl = []
    
    listas_cant = [cantidad_s,cantidad_m,cantidad_l,cantidad_xl,cantidad_xxl]

    for type in p_types:

        tams_p = [0 for x in range(0,5)]                        # Lo creo para que se añada un 0 a las listas en las que no haya un dterminado tamaño para una pizza

        for p_tamaño in p_types_tam_dict.keys():

            if re.findall(type,p_tamaño) == [type]:

                tamaño = re.findall('[a-z]+$',p_tamaño)
                #print(f'{p_tamaño} --> Tamaño: {tamaño}')

                if tamaño[0] == 's':
                    cantidad_s.append(p_types_tam_dict[p_tamaño])
                    tams_p[0] +=1
                    
                elif tamaño[0] == 'm':
                    cantidad_m.append(p_types_tam_dict[p_tamaño])
                    tams_p[1] +=1

                elif tamaño[0] == 'l':
                    cantidad_l.append(p_types_tam_dict[p_tamaño])
                    tams_p[2] +=1

                elif tamaño[0] == 'xl':
                    cantidad_xl.append(p_types_tam_dict[p_tamaño])
                    tams_p[3] +=1

                elif tamaño[0] == 'xxl':
                    cantidad_xxl.append(p_types_tam_dict[p_tamaño])
                    tams_p[4] +=1

        # Voy a gestionar que todas las listas tengan la misma longitud 
        # de manera que si no se ha añadido un valor a la lista de un tamaño
        # porque no exista dicho tamaño para la pizza, añado a la lista de ese tamaño un 0
        # para que la longitud se mantenga igual
        
        
        for d in range(0,len(tams_p)):                                  
            if tams_p[d] == 0:
                listas_cant[d].append(0)


    # Creamos cantidad_total como suma de las otras columnas

    
    ## Creo el dataframe con las columnas creadas

    names = ['Pizzas','Ingredientes','Cantidades S','Cantidades M','Cantidades L','Cantidades XL','Cantidades XXL']
    columns = [p_types,p_ingredients,cantidad_s, cantidad_m,cantidad_l, cantidad_xl,cantidad_xxl]
    df_procesado = create_df(names,columns)
   
    print(df_procesado)

    return df_procesado

def load(df_procesado):

    '''
    Voy a crear una columna que sume la cantidad de ingredientes necesarios por tipo de pizza
    Vamos a asumir que por cada tamaño añadimos x ingredientes:
    S -> x= 1
    M -> x= 1,5
    L -> x= 2
    XL -> x= 2,5
    XXL -> x= 3

    '''
    cantidad_total = 1*df_procesado['Cantidades S'] + (1.5)*df_procesado['Cantidades M'] + (2)*df_procesado['Cantidades L'] + (2.5)*df_procesado['Cantidades XL'] + (3)*df_procesado['Cantidades XXL']

    df_procesado['Cantidad a pedir (ponderada)'] = cantidad_total
    #print(df_procesado)

    ## Buscamos crear un diccionario con cantidad por ingredientes
    ingredientes_dict = {}
    mozzarella = 'Mozzarella Cheese'
    t_sauce = 'Tomato Sauce'

    ingredientes_dict[mozzarella] = 0
    ingredientes_dict[t_sauce] = 0

    for index in range(0,len(df_procesado['Ingredientes'])):

        not_sauce = 0

        lista = df_procesado['Ingredientes'][index]

        for ingrediente in lista:
            
            if re.search('sauce', ingrediente, re.I):

                not_sauce = 1

            if ingrediente not in ingredientes_dict.keys():

                ingredientes_dict[ingrediente] = df_procesado['Cantidad a pedir (ponderada)'][index]

            else:

                ingredientes_dict[ingrediente] += df_procesado['Cantidad a pedir (ponderada)'][index]


        # Controlamos el hecho de que todas lleven mozzarella y salsa de tomate (si no se especifica otra)

        if mozzarella not in lista:
            ingredientes_dict[mozzarella] += df_procesado['Cantidad a pedir (ponderada)'][index]

        if not_sauce == 0:
            ingredientes_dict[t_sauce] += df_procesado['Cantidad a pedir (ponderada)'][index]


    # Creo un dataset a partir del diccionario que acabo de crear para presentárselo al cliente 

    names_i = ['Ingredientes','Unidades a comprar']
    columns_i = [ingredientes_dict.keys(),ingredientes_dict.values()]
    df_ingredients = create_df(names_i,columns_i)

    print(df_ingredients)


    # Guardo los dtaframes en csvs para que sea de facil acceso para el cliente

    df_ingredients.to_csv('estimacion_ingredientes.csv')
    df_procesado.to_csv('analisis_pedidos.csv')

    return df_ingredients, df_procesado


if __name__ == '__main__':

    '''
    Este programa analizará los pedidos de la empresa Maeven Pizzas 
    a lo largo de la semana del 21 al 27 de diciembre de 2015. 
    Una vez analizados,creará dos archivos .csv, uno con los ingredientes que 
    se estima debería comprar para la siguiente semana, y otro con el análisis de los pedidos de la semana,
    incluyendo en el mismo el tipo de pizza, sus ingredientes, la cantidad pedida por tamaños y la cantidad
    de ingredientes necesarios (según las ponderaciones por tamaños)

    '''
    df_pizzas,df_ptypes,df_orders,df_odetails,df_dict = extract()
    df_procesado = transform(df_pizzas,df_ptypes,df_orders,df_odetails,df_dict)
    df_ingredients,df_procesado = load(df_procesado)

