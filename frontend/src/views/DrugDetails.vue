<script setup>
import { ref } from 'vue';
import api from '../services/api';

const query = ref('');
const suggestions = ref([]);
const selectedDrug = ref(null);
const error = ref('');

const onInput = async () => {
  if (query.value.length > 2) {
    const res = await api.searchDrugs(query.value);
    suggestions.value = res.data;
  } else {
    suggestions.value = [];
  }
};

const selectDrug = async (name) => {
  query.value = name;
  suggestions.value = []; // Ocultar sugerencias
  try {
    const res = await api.getDrugDetails(name);
    selectedDrug.value = res.data;
    error.value = '';
  } catch (err) {
    error.value = "No se encontró información detallada.";
  }
};
</script>

<template>
  <div>
    <h1>📋 Información Detallada</h1>
    
    <div class="search-box">
      <input 
        v-model="query" 
        @input="onInput" 
        placeholder="Escribe para buscar..." 
        class="main-search"
      />
      <ul v-if="suggestions.length" class="suggestions">
        <li v-for="s in suggestions" :key="s" @click="selectDrug(s)">
          {{ s }}
        </li>
      </ul>
    </div>

    <div v-if="selectedDrug" class="card details-card">
      <h2>{{ selectedDrug.drug_name }}</h2>
      <div class="detail-row"><strong>Genérico:</strong> {{ selectedDrug.generic_name }}</div>
      <div class="detail-row"><strong>Clases:</strong> {{ selectedDrug.drug_classes }}</div>
      <div class="detail-row"><strong>Condición:</strong> {{ selectedDrug.medical_condition }}</div>
      <div class="detail-row"><strong>Categoría Embarazo:</strong> {{ selectedDrug.pregnancy_category }}</div>
      <div class="detail-row"><strong>CSA (Controlada):</strong> {{ selectedDrug.csa }}</div>
      <div class="detail-row full">
        <strong>Efectos Secundarios:</strong>
        <p>{{ selectedDrug.side_effects }}</p>
      </div>
    </div>
    <div v-if="error" class="error-msg">{{ error }}</div>
  </div>
</template>

<style scoped>
.search-box { position: relative; max-width: 500px; margin-bottom: 2rem; }
.main-search { width: 100%; padding: 10px; font-size: 1.1rem; }
.suggestions { position: absolute; top: 100%; left: 0; right: 0; background: white; border: 1px solid #ddd; list-style: none; padding: 0; margin: 0; z-index: 10; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
.suggestions li { padding: 10px; cursor: pointer; border-bottom: 1px solid #eee; }
.suggestions li:hover { background-color: #f0f0f0; }

.details-card { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.detail-row.full { grid-column: span 2; margin-top: 1rem; border-top: 1px solid #eee; padding-top: 1rem; }
h2 { grid-column: span 2; color: #2c3e50; border-bottom: 2px solid #42b983; padding-bottom: 0.5rem; }
</style>