import { createApp } from 'vue'
import App from './App.vue'
import api from './services/api'

const app = createApp(App)
// make axios instance available as this.$api in components
app.config.globalProperties.$api = api

app.mount('#app')
