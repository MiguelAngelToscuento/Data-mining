#ESTE PROGRAMA GENERA REGLAS DE ASOCIACIÓN MEDIANTE EL ALGORITMO DE APRIORI

from itertools import combinations #conjuntos
import oracledb

# Calcula el soporte de los candidatos y filtra los que no alcanzan el mínimo
def get_frequen_itemsets(candidates, transactions, min_sup):
    num_transactions = len(transactions)
    # Vemos con qué frecuencia aparece cada candidato en las transacciones
    freq = {
        c: sum(1 for t in transactions if c.issubset(t))/num_transactions
        for c in candidates
    }
    # Solo regresamos los que pasan el filtro de soporte
    return {c: sup for c, sup in freq.items() if sup >= min_sup}

# Genera nuevos candidatos de tamaño k combinando los que ya tenemos de tamaño k-1
def apriori_gen(LK_list, k):
    candidates = set()
    LK_set = set(LK_list)
    for i in range(len(LK_list)):
        for j in range(i + 1, len(LK_list)):
            union = LK_list[i] | LK_list[j]
            # Si al unirlos nos da el tamaño buscado, checamos sus subconjuntos
            if len(union) == k:
                # Condición de Apriori: todos sus subconjuntos también deben ser frecuentes
                if all(frozenset(subset) in LK_set for subset
                    in combinations(union, k-1)):
                    candidates.add(union)
    return list(candidates)

# Función principal que corre todo el ciclo de Apriori
def apriori(transactions, min_sup):
    # Sacamos todos los items individuales primero
    items  = {frozenset([item]) for t in transactions for item in t} #set
    # Guardamos los frecuentes de tamaño 1
    freq_itemsets = {1: get_frequen_itemsets(items, transactions, min_sup)}
    k = 1
    # Mientras sigamos encontrando conjuntos frecuentes, seguimos iterando
    while freq_itemsets[k]:
        k += 1
        candidates_k = apriori_gen(list(freq_itemsets[k-1].keys()), k)
        LK = get_frequen_itemsets(candidates_k, transactions, min_sup)
        # Si la lista vuelve vacía, ya no hay más candidatos y rompemos el ciclo
        if not LK:
            break
        freq_itemsets[k] = LK
    return freq_itemsets

# Crea las reglas de asociación a partir de los itemsets frecuentes
def generate_rules(freq_itemsets, min_conf):
    rules = []
    for k, itemset in freq_itemsets.items():
        if k < 2: continue # Brincamos los de tamaño 1 porque no forman reglas de tipo A -> B
        for itemsets, sup_itemset in itemset.items():
            for i in range(1, len(itemsets)):
                for combo in combinations(itemsets, i):
                    antecedente = frozenset(combo)
                    consecuente = itemsets - antecedente
                    # Recuperamos el soporte del antecedente para calcular la fórmula
                    ante_sup = freq_itemsets[len(antecedente)].get(antecedente,0)
                    if ante_sup > 0:
                        conf = sup_itemset / ante_sup
                        # Si pasa el umbral de confianza, la guardamos
                        if conf >= min_conf:
                            rules.append((antecedente, consecuente, sup_itemset, conf))
    return rules

# Se conecta a la base de datos y se trae la tabla/vista
def cargar_transacciones(user, password, dsn, vm):
    try:
        conexion = oracledb.connect(user=user, password=password, dsn=dsn)
        cursor = conexion.cursor()
        cursor.execute(f"select * from {vm}")
        # Convierte cada fila en un set y se salta los valores nulos
        transactions = [set(item for item in row if item is not None) for row in cursor.fetchall()]
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
dsn = "192.168.0.240/FREEPDB1"
vm = "LOTH.TITANIC_APRIORI"
transactions = cargar_transacciones(user, password, dsn, vm)

# Prueba extra de conexión para ver la hora del servidor (los close() están comentados igual que en el original)
try:
    conexion = oracledb.connect(user=user, password=password, dsn=dsn)
    cursor = conexion.cursor()
    cursor.execute("select sysdate from dual")
    #cursor.close()
    #conexion.close()
    print("Conexión exitosa \n Fecha y hora: ", cursor.fetchall())
except Exception as e:
    print("Error al conectar a la base de datos", e)

print("transacciones cargadas: ")
# Imprimimos solo los primeros 5 para ver que sí trajo bien los datos
for t in transactions[:5]:
    print(t)

# declaracion de confianza y soporte
min_sup = 0.05
min_conf = 0.95

print("Miguel Angel Toscuento Flores")
# Arrancamos el algoritmo
freq_itemsets = apriori(transactions,min_sup)

# Esto lo dejaste comentado para debuggear los soportes por tamaño si hiciera falta
"""for k, itemsets in freq_itemsets.items():
    print(f"- Tamaño {k}:")
    for itemsets, sup in itemsets.items():
        print(f" - {set(itemsets)}: soporte = {sup:.2f}")"""

rules = generate_rules(freq_itemsets, min_conf)
print("Reglas de asociación")
for (antecedente, consecuente, sup, conf) in rules:
    # Filtro duro para imprimir únicamente las reglas que resulten en supervivencia ('Vivo')
    if set(consecuente) == {'Vivo'}:
        print(f"Regla: {set(antecedente)} -> {set(consecuente)}," f"soporte = {sup:.2f}, confianza = {conf:.2f}")

# Vuelve a sacar los items para poder calcular los espacios de búsqueda
items  = {frozenset([item]) for t in transactions for item in t} #set
print(f"\n Items únicos en las transacciones: {len(items)}")
# Cálculos teóricos de combinatoria posibles
print(f"Conjuntos diferentes C: {2** len(items)-1}")
print(f"Reglas diferentes de R: {3**len(items)-2**len(items)+1}")