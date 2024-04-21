import {fileURLToPath, URL} from 'node:url'

import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
      '/api/v1': {
        target: 'https://it-bookshelf.ru',
        changeOrigin: true,
        secure: false,
        ws: true,
      },
      '/media': { target: 'https://it-bookshelf.ru', secure: false },
    }
  }
})
