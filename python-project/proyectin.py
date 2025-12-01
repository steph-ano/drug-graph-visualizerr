import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import itertools
import warnings
from difflib import get_close_matches

# Suprimir advertencias de Matplotlib (pueden ser ruidosas)
warnings.filterwarnings("ignore", category=UserWarning)

# --- Constantes y Configuración ---
DATA_FILE = "drugs_side_effects_drugs_com.csv"

# Pesos de SIMILITUD (más alto es mejor)
SIMILARITY_SAME_CONDITION_AND_CLASS = 1.0  # Peso de arista: 1
SIMILARITY_SAME_CONDITION_ONLY = 0.7       # Peso de arista: 0.7
SIMILARITY_SAME_CLASS_ONLY = 0.5           # Peso de arista: 0.5


# --- 1. Carga y Construcción del Grafo ---
def load_and_build_graph():
    """
    Carga el CSV, limpia los datos y construye el grafo guardando
    la razón de la conexión (Condición o Clase).
    """
    print(f"Cargando dataset desde '{DATA_FILE}'...")

    try:
        df = pd.read_csv(DATA_FILE)

        # Limpieza de datos
        cols_to_check = ['drug_name', 'medical_condition', 'drug_classes']
        df = df.dropna(subset=cols_to_check)

        for col in df.select_dtypes(include=['object']):
            df[col] = df[col].str.strip()

        df = df.drop_duplicates(subset=['drug_name'])
        df = df.set_index('drug_name')

    except FileNotFoundError:
        print(f"--- ERROR ---: El archivo '{DATA_FILE}' no se encontró.")
        return None, None
    except Exception as e:
        print(f"--- ERROR INESPERADO ---: {e}")
        return None, None

    print(f"Datos cargados. {len(df)} medicamentos únicos encontrados.")
    print("Construyendo grafo de relaciones...")

    G = nx.Graph()

    # Agregar nodos
    for drug_name, row in df.iterrows():
        G.add_node(drug_name, **row.to_dict())

    condition_map = df.groupby("medical_condition").groups
    class_map = df.groupby("drug_classes").groups

    edges_to_add = {}
    edge_reasons = {} # Nuevo: Diccionario para guardar el texto de la coincidencia

    # Pase 1: misma condición
    for condition, drugs in condition_map.items():
        for drug1, drug2 in itertools.combinations(drugs, 2):
            pair = tuple(sorted((drug1, drug2)))
            edges_to_add[pair] = SIMILARITY_SAME_CONDITION_ONLY
            # Guardamos la razón
            edge_reasons[pair] = f"Condición: '{condition}'"

    # Pase 2: misma clase
    for d_class, drugs in class_map.items():
        for drug1, drug2 in itertools.combinations(drugs, 2):
            pair = tuple(sorted((drug1, drug2)))

            if pair in edges_to_add:
                edges_to_add[pair] = SIMILARITY_SAME_CONDITION_AND_CLASS
                # Si ya existía por condición, agregamos la clase al texto
                edge_reasons[pair] += f" y Clase: '{d_class}'"
            else:
                edges_to_add[pair] = SIMILARITY_SAME_CLASS_ONLY
                # Si es nuevo, solo ponemos la clase
                edge_reasons[pair] = f"Clase: '{d_class}'"

    # Añadir aristas con el atributo 'reason'
    for (drug1, drug2), similarity in edges_to_add.items():
        cost = 1.1 - similarity
        reason_text = edge_reasons.get((drug1, drug2), "Desconocido")
        
        # Aquí agregamos 'reason=reason_text' a la arista
        G.add_edge(drug1, drug2, similarity=similarity, cost=cost, reason=reason_text)

    print(f"✅ Grafo construido.")
    print(f" Nodos: {G.number_of_nodes()}")
    print(f" Aristas: {G.number_of_edges()}")

    return G, df.reset_index()


# --- 2. Funcionalidades del Aplicativo ---
def get_drug_info(df, drug_name):
    try:
        info = df[df['drug_name'] == drug_name].iloc[0]
        print(f"\n--- Información de: {drug_name} ---")
        print(f" Condición Médica: {info['medical_condition']}")
        print(f" Clase de Droga: {info['drug_classes']}")
        print(f" Nombre Genérico: {info['generic_name']}")
        print(f" Acceso (Rx/OTC): {info['rx_otc']}")
        print(f" Cat. Embarazo: {info['pregnancy_category']}")
        print(f" CSA: {info['csa']}")
        print(f" Efectos Secundarios: {info['side_effects'][:100]}...")
        print("-" * (24 + len(drug_name)))
    except IndexError:
        print(f"No se encontró información para '{drug_name}'.")


