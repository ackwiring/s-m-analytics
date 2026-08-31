import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // The dev server must run on a different port than the FastAPI backend
    // (which is hardcoded to 1943 in webapp/backend/main.py) - they can't
    // both bind 1943 at once. Proxy target corrected to match the backend's
    // actual port (was pointing at 8000, where nothing listens).
    port: 5173,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://localhost:1943',
        changeOrigin: true,
      }
    }
  }
})

