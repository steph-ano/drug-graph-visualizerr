<script setup>
import { ref, onMounted, watch } from 'vue';
import { Network } from 'vis-network';

const props = defineProps({
  nodes: Array, // Espera formato: [{ id: 1, label: 'A', color: '...' }]
  edges: Array  // Espera formato: [{ from: 1, to: 2, label: '0.5' }]
});

const container = ref(null);
let network = null;

const drawGraph = () => {
  if (!container.value) return;

  const data = {
    nodes: props.nodes,
    edges: props.edges
  };

  const options = {
    nodes: {
      shape: 'dot',
      size: 20,
      font: { size: 14, color: '#000' },
      borderWidth: 2
    },
    edges: {
      width: 2,
      color: { color: '#848484' },
      smooth: { type: 'continuous' } // Curvas suaves
    },
    physics: {
      stabilization: false,
      barnesHut: {
        gravitationalConstant: -8000, // Qué tanto se repelen
        springConstant: 0.04,
        springLength: 95
      }
    },
    interaction: { hover: true }
  };

  network = new Network(container.value, data, options);
};

// Dibujar al montar
onMounted(() => {
  if (props.nodes.length) drawGraph();
});

// Redibujar si cambian los datos
watch(() => props.nodes, () => {
  drawGraph();
}, { deep: true });
</script>

<template>
  <div ref="container" class="network-container"></div>
</template>

<style scoped>
.network-container {
  width: 100%;
  height: 500px; /* Altura fija para el grafo */
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #ffffff;
}
</style>