def find_shortest_path(G, drug1, drug2, visualize=True):
    if drug1 not in G:
        print(f"Error: '{drug1}' no está en el grafo.")
        return
    if drug2 not in G:
        print(f"Error: '{drug2}' no está en el grafo.")
        return

    print(f"\nBuscando el camino más corto entre '{drug1}' y '{drug2}'...")

    try:
        path = nx.shortest_path(G, source=drug1, target=drug2, weight='cost')
        sim_acumulada = 0

        print("\n" + "="*60)
        print(f" RUTA OPTIMIZADA: {drug1} -> {drug2}")
        print("="*60)

        for i in range(len(path) - 1):
            current_node = path[i]
            next_node = path[i+1]
            
            # Obtener datos de la arista
            edge_data = G.get_edge_data(current_node, next_node)
            sim = edge_data['similarity']
            reason = edge_data.get('reason', 'N/A') # Recuperamos la razón
            
            sim_acumulada += sim

            # Imprimir con formato detallado
            print(f" {i+1}. [ {current_node} ] ---> [ {next_node} ]")
            print(f"     └-> Similitud: {sim:.1f} | Coinciden en: {reason}")
            print("-" * 60)
        
        # Imprimir el último nodo para cerrar visualmente
        print(f" LLEGADA: [ {path[-1]} ]")

        print(f"\n** Peso Total (Similitud Acumulada): {sim_acumulada:.1f} **")

        if visualize:
            plot_dijkstra_path(G, path)

    except nx.NetworkXNoPath:
        print(f"No existe ruta entre '{drug1}' y '{drug2}'.")
    except Exception as e:
        print(f"Error inesperado: {e}")


def plot_dijkstra_path(G, path):
    print("\nGenerando visualización...")

    nodes_to_include = set(path)
    for node in path:
        neighbors = list(G.neighbors(node))[:3]
        nodes_to_include.update(neighbors)

    sub_g = G.subgraph(nodes_to_include)

    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(sub_g, k=1.0, iterations=50, seed=42)

    path_nodes = set(path)
    origin = path[0]
    destination = path[-1]
    intermediate_nodes = path_nodes - {origin, destination}
    context_nodes = nodes_to_include - path_nodes

    if context_nodes:
        nx.draw_networkx_nodes(
            sub_g, pos,
            nodelist=list(context_nodes),
            node_color='#CCCCCC',
            node_size=800,
            alpha=0.4
        )

    if intermediate_nodes:
        nx.draw_networkx_nodes(
            sub_g, pos,
            nodelist=list(intermediate_nodes),
            node_color='#33A1FF',
            node_size=1500
        )

    nx.draw_networkx_nodes(
        sub_g, pos, nodelist=[origin],
        node_color='#28A745', node_size=2000
    )

    nx.draw_networkx_nodes(
        sub_g, pos, nodelist=[destination],
        node_color='#DC3545', node_size=2000
    )

    path_edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
    other_edges = [e for e in sub_g.edges()
                   if e not in path_edges and (e[1], e[0]) not in path_edges]

    if other_edges:
        nx.draw_networkx_edges(
            sub_g, pos, edgelist=other_edges,
            width=1, alpha=0.2, edge_color='#999999'
        )

    nx.draw_networkx_edges(
        sub_g, pos, edgelist=path_edges,
        width=4, alpha=0.8, edge_color='#FF5733',
        arrows=True, arrowsize=20, arrowstyle='->'
    )

    nx.draw_networkx_labels(sub_g, pos, font_size=9, font_weight='bold', font_color='white')

    edge_labels = {(u, v): f"{sub_g[u][v]['similarity']:.1f}" for u, v in path_edges}
    nx.draw_networkx_edge_labels(sub_g, pos, edge_labels=edge_labels, font_color='#8B0000')

    sim_acum_plot = sum(sub_g[path[i]][path[i+1]]['similarity'] for i in range(len(path)-1))

    plt.title(
        f"Camino Dijkstra: {origin} → {destination}\n"
        f"(Longitud: {len(path)} nodos, Peso Total: {sim_acum_plot:.1f})",
        size=14, weight='bold'
    )

    plt.axis('off')
    plt.tight_layout()
    plt.show()


