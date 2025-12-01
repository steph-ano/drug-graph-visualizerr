<script setup>
import { ref, computed } from 'vue';
import api from '../services/api';
import GraphCanvas from '../components/GraphCanvas.vue';

const drugName = ref('');
const alternatives = ref([]);
const error = ref('');
const hasSearched = ref(false);
const loading = ref(false);
const commonCondition = ref(null);

// --- Transformación de datos para el Grafo ---
const graphData = computed(() => {
  if (!alternatives.value.length) return { nodes: [], edges: [] };

  const centerNodeId = drugName.value;
  const nodes = [];
  const edges = [];

  nodes.push({
    id: 'CENTER', 
    label: centerNodeId,
    color: { background: '#f44336', border: '#b71c1c' },
    size: 30,
    font: { size: 18, color: 'white', face: 'arial' }
  });

  alternatives.value.forEach(alt => {
    // Color del nodo según calidad del match
    let nodeColor = '#2196f3'; // Azul por defecto (0.7)
    if (alt.match_code === 'FULL') nodeColor = '#4caf50'; // Verde (1.0)
    if (alt.match_code === 'CLASS') nodeColor = '#ff9800'; // Naranja (0.5)

    nodes.push({
      id: alt.name,
      label: alt.name,
      color: nodeColor,
      title: `${alt.match_type}\nTrata: ${alt.medical_condition}`
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
  if (!drugName.value) return;
  loading.value = true;
  error.value = '';
  hasSearched.value = true;
  alternatives.value = [];
  commonCondition.value = null;

  try {
    const response = await api.getAlternatives(drugName.value);
    alternatives.value = response.data;

    if (alternatives.value.length > 0) {
      const firstCondition = alternatives.value[0].medical_condition;
      const allSame = alternatives.value.every(alt => alt.medical_condition === firstCondition);
      if (allSame) commonCondition.value = firstCondition;
    }
  } catch (err) {
    alternatives.value = [];
    error.value = err.response?.data?.detail || "No se encontraron alternativas o hubo un error.";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="alternatives-container">
    <h1>💊 Red de Alternativas</h1>
    
    <div class="card controls">
      <div class="input-group">
        <input v-model="drugName" placeholder="Medicamento (ej. Xanax)" @keyup.enter="search" />
      </div>
      <button @click="search" :disabled="loading" class="btn-action">
        {{ loading ? 'Buscando...' : 'Graficar Alternativas' }}
      </button>
    </div>

    <div v-if="error" class="error-msg">{{ error }}</div>

    <div v-if="hasSearched && alternatives.length > 0" class="results-wrapper">
       
      <div class="graph-box">
        <GraphCanvas :nodes="graphData.nodes" :edges="graphData.edges" />
      </div>

      <div class="details-box">
        <h3>📄 Lista de Alternativas Sugeridas</h3>
        
        <div class="subtitle-block">
            <p>Ordenadas por similitud con <strong>{{ drugName }}</strong></p>
            <span v-if="commonCondition" class="common-badge">
                <span class="icon">🩺</span> Condición común: <strong>{{ commonCondition }}</strong>
            </span>
        </div>
        
        <div class="timeline">
          <div v-for="(alt, index) in alternatives" :key="alt.name" class="timeline-item">
            
            <div class="drug-node">
              <span class="step-index">{{ index + 1 }}</span>
              <span class="drug-name">{{ alt.name }}</span>
            </div>

            <div class="connection-detail">
              <div class="line"></div>
              <div class="info-bubble">
                
                <!-- Puntuación y Tipo de Match -->
                <div class="score-row">
                    <span class="sim-score">Similitud: {{ alt.similarity.toFixed(2) }}</span>
                    <!-- Badge dinámico según tipo de match -->
                    <span :class="['match-badge', 'badge-' + alt.match_code]">
                        {{ alt.match_type }}
                    </span>
                </div>

                <!-- Detalles adicionales (Clase o Condición si no es común) -->
                <div class="extra-info">
                    <span v-if="!commonCondition" class="info-item">
                        <span class="icon">🩺</span> {{ alt.medical_condition }}
                    </span>
                    <!-- Mostrar clase si es match full para reforzar el 1.0 -->
                    <span v-if="alt.match_code === 'FULL'" class="info-item text-small">
                        <span class="icon">🧪</span> Clase: {{ alt.drug_classes }}
                    </span>
                </div>

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
.alternatives-container { max-width: 900px; margin: 0 auto; }
.controls { display: flex; flex-direction: column; gap: 15px; align-items: center; margin-bottom: 20px; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.input-group { width: 100%; display: flex; justify-content: center; }
.input-group input { padding: 12px; width: 60%; border: 1px solid #ddd; border-radius: 6px; font-size: 1rem; }
.btn-action { padding: 10px 30px; background: #2196f3; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; transition: 0.2s; }
.btn-action:hover:not(:disabled) { background: #1976d2; }
.btn-action:disabled { background: #ccc; }
.error-msg { background: #ffebee; color: #c62828; padding: 15px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
.graph-box { height: 500px; border: 1px solid #eee; border-radius: 10px; background: #fafafa; margin-bottom: 30px; overflow: hidden; }

/* Estilos de Detalle */
.details-box { background: white; border-radius: 10px; padding: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.details-box h3 { margin-top: 0; margin-bottom: 5px; color: #333; }
.subtitle-block { margin-bottom: 25px; border-bottom: 2px solid #f0f0f0; padding-bottom: 15px; }
.subtitle-block p { margin: 0 0 10px 0; color: #666; }

.common-badge { display: inline-block; color: #2e7d32; background: #e8f5e9; padding: 4px 12px; border-radius: 20px; border: 1px solid #c8e6c9; font-size: 0.9rem; }

.timeline { display: flex; flex-direction: column; }
.timeline-item { display: flex; flex-direction: column; align-items: flex-start; margin-bottom: 5px; }
.drug-node { display: flex; align-items: center; gap: 15px; padding: 5px 0; }
.step-index { background: #333; color: white; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; border-radius: 50%; font-weight: bold; font-size: 0.9rem; }
.drug-name { font-size: 1.2rem; font-weight: bold; color: #2c3e50; }

.connection-detail { margin-left: 13px; border-left: 2px dashed #ccc; padding-left: 30px; padding-top: 10px; padding-bottom: 10px; width: 100%; }
.info-bubble { background: #f8f9fa; border: 1px solid #eee; padding: 12px 15px; border-radius: 6px; display: flex; flex-direction: column; gap: 8px; width: fit-content; min-width: 300px; }

/* Fila de Scores */
.score-row { display: flex; align-items: center; gap: 15px; }
.sim-score { font-size: 0.9rem; color: #555; font-weight: bold; }

/* Badges de Match */
.match-badge { font-size: 0.75rem; padding: 2px 8px; border-radius: 4px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; }
.badge-FULL { background: #e8f5e9; color: #2e7d32; border: 1px solid #a5d6a7; } /* Verde */
.badge-COND { background: #e3f2fd; color: #1565c0; border: 1px solid #90caf9; } /* Azul */
.badge-CLASS { background: #fff3e0; color: #ef6c00; border: 1px solid #ffcc80; } /* Naranja */

.extra-info { display: flex; flex-direction: column; gap: 2px; }
.info-item { font-size: 0.9rem; color: #444; display: flex; align-items: center; gap: 6px; }
.text-small { font-size: 0.8rem; color: #666; font-style: italic; }
.icon { font-size: 1rem; }
</style>