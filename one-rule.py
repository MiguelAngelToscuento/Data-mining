# libreria para conectarnos a oracle database
import oracledb

# one - rule
def one_rule(transactions, target):
    reglas = {}
    atributos = [key for key in transactions[0].keys() if key != target]
    for atributo in atributos:
        regla = {}
        error_atributo = 0
        valores_atributo = {}
        for row in transactions:
            valor = row[atributo]
            target_value = row[target]
            if valor not in valores_atributo:
                valores_atributo[valor] = {}
            if target_value not in valores_atributo[valor]:
                valores_atributo[valor][target_value] = 0
            valores_atributo[valor][target_value] += 1
        #print(f"Reglas para atributo '{atributo}': {valores_atributo}")
        for valor, conteo in valores_atributo.items():
            clase_mayoritaria = max(conteo, key = conteo.get)
            regla[valor] = clase_mayoritaria
            total = sum(conteo.values())
            error_atributo += total - conteo[clase_mayoritaria]
        reglas[atributo] = (regla, error_atributo)
    m_atributo, (mejor_regla, error) = min(reglas.items(), key=lambda x: x[1][1])
    return m_atributo, mejor_regla, error, reglas

def cargar_transacciones(user, password, dsn, vm):
    try:
        conexion = oracledb.connect(user=user, password=password, dsn=dsn)
        cursor = conexion.cursor()
        cursor.execute(f"select * from {vm}")
        headers = [col[0] for col in cursor.description] # nombres de cada columna
        # Convierte cada fila en un set y se salta los valores nulos
        transactions = [dict(zip(headers, row)) for row in cursor.fetchall()]
        cursor.close()
        conexion.close()
        print(f"Exito se cargaron las transacciones {len(transactions)} transacciones")
        return transactions
    except Exception as e:
        print("Error al cargar las transacciones: ",e)
        return []

# Conexion a oracle database (parámetros)
user = "toscuento"
password = "migue"
dsn = "10.243.57.244/FREEPDB1"
vm = "LOTH.TITANIC_APRIORI"
transactions = cargar_transacciones(user, password, dsn, vm)

#impresion de primeras 5 transacciones
for row in transactions[:5]:
    print(row)

target = "ESTATUS_SUPERVIVENCIA"
m_atributo, mejor_regla, error, reglas = one_rule(transactions, target)
#impresion de resultados
print(f"mejor atributo: {m_atributo}")
print(f"mejor regla: {mejor_regla}")
print(f"error de la mejor regla: {error}")
# resumen de reglas para cada atributo
for atributo, (regla, error_atributo) in reglas.items():
    print(f"Atributo: {atributo}, regla: {regla}, error: {error_atributo}, porcentaje de error {0}")