def find_alternatives(G, drug, top_n=10):
    if drug not in G:
        print(f"Error: '{drug}' no está en el grafo.")
        return

    print(f"\nBuscando las {top_n} alternativas más similares a '{drug}'...")

    try:
        neighbors = G[drug]

        if not neighbors:
            print(f"'{drug}' no tiene alternativas.")
            return

        sorted_neighbors = sorted(
            neighbors.items(),
            key=lambda item: item[1]['similarity'],
            reverse=True
        )

        print(f"\n--- Alternativas para: {drug} (Condición: {G.nodes[drug]['medical_condition']}) ---")
        for i, (neighbor, data) in enumerate(sorted_neighbors[:top_n]):
            print(f" {i+1}. {neighbor} (Similitud: {data['similarity']:.1f})")
            print(f"   Trata: {G.nodes[neighbor]['medical_condition']}")

        return [n for n, d in sorted_neighbors[:top_n]]

    except Exception as e:
        print(f"Ocurrió un error: {e}")
        return []


def filter_by_criteria(df, cache, **kwargs):
    """
    Versión optimizada con programación dinámica.
    - DP por cada criterio individual.
    """

    # Cache general (ya estaba)
    cache_key = tuple(sorted(kwargs.items()))
    if cache_key in cache:
        print("\n(Resultado obtenido desde el caché)")
        return cache[cache_key]

    print("\nRealizando búsqueda...")

    # --- NUEVO: DP cache POR COLUMNA ---
    if "dp" not in cache:
        cache["dp"] = {     # dp[col][value] = subconjunto filtrado
            "condition": {},
            "preg_cat": {},
            "rx_otc": {},
            "csa": {},
        }
    dp = cache["dp"]

    # Lista para ir uniendo resultados
    partial_results = []

    # --- Procesar cada filtro con DP ---
    if 'condition' in kwargs:
        val = kwargs['condition'].lower()
        if val not in dp["condition"]:
            dp["condition"][val] = df[
                df['medical_condition'].str.contains(val, case=False, na=False)
            ]
        partial_results.append(dp["condition"][val])

    if 'preg_cat' in kwargs:
        val = kwargs['preg_cat'].upper()
        if val not in dp["preg_cat"]:
            dp["preg_cat"][val] = df[df['pregnancy_category'].str.upper() == val]
        partial_results.append(dp["preg_cat"][val])

    if 'rx_otc' in kwargs:
        val = kwargs['rx_otc'].upper()
        if val not in dp["rx_otc"]:
            dp["rx_otc"][val] = df[df['rx_otc'].str.upper() == val]
        partial_results.append(dp["rx_otc"][val])

    if 'csa' in kwargs:
        val = kwargs['csa'].upper()
        if val not in dp["csa"]:
            dp["csa"][val] = df[df['csa'].str.upper() == val]
        partial_results.append(dp["csa"][val])

    # --- Unir los resultados por intersección sin rescaneo ---
    if not partial_results:
        return df

    final = partial_results[0]
    for sub in partial_results[1:]:
        final = pd.merge(final, sub, how='inner')

    # Guardar combinación final en el cache principal
    cache[cache_key] = final
    return final


def plot_alternatives_subgraph(G, origin_drug, alternative_nodes):
    if not alternative_nodes:
        print("No hay alternativas para graficar.")
        return

    print("\nGenerando visualización de alternativas...")

    nodes_to_plot = [origin_drug] + alternative_nodes
    sub_g = G.subgraph(nodes_to_plot)

    plt.figure(figsize=(12, 10))
    pos = nx.spring_layout(sub_g, k=0.8, seed=42)

    nx.draw_networkx_nodes(
        sub_g, pos,
        node_color=['#FF5733' if n == origin_drug else '#33A1FF' for n in sub_g.nodes()],
        node_size=2000
    )

    nx.draw_networkx_edges(sub_g, pos, width=2, alpha=0.5, edge_color='#555555')

    nx.draw_networkx_labels(sub_g, pos, font_size=10, font_weight='bold')

    edge_labels = {(u, v): f"{d['similarity']:.1f}" for u, v, d in sub_g.edges(data=True)}
    nx.draw_networkx_edge_labels(sub_g, pos, edge_labels=edge_labels, font_color='red')

    plt.title(f"Red de Alternativas para: {origin_drug}", size=16)
    plt.axis('off')
    plt.tight_layout()
    plt.show()


