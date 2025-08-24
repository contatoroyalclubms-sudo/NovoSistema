import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import path from 'path'
import { visualizer } from 'rollup-plugin-visualizer'
import { splitVendorChunkPlugin } from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react({
      // Enable React Fast Refresh with better optimization
      plugins: [
        ['@swc/plugin-styled-jsx', {}],
      ],
    }),
    splitVendorChunkPlugin(),
    // Bundle analyzer in development
    process.env.ANALYZE && visualizer({
      filename: 'dist/stats.html',
      open: true,
      gzipSize: true,
      brotliSize: true
    })
  ].filter(Boolean),
  server: {
    port: 4200,
    host: '0.0.0.0',
    open: false,
    cors: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('Sending Request to the Target:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
          });
        },
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@/components': path.resolve(__dirname, './src/components'),
      '@/pages': path.resolve(__dirname, './src/pages'),
      '@/services': path.resolve(__dirname, './src/services'),
      '@/types': path.resolve(__dirname, './src/types'),
      '@/utils': path.resolve(__dirname, './src/utils'),
      '@/contexts': path.resolve(__dirname, './src/contexts'),
      '@/hooks': path.resolve(__dirname, './src/hooks'),
      '@/lib': path.resolve(__dirname, './src/lib')
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: process.env.NODE_ENV === 'development',
    minify: 'terser',
    target: 'esnext',
    assetsDir: 'assets',
    cssCodeSplit: true,
    reportCompressedSize: false, // Faster builds
    terserOptions: {
      compress: {
        drop_console: process.env.NODE_ENV === 'production',
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.debug'],
      },
    },
    rollupOptions: {
      output: {
        // Advanced code splitting strategy
        manualChunks: (id) => {
          // React core
          if (id.includes('react') || id.includes('react-dom')) {
            return 'react-core';
          }
          
          // React Router
          if (id.includes('react-router')) {
            return 'react-router';
          }
          
          // UI components (Radix UI)
          if (id.includes('@radix-ui') || id.includes('lucide-react')) {
            return 'ui-components';
          }
          
          // Form handling
          if (id.includes('react-hook-form') || id.includes('@hookform') || id.includes('yup')) {
            return 'form-handling';
          }
          
          // Data fetching and state management
          if (id.includes('@tanstack/react-query') || id.includes('axios') || id.includes('swr')) {
            return 'data-management';
          }
          
          // Charts and visualization
          if (id.includes('recharts') || id.includes('chart')) {
            return 'charts';
          }
          
          // Animation libraries
          if (id.includes('framer-motion') || id.includes('react-transition')) {
            return 'animations';
          }
          
          // Date utilities
          if (id.includes('date-fns') || id.includes('moment') || id.includes('dayjs')) {
            return 'date-utils';
          }
          
          // CSS and styling utilities
          if (id.includes('clsx') || id.includes('tailwind-merge') || id.includes('class-variance-authority')) {
            return 'style-utils';
          }
          
          // Large third-party libraries
          if (id.includes('lodash') || id.includes('ramda')) {
            return 'utils-heavy';
          }
          
          // Testing utilities (should not be in production)
          if (id.includes('@testing-library') || id.includes('vitest') || id.includes('msw')) {
            return 'testing';
          }
          
          // Node modules that are not specifically categorized
          if (id.includes('node_modules')) {
            return 'vendor';
          }
          
          // App-specific chunks
          if (id.includes('/pages/') || id.includes('/routes/')) {
            return 'pages';
          }
          
          if (id.includes('/components/')) {
            // Split large component groups
            if (id.includes('/dashboard/')) return 'dashboard-components';
            if (id.includes('/eventos/')) return 'eventos-components';
            if (id.includes('/pdv/')) return 'pdv-components';
            if (id.includes('/auth/')) return 'auth-components';
            if (id.includes('/ui/')) return 'ui-base-components';
            return 'components';
          }
          
          if (id.includes('/services/')) {
            return 'services';
          }
          
          if (id.includes('/hooks/')) {
            return 'hooks';
          }
          
          if (id.includes('/utils/')) {
            return 'app-utils';
          }
        },
        // Optimize chunk file names
        chunkFileNames: (chunkInfo) => {
          const facadeModuleId = chunkInfo.facadeModuleId ? chunkInfo.facadeModuleId.split('/').pop() : 'chunk';
          return `js/[name]-[hash].js`;
        },
        entryFileNames: 'js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.');
          const ext = info[info.length - 1];
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(ext)) {
            return `images/[name]-[hash][extname]`;
          }
          if (/woff2?|eot|ttf|otf/i.test(ext)) {
            return `fonts/[name]-[hash][extname]`;
          }
          return `assets/[name]-[hash][extname]`;
        },
      },
    },
    chunkSizeWarningLimit: 800, // Reduced for better performance
  },
  define: {
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'development'),
    __DEV__: process.env.NODE_ENV === 'development',
    // Feature flags
    __ENABLE_ANALYTICS__: process.env.ENABLE_ANALYTICS === 'true',
    __ENABLE_PWA__: process.env.ENABLE_PWA === 'true',
  },
  optimizeDeps: {
    // Pre-bundle these for faster dev startup
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'axios',
      '@tanstack/react-query',
      'lucide-react',
      'clsx',
      'tailwind-merge',
      'date-fns',
      'framer-motion',
      'react-hook-form',
      'yup',
    ],
    // Exclude large libraries that should be loaded on demand
    exclude: [
      '@radix-ui/react-dialog',
      'recharts',
    ],
  },
  // Performance optimizations
  esbuild: {
    // Remove unused imports in production
    drop: process.env.NODE_ENV === 'production' ? ['console', 'debugger'] : [],
  },
  // CSS optimizations
  css: {
    modules: {
      localsConvention: 'camelCaseOnly',
    },
    postcss: {
      plugins: [
        // Add any PostCSS plugins for optimization
      ],
    },
  },
})