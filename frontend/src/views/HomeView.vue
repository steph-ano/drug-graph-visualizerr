<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';

const stats = ref(null);
const loading = ref(true);
const errorMsg = ref('');

onMounted(async () => {
  try {
    const response = await api.getStats();
    stats.value = response.data;
  } catch (error) {
    console.error(error);
    errorMsg.value = "No se pudo conectar con el servidor Backend.";
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="home-container">
    
    <!-- Hero Header -->
    <header class="hero">
      <div class="icon-wrapper">💊</div>
      <h1>Gestor de Medicamentos</h1>
      <p class="subtitle">
        Plataforma de análisis de interacciones y relaciones farmacológicas basada en teoría de grafos.
      </p>
    </header>
    
    <!-- Estado de Carga -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Conectando con el sistema...</p>
    </div>
    
    <!-- Dashboard de Estadísticas -->
    <div v-else-if="stats" class="dashboard-grid">
      
      <!-- Tarjeta 1: Estado del Sistema -->
      <div class="stat-card status-card">
        <div class="card-icon">📡</div>
        <div class="card-content">
          <h3>Estado del Sistema</h3>
          <div class="status-indicator">
            <span class="dot pulse"></span>
            <span class="value">{{ stats.status.toUpperCase() }}</span>
          </div>
        </div>
      </div>

      <!-- Tarjeta 2: Tamaño de la Base de Datos -->
      <div class="stat-card data-card">
        <div class="card-icon">🔗</div>
        <div class="card-content">
          <h3>Nodos en el Grafo</h3>
          <span class="value number">{{ stats.nodes }}</span>
          <span class="label-small">Medicamentos indexados</span>
        </div>
      </div>

    </div>
    
    <!-- Estado de Error -->
    <div v-else class="error-state">
      <span class="error-icon">⚠️</span>
      <h3>Conexión Fallida</h3>
      <p>{{ errorMsg }}</p>
      <small>Asegúrate de que el backend (Flask) esté ejecutándose en el puerto 8000.</small>
    </div>

  </div>
</template>

<style scoped>
.home-container { max-width: 800px; margin: 0 auto; padding-top: 2rem; text-align: center; }

/* --- Hero Section --- */
.hero { margin-bottom: 3rem; animation: fadeIn 0.5s ease-out; }
.icon-wrapper { font-size: 4rem; margin-bottom: 10px; display: inline-block; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1)); }
h1 { color: #2c3e50; margin-bottom: 0.5rem; font-size: 2.2rem; }
.subtitle { color: #7f8c8d; font-size: 1.1rem; max-width: 600px; margin: 0 auto; line-height: 1.5; }

/* --- Dashboard Grid --- */
.dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; animation: slideUp 0.5s ease-out; }

/* --- Stat Cards --- */
.stat-card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); display: flex; align-items: center; gap: 20px; transition: transform 0.2s, box-shadow 0.2s; border: 1px solid #f0f0f0; }
.stat-card:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); }

.card-icon { font-size: 2.5rem; background: #f8f9fa; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; border-radius: 50%; }

.card-content { text-align: left; display: flex; flex-direction: column; }
.card-content h3 { margin: 0 0 5px 0; font-size: 1rem; color: #95a5a6; text-transform: uppercase; letter-spacing: 0.5px; }

/* Tipografía de valores */
.value { font-size: 1.5rem; font-weight: 800; color: #2c3e50; }
.number { color: #2196f3; font-size: 2rem; line-height: 1; }
.label-small { font-size: 0.85rem; color: #bdc3c7; margin-top: 5px; }

/* Indicador de estado (Punto verde pulsante) */
.status-indicator { display: flex; align-items: center; gap: 10px; }
.dot { width: 10px; height: 10px; background-color: #2ecc71; border-radius: 50%; display: inline-block; }
.pulse { box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.7); animation: pulse-green 2s infinite; }

/* --- Estados de Carga y Error --- */
.loading-state { color: #7f8c8d; margin-top: 3rem; font-style: italic; }
.error-state { background: #fff5f5; border: 1px solid #ffcccc; padding: 30px; border-radius: 12px; color: #c0392b; margin-top: 2rem; }
.error-icon { font-size: 3rem; display: block; margin-bottom: 10px; }

/* Animaciones */
@keyframes pulse-green {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(46, 204, 113, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(46, 204, 113, 0); }
}

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>