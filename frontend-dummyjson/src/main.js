import { createApp } from 'vue'
import App from './App.vue'
import api from './services/api'

const app = createApp(App)
// Hacemos que la instancia de Axios esté disponible como this.$api en todos los componentes
app.config.globalProperties.$api = api

app.mount('#app')