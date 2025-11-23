import json
import pandas as pd
import networkx as nx
import itertools
from flask import Flask, request, jsonify, abort
from flask_cors import CORS

# --- CONFIGURACIÓN Y CONSTANTES ---
DATA_FILE = "drugs_side_effects_drugs_com.csv"
SIMILARITY_SAME_CONDITION_AND_CLASS = 1.0
SIMILARITY_SAME_CONDITION_ONLY = 0.7
SIMILARITY_SAME_CLASS_ONLY = 0.5

# --- INICIALIZACIÓN DE FLASK ---
app = Flask(__name__)
# Habilitar CORS para todas las rutas (Vital para conectar con Vue)
CORS(app)

# Contexto Global
global_context = {
    "G": None,
    "df": None,
    "search_index": {}
}

# --- LÓGICA DE NEGOCIO (Idéntica a tu versión anterior) ---
def build_graph():
    """Carga datos y construye el grafo."""
    print("--- INICIANDO SERVIDOR (FLASK) ---")
    print(f"Cargando {DATA_FILE}...")
    
    try:
        df = pd.read_csv(DATA_FILE)
        cols_to_check = ['drug_name', 'medical_condition', 'drug_classes']
        df = df.dropna(subset=cols_to_check)
        
        for col in df.select_dtypes(include=['object']):
            df[col] = df[col].str.strip()

        df = df.drop_duplicates(subset=['drug_name'])
        df_clean = df.copy() # Copia para devolver datos
        df = df.set_index('drug_name')

        G = nx.Graph()
        for drug_name, row in df.iterrows():
            # Convertimos NaN a None manualmente
            row_data = row.where(pd.notnull(row), None).to_dict()
            G.add_node(drug_name, **row_data)

        condition_map = df.groupby("medical_condition").groups
        class_map = df.groupby("drug_classes").groups
        edges_to_add = {}

        print("Calculando relaciones...")
        
        # Lógica de aristas
        for condition, drugs in condition_map.items():
            for drug1, drug2 in itertools.combinations(drugs, 2):
                pair = tuple(sorted((drug1, drug2)))
                edges_to_add[pair] = SIMILARITY_SAME_CONDITION_ONLY

        for d_class, drugs in class_map.items():
            for drug1, drug2 in itertools.combinations(drugs, 2):
                pair = tuple(sorted((drug1, drug2)))
                if pair in edges_to_add:
                    edges_to_add[pair] = SIMILARITY_SAME_CONDITION_AND_CLASS
                else:
                    edges_to_add[pair] = SIMILARITY_SAME_CLASS_ONLY

        for (drug1, drug2), similarity in edges_to_add.items():
            cost = 1.1 - similarity
            G.add_edge(drug1, drug2, similarity=similarity, cost=cost)

        print(f"Grafo construido: {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas.")
        
        search_idx = {name.lower(): name for name in df.index}
        
        return G, df_clean, search_idx

    except FileNotFoundError:
        print("ERROR: No se encontró el archivo CSV.")
        return None, None, None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None, None, None

# --- CARGA DE DATOS AL INICIO ---
# En Flask, ejecutamos esto antes de que arranque el servidor
G, df, search_idx = build_graph()
global_context["G"] = G
global_context["df"] = df
global_context["search_index"] = search_idx

# --- HELPERS ---
def get_real_name(name):
    """Busca el nombre real (case-insensitive)"""
    if not name: return None
    return global_context["search_index"].get(name.lower().strip())

# --- ENDPOINTS (RUTAS) ---

@app.route('/', methods=['GET'])
def read_root():
    if global_context["G"]:
        return jsonify({"status": "online", "nodes": global_context["G"].number_of_nodes()})
    return jsonify({"status": "error", "detail": "Datos no cargados"}), 500

@app.route('/drugs/search', methods=['GET'])
def search_drugs():
    # En Flask, los query params (?query=...) están en request.args
    query = request.args.get('query', '').lower()
    
    matches = [
        name for name in global_context["search_index"].values() 
        if query in name.lower()
    ]
    return jsonify(matches[:20])

@app.route('/drugs/<path:drug_name>', methods=['GET'])
def get_drug_details(drug_name):
    real_name = get_real_name(drug_name)
    if not real_name:
        # En Flask usamos jsonify con código de error manual
        return jsonify({"detail": "Medicamento no encontrado"}), 404
    
    df = global_context["df"]
    info = df[df['drug_name'] == real_name].iloc[0].to_dict()
    
    # Limpiar NaNs para JSON
    clean_info = {k: (v if pd.notnull(v) else None) for k, v in info.items()}
    return jsonify(clean_info)

@app.route('/analysis/path', methods=['POST'])
def get_shortest_path():
    # En Flask, el body JSON se obtiene con request.get_json()
    data = request.get_json()
    
    # Validación manual (en FastAPI lo hacía Pydantic)
    if not data:
        return jsonify({"detail": "JSON inválido"}), 400
        
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
                total_similarity += sim
                node_info["similarity_to_next"] = sim
            
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
    # Obtener query param ?top_n=10, default 10
    top_n = int(request.args.get('top_n', 10))
    
    G = global_context["G"]
    real_name = get_real_name(drug_name)
    
    if not real_name:
        return jsonify({"detail": "Medicamento no encontrado"}), 404

    neighbors = G[real_name]
    if not neighbors:
        return jsonify([])

    sorted_neighbors = sorted(
        neighbors.items(), 
        key=lambda item: item[1]['similarity'], 
        reverse=True
    )

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
    # Recibimos los datos
    criteria = request.get_json() or {} # Si es None, usar dict vacío
    print(f"🔍 Filtro Recibido: {criteria}")
    
    df = global_context["df"]
    results = df.copy()

    try:
        # Extracción manual de variables (En FastAPI era criteria.condition)
        cond = criteria.get('condition')
        preg = criteria.get('pregnancy_category')
        rx = criteria.get('rx_otc')
        csa_val = criteria.get('csa')

        if cond:
            results = results[results['medical_condition'].astype(str).str.contains(cond, case=False, na=False)]

        if preg:
            val = preg.upper().strip()
            results = results[results['pregnancy_category'].astype(str).str.upper() == val]

        if rx:
            val = rx.upper().strip()
            results = results[results['rx_otc'].astype(str).str.upper().str.contains(val, na=False)]

        if csa_val:
            val = csa_val.upper().strip()
            results = results[results['csa'].astype(str).str.upper() == val]

        results = results.head(100)
        print(f"✅ Resultados: {len(results)}")

        # Retornar JSON seguro manejando NaNs
        return json.loads(results.to_json(orient="records"))

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"detail": "Error interno del servidor"}), 500

# --- EJECUCIÓN ---
if __name__ == '__main__':
    # debug=True permite que el servidor se reinicie si cambias el código
    # port=8000 mantiene compatibilidad con tu Frontend actual
    app.run(host='0.0.0.0', port=8000, debug=True)