<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="app-container">
    <nav class="navbar">
      <div class="logo">💊 DrugGraph</div>
      <div class="links">
        <RouterLink to="/">Inicio</RouterLink>
        <RouterLink to="/path">Ruta (Dijkstra)</RouterLink>
        <RouterLink to="/alternatives">Alternativas</RouterLink>
        <RouterLink to="/filter">Filtrar</RouterLink>
        <RouterLink to="/details">Detalles</RouterLink>
      </div>
    </nav>

    <main class="content">
      <RouterView />
    </main>
  </div>
</template>

<style>
/* Estilos Globales Simples */
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  margin: 0;
  background-color: #f4f7f6;
  color: #333;
}

.navbar {
  background-color: #2c3e50;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
}

.logo { font-weight: bold; font-size: 1.2rem; }

.links a {
  color: #ddd;
  text-decoration: none;
  margin-left: 1.5rem;
  transition: color 0.3s;
}

.links a:hover, .links a.router-link-active {
  color: #42b983;
}

.content {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

button {
  background-color: #42b983;
  border: none;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}
button:hover { background-color: #3aa876; }
button:disabled { background-color: #ccc; cursor: not-allowed;}

input, select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-right: 0.5rem;
}

.card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  margin-bottom: 1rem;
}
</style>