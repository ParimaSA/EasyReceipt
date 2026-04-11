import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      // Ensure imports from 'vue' resolve to the ESM bundler build so named exports
      // (computed, shallowRef, etc.) are available when Vite loads plugins/config.
      'vue': 'vue/dist/vue.runtime.esm-bundler.js',
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
      '/uploads': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})
