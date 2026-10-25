import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
 server: {
  host: '0.0.0.0',
  allowedHosts: ['lego-hurdle-circling.ngrok-free.dev'],
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
    },
    // Uploaded cover files are served by FastAPI at /uploads, not by Vite.
    '/uploads': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
    },
  },
},
})
