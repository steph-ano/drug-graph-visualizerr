<script setup>
import { ref, computed } from 'vue';
import api from '../services/api';
import GraphCanvas from '../components/GraphCanvas.vue';

const startDrug = ref('');
const endDrug = ref('');
const result = ref(null);
const error = ref('');
const loading = ref(false);

// --- Transformación para el Grafo (Visualización Limpia) ---
const graphData = computed(() => {
  if (!result.value) return { nodes: [], edges: [] };

  const nodes = [];
  const edges = [];
  const path = result.value.path;

  path.forEach((step, index) => {
    // Colores: Inicio=Verde, Fin=Rojo, Medio=Azul
    let color = '#2196f3'; 
    if (index === 0) color = '#4caf50'; 
    if (index === path.length - 1) color = '#f44336'; 

    nodes.push({
      id: step.name,
      label: step.name,
      color: { background: color, border: 'black' }
    });

    // Aristas: Solo mostramos el número de similitud en el gráfico
    if (index < path.length - 1) {
      edges.push({
        from: step.name,
        to: path[index + 1].name,
        label: step.similarity_to_next.toFixed(2), // Solo número
        font: { align: 'top' }
      });
    }
  });

  return { nodes, edges };
});

const findPath = async () => {
  loading.value = true;
  error.value = '';
  result.value = null;
  
  try {
    const response = await api.getShortestPath(startDrug.value, endDrug.value);
    result.value = response.data;
  } catch (err) {
    console.error(err);
    error.value = err.response?.data?.detail || "Error al buscar el camino.";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="path-container">
    <h1>🔍 Buscador de Caminos (Dijkstra)</h1>
    
    <!-- Controles -->
    <div class="card controls">
      <div class="input-group">
        <input v-model="startDrug" placeholder="Inicio (ej. Aspirin)" @keyup.enter="findPath" />
        <span class="arrow-icon">➜</span>
        <input v-model="endDrug" placeholder="Fin (ej. Warfarin)" @keyup.enter="findPath" />
      </div>
      <button @click="findPath" :disabled="loading || !startDrug || !endDrug" class="btn-action">
        {{ loading ? 'Calculando...' : 'Analizar Ruta' }}
      </button>
    </div>

    <!-- Mensaje de Error -->
    <div v-if="error" class="error-msg">{{ error }}</div>

    <!-- Resultados -->
    <div v-if="result" class="results-wrapper">
      
      <!-- Resumen Superior -->
      <div class="summary-card">
        <div class="stat-box">
          <span class="stat-label">Pasos</span>
          <span class="stat-value">{{ result.steps }}</span>
        </div>
        <div class="stat-box">
          <span class="stat-label">Similitud Total</span>
          <span class="stat-value">{{ result.total_similarity }}</span>
        </div>
      </div>

      <!-- El Grafo (Limpio) -->
      <div class="graph-box">
        <GraphCanvas 
          :nodes="graphData.nodes" 
          :edges="graphData.edges" 
        />
      </div>

      <!-- Detalle Paso a Paso (Aquí mostramos la Razón) -->
      <div class="details-box">
        <h3>📄 Detalle de la Conexión</h3>
        <div class="timeline">
          
          <div v-for="(step, index) in result.path" :key="index" class="timeline-item">
            <!-- El Nodo (Medicamento) -->
            <div class="drug-node">
              <span class="step-index">{{ index + 1 }}</span>
              <span class="drug-name">{{ step.name }}</span>
            </div>

            <!-- La Conexión (si hay siguiente paso) -->
            <div v-if="index < result.path.length - 1" class="connection-detail">
              <div class="line"></div>
              <div class="info-bubble">
                <span class="sim-score">Similitud: {{ step.similarity_to_next.toFixed(2) }}</span>
                <span class="reason-text">
                  <span class="icon">🔗</span> Coinciden en: <strong>{{ step.reason }}</strong>
                </span>
              </div>
              <div class="line"></div>
            </div>
          </div>

        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.path-container { max-width: 900px; margin: 0 auto; }

/* Controles */
.controls { display: flex; flex-direction: column; gap: 15px; align-items: center; margin-bottom: 20px; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.input-group { display: flex; align-items: center; gap: 10px; width: 100%; justify-content: center; }
.input-group input { padding: 12px; width: 40%; border: 1px solid #ddd; border-radius: 6px; font-size: 1rem; }
.arrow-icon { font-size: 1.5rem; color: #888; }
.btn-action { padding: 10px 30px; background: #2196f3; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; transition: 0.2s; }
.btn-action:hover:not(:disabled) { background: #1976d2; }
.btn-action:disabled { background: #ccc; }

.error-msg { background: #ffebee; color: #c62828; padding: 15px; border-radius: 8px; margin-bottom: 20px; text-align: center; }

/* Resumen */
.summary-card { display: flex; justify-content: center; gap: 40px; margin-bottom: 20px; }
.stat-box { display: flex; flex-direction: column; align-items: center; background: white; padding: 10px 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); min-width: 120px; }
.stat-label { font-size: 0.85rem; color: #666; text-transform: uppercase; letter-spacing: 0.5px; }
.stat-value { font-size: 1.5rem; font-weight: bold; color: #2196f3; }

/* Caja del Grafo */
.graph-box { height: 400px; border: 1px solid #eee; border-radius: 10px; background: #fafafa; margin-bottom: 30px; overflow: hidden; }

/* Línea de tiempo (Detalles) */
.details-box { background: white; border-radius: 10px; padding: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.details-box h3 { margin-top: 0; margin-bottom: 20px; color: #333; border-bottom: 2px solid #f0f0f0; padding-bottom: 10px; }

.timeline { display: flex; flex-direction: column; }
.timeline-item { display: flex; flex-direction: column; align-items: flex-start; }

.drug-node { display: flex; align-items: center; gap: 15px; padding: 5px 0; }
.step-index { background: #333; color: white; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; border-radius: 50%; font-weight: bold; font-size: 0.9rem; }
.drug-name { font-size: 1.2rem; font-weight: bold; color: #2c3e50; }

/* Estilo de la conexión (flecha y burbuja de texto) */
.connection-detail { margin-left: 13px; /* Centrado con el círculo del índice */ border-left: 2px dashed #ccc; padding-left: 30px; padding-top: 10px; padding-bottom: 10px; width: 100%; }

.info-bubble { background: #e3f2fd; border-left: 4px solid #2196f3; padding: 10px 15px; border-radius: 4px; display: flex; flex-direction: column; gap: 4px; width: fit-content; }
.sim-score { font-size: 0.85rem; color: #1976d2; font-weight: bold; }
.reason-text { font-size: 0.95rem; color: #444; }
.reason-text strong { color: #0d47a1; }
.icon { font-size: 1rem; }
</style>