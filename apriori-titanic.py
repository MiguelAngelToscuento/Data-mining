#ESTE PROGRAMA GENERA REGLAS DE ASOCIACIÓN MEDIANTE EL ALGORITMO DE APRIORI


from itertools import combinations #conjuntos
import oracledb

def get_frequen_itemsets(candidates, transactions, min_sup):
    num_transactions = len(transactions)
    freq = {
        c: sum(1 for t in transactions if c.issubset(t))/num_transactions
        for c in candidates
    }
    return {c: sup for c, sup in freq.items() if sup >= min_sup}

def apriori_gen(LK_list, k):
    candidates = set()
    LK_set = set(LK_list)
    for i in range(len(LK_list)):
        for j in range(i + 1, len(LK_list)):
            union = LK_list[i] | LK_list[j]
            if len(union) == k:
                if all(frozenset(subset) in LK_set for subset
                    in combinations(union, k-1)):
                    candidates.add(union)
    return list(candidates)

def apriori(transactions, min_sup):
    items  = {frozenset([item]) for t in transactions for item in t} #set
    freq_itemsets = {1: get_frequen_itemsets(items, transactions, min_sup)}
    k = 1
    while freq_itemsets[k]:
        k += 1
        candidates_k = apriori_gen(list(freq_itemsets[k-1].keys()), k)
        LK = get_frequen_itemsets(candidates_k, transactions, min_sup)
        if not LK:
            break
        freq_itemsets[k] = LK
    return freq_itemsets


def generate_rules(freq_itemsets, min_conf):
    rules = []
    for k, itemset in freq_itemsets.items():
        if k < 2: continue
        for itemsets, sup_itemset in itemset.items():
            for i in range(1, len(itemsets)):
                for combo in combinations(itemsets, i):
                    antecedente = frozenset(combo)
                    consecuente = itemsets - antecedente
                    ante_sup = freq_itemsets[len(antecedente)].get(antecedente,0)
                    if ante_sup > 0:
                        conf = sup_itemset / ante_sup
                        if conf >= min_conf:
                            rules.append((antecedente, consecuente, sup_itemset, conf))
    return rules

def cargar_transacciones(user, password, dsn, vm):
    try:
        conexion = oracledb.connect(user=user, password=password, dsn=dsn)
        cursor = conexion.cursor()
        cursor.execute(f"select * from {vm}")
        transactions = [set(item for item in row if item is not None) for row in cursor.fetchall()]
        cursor.close()
        conexion.close()
        print(f"Exito se cargaron las transacciones {len(transactions)} transacciones")
        return transactions
    except Exception as e:
        print("Error al cargar las transacciones: ",e)
        return []



#Conexipn a oracle database
user = "toscuento"
password = "migue"
dsn = "192.168.0.240/FREEPDB1"
vm = "LOTH.TITANIC_APRIORI"
transactions = cargar_transacciones(user, password, dsn, vm)

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
for t in transactions[:5]:
    print(t)

# declaracion de confianza y soporte
min_sup = 0.05
min_conf = 0.95

print("Miguel Angel Toscuento Flores")
freq_itemsets = apriori(transactions,min_sup)
"""for k, itemsets in freq_itemsets.items():
    print(f"- Tamaño {k}:")
    for itemsets, sup in itemsets.items():
        print(f" - {set(itemsets)}: soporte = {sup:.2f}")"""

rules = generate_rules(freq_itemsets, min_conf)
print("Reglas de asociación")
for (antecedente, consecuente, sup, conf) in rules:
    if set(consecuente) == {'Vivo'}:
        print(f"Regla: {set(antecedente)} -> {set(consecuente)}," f"soporte = {sup:.2f}, confianza = {conf:.2f}")

items  = {frozenset([item]) for t in transactions for item in t} #set
print(f"\n Items únicos en las transacciones: {len(items)}")
print(f"Conjuntos diferentes C: {2** len(items)-1}")
print(f"Reglas diferentes de R: {3**len(items)-2**len(items)+1}")

