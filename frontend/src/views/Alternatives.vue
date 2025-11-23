<script setup>
import { ref, computed } from 'vue';
import api from '../services/api';
import GraphCanvas from '../components/GraphCanvas.vue';

const drugName = ref('');
const alternatives = ref([]);
const error = ref('');
const hasSearched = ref(false);

// --- Transformación de datos ---
const graphData = computed(() => {
  if (!alternatives.value.length) return { nodes: [], edges: [] };

  const centerNodeId = drugName.value; // El nodo central
  const nodes = [];
  const edges = [];

  // 1. Agregar nodo central (Rojo grande)
  nodes.push({
    id: 'CENTER', // Usamos ID fijo o el nombre para evitar duplicados visuales
    label: centerNodeId,
    color: { background: '#f44336', border: '#b71c1c' },
    size: 30,
    font: { size: 18, color: 'white', face: 'arial' }
  });

  // 2. Agregar satélites
  alternatives.value.forEach(alt => {
    nodes.push({
      id: alt.name,
      label: alt.name,
      color: '#2196f3', // Azul
      title: `Trata: ${alt.medical_condition}` // Tooltip al pasar el mouse
    });

    edges.push({
      from: 'CENTER',
      to: alt.name,
      label: alt.similarity.toFixed(2)
    });
  });

  return { nodes, edges };
});

const search = async () => {
  error.value = '';
  hasSearched.value = true;
  try {
    const response = await api.getAlternatives(drugName.value);
    alternatives.value = response.data;
  } catch (err) {
    alternatives.value = [];
    error.value = err.response?.data?.detail || "Error buscando alternativas.";
  }
};
</script>

<template>
  <div>
    <h1>💊 Red de Alternativas</h1>
    <div class="card controls">
      <input v-model="drugName" placeholder="Medicamento (ej. Xanax)" @keyup.enter="search" />
      <button @click="search">Graficar</button>
    </div>

    <div v-if="error" class="error-msg">{{ error }}</div>

    <div v-if="hasSearched && alternatives.length > 0">
       <GraphCanvas 
        :nodes="graphData.nodes" 
        :edges="graphData.edges" 
      />
      
      <div class="list-container">
        <h3>Detalles de Alternativas</h3>
        <ul>
          <li v-for="alt in alternatives" :key="alt.name">
            <strong>{{ alt.name }}</strong> ({{ alt.similarity.toFixed(2) }}) - {{ alt.medical_condition }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
.controls { margin-bottom: 1rem; }
.list-container { margin-top: 2rem; color: #555; }
</style>