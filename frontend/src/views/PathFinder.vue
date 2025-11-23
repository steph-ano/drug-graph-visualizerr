<script setup>
import { ref, computed } from 'vue';
import api from '../services/api';
import GraphCanvas from '../components/GraphCanvas.vue'; // Importamos el grafo

const startDrug = ref('');
const endDrug = ref('');
const result = ref(null);
const error = ref('');
const loading = ref(false);

// --- Transformación de datos para el Grafo ---
const graphData = computed(() => {
  if (!result.value) return { nodes: [], edges: [] };

  const nodes = [];
  const edges = [];
  const path = result.value.path;

  path.forEach((step, index) => {
    // Determinar color: Inicio=Verde, Fin=Rojo, Medio=Azul
    let color = '#2196f3'; // Azul default
    if (index === 0) color = '#4caf50'; // Verde
    if (index === path.length - 1) color = '#f44336'; // Rojo

    nodes.push({
      id: step.name,
      label: step.name,
      color: { background: color, border: 'black' }
    });

    // Crear arista con el siguiente nodo
    if (index < path.length - 1) {
      edges.push({
        from: step.name,
        to: path[index + 1].name,
        label: step.similarity_to_next.toFixed(2), // Mostrar similitud en la línea
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
    error.value = err.response?.data?.detail || "Error al buscar el camino.";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div>
    <h1>🔍 Camino de Similitud (Visual)</h1>
    <div class="card controls">
      <input v-model="startDrug" placeholder="Inicio (ej. Aspirin)" />
      <input v-model="endDrug" placeholder="Fin (ej. Warfarin)" />
      <button @click="findPath" :disabled="loading">
        {{ loading ? 'Calculando...' : 'Ver Grafo' }}
      </button>
    </div>

    <div v-if="error" class="error-msg">{{ error }}</div>

    <div v-if="result" class="results-container">
      <div class="summary">
        <h3>Ruta Encontrada</h3>
        <p>Pasos: {{ result.steps }} | Similitud Total: <strong>{{ result.total_similarity }}</strong></p>
      </div>

      <GraphCanvas 
        :nodes="graphData.nodes" 
        :edges="graphData.edges" 
      />
    </div>
  </div>
</template>

<style scoped>
.controls { display: flex; gap: 10px; margin-bottom: 1rem; }
.error-msg { color: red; margin: 1rem 0; }
.summary { margin-bottom: 10px; }
</style>