import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig(async ({ mode }) => {
  const plugins = [vue()]
  if (mode === 'development' && process.env.VITE_DEVTOOLS === 'true') {
    // Import dinámico (solo se evalúa en desarrollo, nunca en producción)
    const { default: vueDevTools } = await import('vite-plugin-vue-devtools')
    plugins.push(vueDevTools())
  }
  return {
    plugins,
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      },
    },
  }
})
