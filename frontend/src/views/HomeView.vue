<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';

const stats = ref(null);
const loading = ref(true);

onMounted(async () => {
  try {
    const response = await api.getStats();
    stats.value = response.data;
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="home">
    <h1>Bienvenido al Gestor de Medicamentos</h1>
    <p>Esta aplicación utiliza grafos para analizar relaciones entre medicamentos.</p>
    
    <div v-if="loading" class="loading">Cargando datos del servidor...</div>
    
    <div v-else-if="stats" class="stats-card card">
      <h2>Estado del Sistema</h2>
      <div class="stat-item">
        <span class="label">Estado API:</span>
        <span class="value active">{{ stats.status }}</span>
      </div>
      <div class="stat-item">
        <span class="label">Nodos en Grafo:</span>
        <span class="value">{{ stats.nodes }}</span>
      </div>
    </div>
    
    <div v-else class="error">
      No se pudo conectar con el Backend.
    </div>
  </div>
</template>

<style scoped>
.active { color: green; font-weight: bold; }
.stat-item { margin: 10px 0; font-size: 1.1rem; }
</style>