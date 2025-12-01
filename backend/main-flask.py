import json
import pandas as pd
import networkx as nx
import itertools
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- CONFIGURACIÓN Y CONSTANTES ---
DATA_FILE = "drugs_side_effects_drugs_com.csv"
SIMILARITY_SAME_CONDITION_AND_CLASS = 1.0
SIMILARITY_SAME_CONDITION_ONLY = 0.7
SIMILARITY_SAME_CLASS_ONLY = 0.5

# --- INICIALIZACIÓN DE FLASK ---
app = Flask(__name__)
# Habilitar CORS para permitir peticiones desde Vue (puerto 5173 o el que uses)
CORS(app)

# Contexto Global para almacenar datos en memoria
global_context = {
    "G": None,
    "df": None,
    "search_index": {},
    "filter_cache": {} # Caché para optimización
}

# --- LÓGICA DE NEGOCIO ---
def build_graph():
    """Carga datos y construye el grafo incluyendo la razón de la conexión."""
    print("--- INICIANDO SERVIDOR (FLASK) ---")
    print(f"Cargando {DATA_FILE}...")
    
    try:
        df = pd.read_csv(DATA_FILE)
        cols_to_check = ['drug_name', 'medical_condition', 'drug_classes']
        df = df.dropna(subset=cols_to_check)
        
        for col in df.select_dtypes(include=['object']):
            df[col] = df[col].str.strip()

        df = df.drop_duplicates(subset=['drug_name'])
        df_clean = df.copy()
        df = df.set_index('drug_name')

        G = nx.Graph()
        # Agregar nodos
        for drug_name, row in df.iterrows():
            row_data = row.where(pd.notnull(row), None).to_dict()
            G.add_node(drug_name, **row_data)

        condition_map = df.groupby("medical_condition").groups
        class_map = df.groupby("drug_classes").groups
        
        edges_to_add = {}
        edge_reasons = {} # Diccionario para guardar el texto de la coincidencia

        print("Calculando relaciones...")
        
        # Pase 1: misma condición
        for condition, drugs in condition_map.items():
            for drug1, drug2 in itertools.combinations(drugs, 2):
                pair = tuple(sorted((drug1, drug2)))
                edges_to_add[pair] = SIMILARITY_SAME_CONDITION_ONLY
                edge_reasons[pair] = f"Condición: '{condition}'"

        # Pase 2: misma clase
        for d_class, drugs in class_map.items():
            for drug1, drug2 in itertools.combinations(drugs, 2):
                pair = tuple(sorted((drug1, drug2)))
                if pair in edges_to_add:
                    edges_to_add[pair] = SIMILARITY_SAME_CONDITION_AND_CLASS
                    # Si ya existía, agregamos la clase al texto
                    edge_reasons[pair] += f" y Clase: '{d_class}'"
                else:
                    edges_to_add[pair] = SIMILARITY_SAME_CLASS_ONLY
                    edge_reasons[pair] = f"Clase: '{d_class}'"

        # Añadir aristas con atributos
        for (drug1, drug2), similarity in edges_to_add.items():
            cost = 1.1 - similarity
            reason_text = edge_reasons.get((drug1, drug2), "Desconocido")
            # Guardamos 'reason' en la arista
            G.add_edge(drug1, drug2, similarity=similarity, cost=cost, reason=reason_text)

        print(f"Grafo construido: {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas.")
        
        search_idx = {name.lower(): name for name in df.index}
        
        return G, df_clean, search_idx

    except FileNotFoundError:
        print("ERROR: No se encontró el archivo CSV.")
        return None, None, None
    except Exception as e:
        print(f"Error inesperado cargando datos: {e}")
        return None, None, None

# --- CARGA INICIAL ---
G, df, search_idx = build_graph()
global_context["G"] = G
global_context["df"] = df
global_context["search_index"] = search_idx

# --- HELPERS ---
def get_real_name(name):
    if not name: return None
    return global_context["search_index"].get(name.lower().strip())

# --- ENDPOINTS ---

@app.route('/', methods=['GET'])
def read_root():
    if global_context["G"]:
        return jsonify({"status": "online", "nodes": global_context["G"].number_of_nodes()})
    return jsonify({"status": "error", "detail": "Datos no cargados"}), 500

@app.route('/drugs/search', methods=['GET'])
def search_drugs():
    query = request.args.get('query', '').lower()
    matches = [name for name in global_context["search_index"].values() if query in name.lower()]
    return jsonify(matches[:20])

@app.route('/drugs/<path:drug_name>', methods=['GET'])
def get_drug_details(drug_name):
    real_name = get_real_name(drug_name)
    if not real_name:
        return jsonify({"detail": "Medicamento no encontrado"}), 404
    
    df = global_context["df"]
    info = df[df['drug_name'] == real_name].iloc[0].to_dict()
    clean_info = {k: (v if pd.notnull(v) else None) for k, v in info.items()}
    return jsonify(clean_info)

