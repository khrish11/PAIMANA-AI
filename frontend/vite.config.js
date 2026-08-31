import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    watch: {
      // Ignore large data directories to prevent performance issues
      ignored: [
        '**/data/**',
        '**/node_modules/**',
        '**/dist/**',
        '**/.git/**',
        '**/__pycache__/**',
        '**/*.pyc',
      ],
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
});
