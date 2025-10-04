import {fileURLToPath, URL} from 'node:url'

import {defineConfig} from 'vite'
import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        vue(),
        tailwindcss(),
    ],
    build: {
        rollupOptions: {
            output: {
                manualChunks(id) {
                    if (id.indexOf('node_modules') !== -1) {
                        return id.toString().split("node_modules/")[1].split("/")[0].toString();
                    }
                }
            }
        }
    },
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    },
    server: {
        proxy: {
            '/api/v1': {
                target: 'http://127.0.0.1:8080',
                changeOrigin: true,
                secure: false,
                ws: true,
            },
            '/media': {target: 'http://127.0.0.1:8080', secure: false},
        }
    },
    optimizeDeps: {
        exclude: ["vue-recaptcha"]
    }
})
