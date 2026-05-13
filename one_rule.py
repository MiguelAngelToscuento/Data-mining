import oracledb

#one rule_8b
def one_rules(transactions, target):
    reglas= {}
    atributos = [key for key in transactions[0].keys() if key != target]
    for atributo in atributos:
        regla = {}
        error_atributo=0
        valores_atributo={}
        for row in transactions:
            valor= row[atributo]
            target_value = row[target]
            if valor not in valores_atributo:
                valores_atributo[valor]={}
            if target_value not in valores_atributo[valor]:
                valores_atributo[valor][target_value]=0
            valores_atributo[valor][target_value] +=1
       # print(f"Regla para atributo'{atributo}': {valores_atributo}")
        for valor, conteo in valores_atributo.items():
            clase_mayoritaria = max(conteo, key=conteo.get)
            regla[valor]=clase_mayoritaria
            total = sum(conteo.values())
            error_atributo += total - conteo[clase_mayoritaria]
            porcentaje_error = (total - conteo[clase_mayoritaria]) / total *100
        reglas[atributo]=(regla, error_atributo, porcentaje_error)

    m_atributo, (mejor_regla, error, porcentaje_error) = min (reglas.items(), key=lambda x: x[1][1])
    return m_atributo, mejor_regla, error, reglas

#one rule_8b
def cargar_transacciones(user, password, dsn, vm):
    try:
        conexion = oracledb.connect(user=user, password=password, dsn=dsn)
        cursor = conexion.cursor()
        cursor.execute(f"select * from {vm}")
        headers= [col[0]for col in cursor.description]
        transactions = [dict(zip(headers,row)) for row in cursor.fetchall()]
        cursor.close()
        conexion.close()
        print(f"Exito, se cargaron {len(transactions)} transacciones")
        return transactions
    except Exception as e:
        print("Error al cargar transacciones: ", e)
        return[]

user = "toscuento"
password = "migue"
dsn = "10.243.57.244/FREEPDB1"
vm = "LOTH.TITANIC_APRIORI"
transactions = cargar_transacciones(user, password, dsn, vm)

#impresion de primeras 5 transacciones

for row in transactions[:5]:
    print(row)

target = "ESTATUS_SUPERVIVENCIA"
m_atributo, mejor_regla, error, reglas= one_rules(transactions, target)
#impresion de resultados
print(f"\nEl mejor atributo es: {m_atributo}")
print(f"La mejor regla es: {mejor_regla}")
print(f"Errores: {error}")
#Resumen de reglas para cada articulo
print("\nResumen de reglas por atributo:")
for atributo, (regla, error_atributo, porcentaje_error) in reglas.items():
    print(f"Atributo: {atributo}, Regla: {regla}, Error: {error_atributo}, Porcentaje de Error: {porcentaje_error: .2f}%")