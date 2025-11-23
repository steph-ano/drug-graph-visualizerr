import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import './style.css' // Estilos base de Vite

const app = createApp(App)
app.use(router)
app.mount('#app')