def get_valid_drug_name(G, prompt):
    all_drugs = list(G.nodes())
    drugs_lower = {drug.lower(): drug for drug in all_drugs}

    while True:
        drug_name = input(prompt).strip()
        low = drug_name.lower()

        if low in drugs_lower:
            return drugs_lower[low]

        matches = get_close_matches(drug_name, all_drugs, n=3, cutoff=0.7)
        if matches:
            print(f"'{drug_name}' no encontrado. Quizás quisiste decir:")
            for m in matches:
                print(f"- {m}")
        else:
            print(f"'{drug_name}' no encontrado. Intenta de nuevo.")


# --- 3. Menú Principal ---
def main_menu():
    G, df = load_and_build_graph()
    if G is None:
        return

    filter_cache = {}

    print("\n" + "="*70)
    print(" " * 28 + "ADVERTENCIA")
    print("Este aplicativo es un proyecto académico y no reemplaza")
    print("la opinión de un profesional de la salud.")
    print("="*70)

    while True:
        print("\n--- Menú Principal: Gestor de Medicamentos ---")
        print("1. Buscar camino entre dos medicamentos (Dijkstra)")
        print("2. Buscar alternativas a un medicamento")
        print("3. Filtrar medicamentos por criterios")
        print("4. Ver información de un medicamento")
        print("5. Salir")

        choice = input("Seleccione una opción (1-5): ").strip()

        if choice == '1':
            try:
                drug1 = get_valid_drug_name(G, "Ingrese el primer medicamento: ")
                drug2 = get_valid_drug_name(G, "Ingrese el segundo medicamento: ")

                if drug1 == drug2:
                    print("Error: deben ser diferentes.")
                else:
                    viz = input("¿Ver grafo del camino? (s/n): ").strip().lower()
                    visualize = (viz == 's')
                    find_shortest_path(G, drug1, drug2, visualize)

            except Exception as e:
                print(f"Error en entrada: {e}")

        elif choice == '2':
            try:
                drug = get_valid_drug_name(G, "Ingrese el medicamento: ")
                alternatives = find_alternatives(G, drug, top_n=7)

                if alternatives:
                    plot = input("¿Ver grafo? (s/n): ").strip().lower()
                    if plot == 's':
                        plot_alternatives_subgraph(G, drug, alternatives)

            except Exception as e:
                print(f"Error: {e}")

        elif choice == '3':
            print("\n--- Filtrar Medicamentos ---")
            print("(Deje en blanco para ignorar filtros)")

            filters = {}
            cond = input(" Condición: ").strip()
            preg = input(" Cat. Embarazo (A, B, C, D, X, N): ").strip()
            access = input(" Acceso (Rx, OTC, Rx/OTC): ").strip()
            csa = input(" CSA (N, M, U, 1-5): ").strip()

            if cond: filters['condition'] = cond
            if preg: filters['preg_cat'] = preg
            if access: filters['rx_otc'] = access
            if csa: filters['csa'] = csa

            if not filters:
                print("No se ingresaron filtros.")
                continue

            results = filter_by_criteria(df, filter_cache, **filters)

            if results.empty:
                print("\nNo se encontraron medicamentos.")
            else:
                cols = ['drug_name', 'medical_condition', 'pregnancy_category', 'rx_otc', 'csa']
                print(f"\n--- {len(results)} Medicamentos Encontrados ---")
                print(results[cols].to_string(index=False))

        elif choice == '4':
            try:
                drug = get_valid_drug_name(G, "Ingrese el medicamento: ")
                get_drug_info(df, drug)
            except Exception as e:
                print(f"Error: {e}")

        elif choice == '5':
            print("Saliendo del programa...")
            break

        else:
            print("Opción inválida.")


# Ejecutar menú
if __name__ == "__main__":
    main_menu()
