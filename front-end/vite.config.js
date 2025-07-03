import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'

// 📁 Ahora los .html están en el root del proyecto (no en /html)
const htmlDir = __dirname

const input = Object.fromEntries(
  fs.readdirSync(htmlDir)
    .filter(f => f.endsWith('.html'))
    .map(f => [
      path.basename(f, '.html'),         // entrada: 'login'
      path.resolve(htmlDir, f)           // salida: '/abs/path/login.html'
    ])
)

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      input,
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash][extname]'
      }
    }
  },
  server: {
    proxy: {
      '^/(auth|turnos|profesores|comprobantes)': 'http://localhost:5050'
    }
  }
})
