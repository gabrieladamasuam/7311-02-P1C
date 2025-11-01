import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Muestra el overlay de Vue DevTools solo si arrancas con VITE_DEVTOOLS=true
  const enableDevtools = mode === 'development' && process.env.VITE_DEVTOOLS === 'true'
  return {
    plugins: [
      vue(),
      enableDevtools && vueDevTools(),
    ].filter(Boolean),
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      },
    },
  }
})