@app.route('/analysis/path', methods=['POST'])
def get_shortest_path():
    data = request.get_json()
    if not data: return jsonify({"detail": "JSON inválido"}), 400
        
    start_drug = data.get('start_drug')
    end_drug = data.get('end_drug')

    G = global_context["G"]
    start = get_real_name(start_drug)
    end = get_real_name(end_drug)

    if not start or not end:
        return jsonify({"detail": "Uno o ambos medicamentos no existen"}), 404

    try:
        path = nx.shortest_path(G, source=start, target=end, weight='cost')
        
        result_path = []
        total_similarity = 0.0
        
        for i in range(len(path)):
            node_info = {"name": path[i], "step": i + 1}
            
            if i < len(path) - 1:
                u, v = path[i], path[i+1]
                edge_data = G.get_edge_data(u, v)
                sim = edge_data['similarity']
                # Extraemos la razón guardada en build_graph
                reason = edge_data.get('reason', 'N/A')
                
                total_similarity += sim
                node_info["similarity_to_next"] = sim
                node_info["reason"] = reason # Enviamos la razón al frontend
            
            result_path.append(node_info)

        return jsonify({
            "path": result_path,
            "total_similarity": round(total_similarity, 2),
            "steps": len(path)
        })

    except nx.NetworkXNoPath:
        return jsonify({"detail": "No hay relación entre estos medicamentos"}), 400
    except Exception as e:
        return jsonify({"detail": str(e)}), 500

@app.route('/analysis/alternatives/<path:drug_name>', methods=['GET'])
def get_alternatives(drug_name):
    top_n = int(request.args.get('top_n', 10))
    G = global_context["G"]
    real_name = get_real_name(drug_name)
    
    if not real_name:
        return jsonify({"detail": "Medicamento no encontrado"}), 404

    neighbors = G[real_name]
    if not neighbors: return jsonify([])

    sorted_neighbors = sorted(neighbors.items(), key=lambda item: item[1]['similarity'], reverse=True)

    results = []
    for neighbor_name, data in sorted_neighbors[:top_n]:
        results.append({
            "name": neighbor_name,
            "similarity": data['similarity'],
            "medical_condition": G.nodes[neighbor_name].get("medical_condition", "N/A")
        })
    return jsonify(results)

@app.route('/drugs/filter', methods=['POST'])
def filter_drugs():
    criteria = request.get_json() or {}
    print(f"🔍 Filtro Recibido: {criteria}")
    
    df = global_context["df"]
    cache = global_context["filter_cache"]
    
    # 1. Verificar Cache Total
    cache_key = tuple(sorted(criteria.items()))
    if cache_key in cache:
        print("💡 Resultado obtenido desde el caché.")
        results = cache[cache_key].head(100)
        return json.loads(results.to_json(orient="records"))

    # 2. Programación Dinámica (Cache por Columna)
    if "dp" not in cache: cache["dp"] = {}
    dp = cache["dp"]
    
    partial_results = []
    
    # Extraer filtros
    cond = criteria.get('condition')
    preg = criteria.get('pregnancy_category')
    rx = criteria.get('rx_otc')
    csa_val = criteria.get('csa')

    # Procesar Condition
    if cond:
        val = cond.lower().strip()
        if ('condition', val) not in dp:
            dp[('condition', val)] = df[df['medical_condition'].astype(str).str.contains(val, case=False, na=False)]
        partial_results.append(dp[('condition', val)])

    # Procesar Pregnancy
    if preg:
        val = preg.upper().strip()
        if ('preg_cat', val) not in dp:
            dp[('preg_cat', val)] = df[df['pregnancy_category'].astype(str).str.upper() == val]
        partial_results.append(dp[('preg_cat', val)])

    # Procesar Rx
    if rx:
        val = rx.upper().strip()
        if ('rx_otc', val) not in dp:
            dp[('rx_otc', val)] = df[df['rx_otc'].astype(str).str.upper().str.contains(val, na=False)]
        partial_results.append(dp[('rx_otc', val)])

    # Procesar CSA
    if csa_val:
        val = csa_val.upper().strip()
        if ('csa', val) not in dp:
            dp[('csa', val)] = df[df['csa'].astype(str).str.upper() == val]
        partial_results.append(dp[('csa', val)])

    # 3. Intersección de Resultados
    if not partial_results:
        final = df.copy()
    else:
        final = partial_results[0]
        for sub in partial_results[1:]:
            final = pd.merge(final, sub, how='inner', on=list(final.columns))
            
    # Guardar en cache y retornar
    cache[cache_key] = final.copy() 
    results = final.head(100)
    
    return json.loads(results.to_json(orient="records"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)