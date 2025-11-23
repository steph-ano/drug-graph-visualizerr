<script setup>
import { ref } from 'vue';
import api from '../services/api';

// Modelo de datos del formulario
const filters = ref({
  condition: '',
  pregnancy_category: '',
  rx_otc: '',
  csa: ''
});

const results = ref([]);
const loading = ref(false);
const searched = ref(false);
const errorMsg = ref('');

const applyFilter = async () => {
  loading.value = true;
  searched.value = true;
  errorMsg.value = '';
  results.value = [];

  try {
    // 1. Limpiar el objeto: Eliminar claves vacías
    const payload = {};
    if (filters.value.condition.trim()) payload.condition = filters.value.condition;
    if (filters.value.pregnancy_category) payload.pregnancy_category = filters.value.pregnancy_category;
    if (filters.value.rx_otc) payload.rx_otc = filters.value.rx_otc;
    if (filters.value.csa) payload.csa = filters.value.csa;

    console.log("Enviando payload:", payload); // Mira la consola del navegador (F12)

    const response = await api.filterDrugs(payload);
    results.value = response.data;
    
  } catch (error) {
    console.error(error);
    errorMsg.value = "Error al conectar con el servidor. Revisa la terminal de Python.";
  } finally {
    loading.value = false;
  }
};

// Función para limpiar filtros
const clearFilters = () => {
  filters.value = { condition: '', pregnancy_category: '', rx_otc: '', csa: '' };
  results.value = [];
  searched.value = false;
};
</script>

<template>
  <div class="filter-container">
    <h1>🔬 Buscador Avanzado</h1>
    
    <div class="card filter-card">
      <div class="form-grid">
        
        <div class="form-group">
          <label>Condición Médica:</label>
          <input 
            v-model="filters.condition" 
            placeholder="Ej. Pain, Acne, Anxiety..." 
            @keyup.enter="applyFilter"
          />
        </div>

        <div class="form-group">
          <label>Categoría Embarazo:</label>
          <select v-model="filters.pregnancy_category">
            <option value="">Todas</option>
            <option value="A">A (Sin riesgo)</option>
            <option value="B">B (Probablemente seguro)</option>
            <option value="C">C (Riesgo no descartado)</option>
            <option value="D">D (Riesgo evidente)</option>
            <option value="X">X (Contraindicado)</option>
          </select>
        </div>

        <div class="form-group">
          <label>Tipo de Acceso:</label>
          <select v-model="filters.rx_otc">
            <option value="">Cualquiera</option>
            <option value="Rx">Rx (Con Receta)</option>
            <option value="OTC">OTC (Venta Libre)</option>
          </select>
        </div>

        <div class="form-group">
          <label>Clase CSA (Controlada):</label>
          <select v-model="filters.csa">
            <option value="">Cualquiera</option>
            <option value="N">N (No controlada)</option>
            <option value="2">2 (Alto potencial abuso)</option>
            <option value="3">3</option>
            <option value="4">4</option>
            <option value="5">5</option>
          </select>
        </div>
      </div>

      <div class="actions">
        <button @click="applyFilter" :disabled="loading" class="btn-search">
          {{ loading ? 'Buscando...' : '🔎 Aplicar Filtros' }}
        </button>
        <button @click="clearFilters" class="btn-clear">Limpiar</button>
      </div>
    </div>

    <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>

    <div v-if="searched" class="results-area">
      <h3>Resultados encontrados: {{ results.length }}</h3>
      
      <div v-if="results.length === 0 && !loading" class="no-results">
        No hay medicamentos que coincidan con estos criterios.
      </div>

      <div v-else class="table-responsive">
        <table>
          <thead>
            <tr>
              <th>Medicamento</th>
              <th>Condición</th>
              <th>Emb.</th>
              <th>Tipo</th>
              <th>CSA</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="drug in results" :key="drug.drug_name">
              <td class="fw-bold">{{ drug.drug_name }}</td>
              <td>{{ drug.medical_condition }}</td>
              <td>
                <span :class="['badge', 'cat-' + drug.pregnancy_category]">
                  {{ drug.pregnancy_category || '-' }}
                </span>
              </td>
              <td>{{ drug.rx_otc }}</td>
              <td>{{ drug.csa }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.filter-container { max-width: 900px; margin: 0 auto; }
.filter-card { padding: 20px; background: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }

.form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }
.form-group { display: flex; flex-direction: column; }
label { font-weight: 600; font-size: 0.9rem; margin-bottom: 5px; color: #555; }
input, select { padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 1rem; }
input:focus, select:focus { outline: none; border-color: #42b983; box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.1); }

.actions { display: flex; gap: 10px; justify-content: flex-end; }
.btn-search { background: #42b983; color: white; padding: 10px 20px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; transition: background 0.2s; }
.btn-search:hover { background: #3aa876; }
.btn-clear { background: #e0e0e0; color: #333; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; }
.btn-clear:hover { background: #d0d0d0; }

.error-msg { color: #d32f2f; background: #ffebee; padding: 10px; border-radius: 6px; margin-top: 10px; }
.results-area { margin-top: 30px; }
.no-results { text-align: center; padding: 40px; color: #888; font-style: italic; background: #f9f9f9; border-radius: 8px; }

.table-responsive { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #eee; }
th { background: #f8f9fa; font-weight: 600; color: #444; }
tr:hover { background: #f1f8ff; }
.fw-bold { font-weight: bold; color: #2c3e50; }

/* Badges para categorías de embarazo */
.badge { padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; color: white; background: #999; }
.cat-A { background: #2ecc71; }
.cat-B { background: #3498db; }
.cat-C { background: #f1c40f; color: #333; }
.cat-D { background: #e67e22; }
.cat-X { background: #e74c3c; }
</style>