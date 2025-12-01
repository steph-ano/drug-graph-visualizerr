<script setup>
import { ref } from 'vue';
import api from '../services/api';

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
    const payload = {};
    if (filters.value.condition.trim()) payload.condition = filters.value.condition;
    if (filters.value.pregnancy_category) payload.pregnancy_category = filters.value.pregnancy_category;
    if (filters.value.rx_otc) payload.rx_otc = filters.value.rx_otc;
    if (filters.value.csa) payload.csa = filters.value.csa;

    const response = await api.filterDrugs(payload);
    results.value = response.data;
  } catch (error) {
    console.error(error);
    errorMsg.value = "Error al conectar con el servidor.";
  } finally {
    loading.value = false;
  }
};

const clearFilters = () => {
  filters.value = { condition: '', pregnancy_category: '', rx_otc: '', csa: '' };
  results.value = [];
  searched.value = false;
};
</script>

<template>
  <div class="filter-container">
    <h1>🔬 Buscador Avanzado</h1>
    
    <!-- Tarjeta de Filtros -->
    <div class="card filter-card">
      <div class="form-grid">
        
        <!-- Condición Médica (Ocupa todo el ancho) -->
        <div class="form-group full-width">
          <label>Condición Médica</label>
          <input 
            v-model="filters.condition" 
            placeholder="Ej. Pain, Acne, Anxiety..." 
            @keyup.enter="applyFilter"
            class="input-control"
          />
        </div>

        <div class="form-group">
          <label>Cat. Embarazo</label>
          <select v-model="filters.pregnancy_category" class="input-control">
            <option value="">Todas</option>
            <option value="A">A (Sin riesgo)</option>
            <option value="B">B (Probablemente seguro)</option>
            <option value="C">C (Riesgo no descartado)</option>
            <option value="D">D (Riesgo evidente)</option>
            <option value="X">X (Contraindicado)</option>
          </select>
        </div>

        <div class="form-group">
          <label>Acceso</label>
          <select v-model="filters.rx_otc" class="input-control">
            <option value="">Cualquiera</option>
            <option value="Rx">Rx (Con Receta)</option>
            <option value="OTC">OTC (Venta Libre)</option>
          </select>
        </div>

        <div class="form-group">
          <label>Clase CSA</label>
          <select v-model="filters.csa" class="input-control">
            <option value="">Cualquiera</option>
            <option value="N">N (No controlada)</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="4">4</option>
            <option value="5">5</option>
          </select>
        </div>

      </div>

      <div class="actions">
        <button @click="clearFilters" class="btn-clear">
          Limpiar Campos
        </button>
        <button @click="applyFilter" :disabled="loading" class="btn-search">
          {{ loading ? 'Buscando...' : '🔎 Buscar Medicamentos' }}
        </button>
      </div>
    </div>

    <!-- Mensaje de Error -->
    <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>

    <!-- Resultados -->
    <div v-if="searched" class="results-area">
      <div class="results-header">
        <h3>Resultados encontrados</h3>
        <span class="badge-count">{{ results.length }}</span>
      </div>

      <div v-if="results.length === 0 && !loading" class="no-results">
        <span class="icon">📭</span>
        <p>No se encontraron medicamentos con estos criterios.</p>
      </div>

      <div v-else class="table-responsive">
        <table class="modern-table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Condición</th>
              <th>Emb.</th>
              <th>Tipo</th>
              <th>CSA</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="drug in results" :key="drug.drug_name">
              <td class="drug-name-cell">{{ drug.drug_name }}</td>
              <td>{{ drug.medical_condition }}</td>
              <td>
                <span :class="['badge-preg', 'cat-' + drug.pregnancy_category]">
                  {{ drug.pregnancy_category || 'N/A' }}
                </span>
              </td>
              <td>
                <span class="rx-badge">{{ drug.rx_otc }}</span>
              </td>
              <td>{{ drug.csa }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.filter-container { max-width: 900px; margin: 0 auto; padding-bottom: 3rem; }

/* --- Tarjeta de Filtros --- */
.filter-card { padding: 30px; background: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 2rem; border: 1px solid #f0f0f0; }

.form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 25px; }

/* Hace que el elemento ocupe todo el ancho disponible */
.full-width { grid-column: 1 / -1; }

.form-group { display: flex; flex-direction: column; gap: 8px; }
label { font-weight: 600; font-size: 0.85rem; text-transform: uppercase; color: #95a5a6; letter-spacing: 0.5px; }

.input-control { padding: 12px; border: 1px solid #e0e0e0; border-radius: 8px; font-size: 1rem; color: #2c3e50; background: #fafafa; transition: all 0.2s; width: 100%; }
.input-control:focus { outline: none; border-color: #2196f3; background: white; box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1); }

/* Botones */
.actions { display: flex; gap: 15px; justify-content: flex-end; padding-top: 10px; border-top: 1px solid #f5f5f5; }

.btn-search { background: #2196f3; color: white; padding: 12px 25px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; transition: background 0.2s, transform 0.1s; display: flex; align-items: center; gap: 8px; }
.btn-search:hover:not(:disabled) { background: #1976d2; transform: translateY(-1px); }
.btn-search:disabled { background: #bdc3c7; cursor: not-allowed; }

.btn-clear { background: white; color: #7f8c8d; padding: 12px 20px; border: 1px solid #e0e0e0; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.btn-clear:hover { background: #f8f9fa; color: #333; border-color: #d0d0d0; }

/* --- Resultados --- */
.results-area { animation: fadeIn 0.3s ease-in-out; }
.results-header { display: flex; align-items: center; gap: 10px; margin-bottom: 15px; }
.results-header h3 { margin: 0; color: #2c3e50; font-size: 1.2rem; }
.badge-count { background: #e3f2fd; color: #2196f3; padding: 2px 8px; border-radius: 10px; font-weight: bold; font-size: 0.9rem; }

.no-results { text-align: center; padding: 40px; background: #fff; border-radius: 12px; color: #7f8c8d; border: 1px dashed #e0e0e0; }
.no-results .icon { font-size: 2rem; display: block; margin-bottom: 10px; }

/* --- Tabla --- */
.table-responsive { overflow-x: auto; background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #f0f0f0; }
.modern-table { width: 100%; border-collapse: collapse; }

.modern-table th { background: #f8f9fa; color: #444; font-weight: 600; text-align: left; padding: 15px; border-bottom: 2px solid #eee; white-space: nowrap; }
.modern-table td { padding: 15px; border-bottom: 1px solid #f5f5f5; color: #555; font-size: 0.95rem; }
.modern-table tr:last-child td { border-bottom: none; }
.modern-table tr:hover { background-color: #f0f7ff; }

.drug-name-cell { font-weight: bold; color: #2c3e50; }
.rx-badge { font-size: 0.8rem; background: #f0f2f5; padding: 2px 6px; border-radius: 4px; color: #606266; border: 1px solid #dcdfe6; }

/* --- Badges de Embarazo --- */
.badge-preg { display: inline-block; padding: 4px 10px; border-radius: 20px; font-weight: bold; color: white; font-size: 0.8rem; text-align: center; min-width: 30px; }
.cat-A { background: #2ecc71; }
.cat-B { background: #3498db; }
.cat-C { background: #f1c40f; color: #333; }
.cat-D { background: #e67e22; }
.cat-X { background: #e74c3c; }
.cat-N { background: #95a5a6; }

.error-msg { background: #ffebee; color: #c62828; padding: 15px; border-radius: 8px; margin-bottom: 20px; text-align: center; border: 1px solid #ffcdd2; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>