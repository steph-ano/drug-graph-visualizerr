<script setup>
import { ref } from 'vue';
import api from '../services/api';

const query = ref('');
const suggestions = ref([]);
const selectedDrug = ref(null);
const error = ref('');
const loading = ref(false);

const onInput = async () => {
  if (query.value.length > 2) {
    try {
      const res = await api.searchDrugs(query.value);
      suggestions.value = res.data;
    } catch (e) {
      console.error(e);
    }
  } else {
    suggestions.value = [];
  }
};

const selectDrug = async (name) => {
  query.value = name;
  suggestions.value = []; // Ocultar sugerencias
  loading.value = true;
  selectedDrug.value = null;
  error.value = '';
  
  try {
    const res = await api.getDrugDetails(name);
    selectedDrug.value = res.data;
  } catch (err) {
    error.value = "No se encontró información detallada de este medicamento.";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="details-container">
    <h1>📋 Información Clínica</h1>
    
    <!-- Caja de Búsqueda -->
    <div class="card search-card">
      <div class="search-wrapper">
        <span class="search-icon">🔍</span>
        <input 
          v-model="query" 
          @input="onInput" 
          placeholder="Buscar medicamento (ej. Amoxicillin)..." 
          class="main-search"
        />
        <!-- Lista de Sugerencias -->
        <ul v-if="suggestions.length" class="suggestions-list">
          <li v-for="s in suggestions" :key="s" @click="selectDrug(s)">
            {{ s }}
          </li>
        </ul>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">Cargando datos...</div>

    <!-- Tarjeta de Detalles -->
    <div v-if="selectedDrug" class="card details-card">
      
      <!-- Encabezado del Medicamento -->
      <div class="drug-header">
        <div class="title-group">
          <h2>{{ selectedDrug.drug_name }}</h2>
          <span class="generic-name">{{ selectedDrug.generic_name }}</span>
        </div>
        <div class="access-badge">{{ selectedDrug.rx_otc || 'N/A' }}</div>
      </div>

      <hr class="divider">

      <!-- Grid de Información Clave -->
      <div class="info-grid">
        
        <div class="info-item">
          <span class="label">Condición Médica</span>
          <span class="value main-condition">{{ selectedDrug.medical_condition }}</span>
        </div>

        <div class="info-item">
          <span class="label">Clase Farmacológica</span>
          <span class="value">{{ selectedDrug.drug_classes }}</span>
        </div>

        <div class="info-item">
          <span class="label">Categoría Embarazo</span>
          <span :class="['badge-preg', 'cat-' + selectedDrug.pregnancy_category]">
            {{ selectedDrug.pregnancy_category || 'N/A' }}
          </span>
        </div>

        <div class="info-item">
          <span class="label">Control CSA</span>
          <span class="badge-csa">
             {{ selectedDrug.csa === 'N' ? 'No Controlado' : 'Clase ' + selectedDrug.csa }}
          </span>
        </div>

      </div>

      <!-- Sección de Efectos Secundarios -->
      <div class="side-effects-section">
        <h3>⚠️ Efectos Secundarios Reportados</h3>
        <p>{{ selectedDrug.side_effects }}</p>
      </div>

    </div>

    <!-- Error -->
    <div v-if="error" class="error-msg">{{ error }}</div>
  </div>
</template>

<style scoped>
.details-container { max-width: 800px; margin: 0 auto; }

/* --- Búsqueda --- */
.search-card { padding: 20px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 2rem; }
.search-wrapper { position: relative; display: flex; align-items: center; width: 100%; }
.search-icon { position: absolute; left: 15px; font-size: 1.2rem; color: #888; }
.main-search { width: 100%; padding: 12px 12px 12px 45px; font-size: 1.1rem; border: 1px solid #ddd; border-radius: 8px; transition: border-color 0.2s; }
.main-search:focus { outline: none; border-color: #2196f3; box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1); }

/* Autocompletado */
.suggestions-list { position: absolute; top: 100%; left: 0; right: 0; background: white; border: 1px solid #eee; border-radius: 8px; list-style: none; padding: 5px 0; margin-top: 5px; z-index: 100; box-shadow: 0 4px 12px rgba(0,0,0,0.1); max-height: 250px; overflow-y: auto; }
.suggestions-list li { padding: 10px 20px; cursor: pointer; color: #333; border-bottom: 1px solid #f9f9f9; }
.suggestions-list li:hover { background-color: #f0f7ff; color: #2196f3; }

/* --- Tarjeta de Detalles --- */
.details-card { background: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); overflow: hidden; animation: fadeIn 0.3s ease-in-out; }

/* Header */
.drug-header { padding: 25px 25px 15px 25px; display: flex; justify-content: space-between; align-items: flex-start; }
.title-group h2 { margin: 0; font-size: 1.8rem; color: #2c3e50; }
.generic-name { font-size: 1rem; color: #7f8c8d; font-style: italic; margin-top: 5px; display: block; }
.access-badge { background: #34495e; color: white; padding: 5px 10px; border-radius: 6px; font-weight: bold; font-size: 0.9rem; letter-spacing: 0.5px; }

.divider { border: 0; height: 1px; background: #eee; margin: 0 25px; }

/* Grid de Información */
.info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 20px; padding: 25px; }
.info-item { display: flex; flex-direction: column; gap: 5px; }
.label { font-size: 0.8rem; text-transform: uppercase; color: #95a5a6; font-weight: bold; letter-spacing: 0.5px; }
.value { font-size: 1.1rem; font-weight: 600; color: #2c3e50; }
.main-condition { color: #2196f3; }

/* Badges */
.badge-preg { display: inline-block; width: fit-content; padding: 4px 12px; border-radius: 20px; font-weight: bold; color: white; font-size: 0.9rem; }
.cat-A { background: #2ecc71; }
.cat-B { background: #3498db; }
.cat-C { background: #f1c40f; color: #333; }
.cat-D { background: #e67e22; }
.cat-X { background: #e74c3c; }
.cat-N { background: #95a5a6; }

.badge-csa { display: inline-block; width: fit-content; padding: 4px 10px; border-radius: 6px; background: #f0f2f5; color: #555; border: 1px solid #dcdfe6; font-size: 0.9rem; }

/* Efectos Secundarios */
.side-effects-section { background: #fff8f8; padding: 25px; border-top: 1px solid #ffebeb; }
.side-effects-section h3 { margin-top: 0; font-size: 1.1rem; color: #c0392b; display: flex; align-items: center; gap: 8px; }
.side-effects-section p { color: #555; line-height: 1.6; margin-bottom: 0; text-align: justify; }

/* Estados */
.loading-state { text-align: center; color: #888; font-style: italic; margin: 2rem 0; }
.error-msg { background: #ffebee; color: #c62828; padding: 15px; border-radius: 8px; margin-top: 20px; text-align: center; border: 1px solid #ffcdd2; }

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>