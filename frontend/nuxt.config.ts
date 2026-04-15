export default defineNuxtConfig({
  modules: ['@nuxt/ui', '@pinia/nuxt'],

  colorMode: {
    preference: 'dark',
    fallback: 'dark',
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api',
    },
  },

  devtools: { enabled: true },

  app: {
    head: {
      title: 'Marketing Studio',
      meta: [
        { name: 'description', content: 'AI Marketing Studio for E-Commerce Brands' },
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
      ],
    },
  },

  compatibilityDate: '2025-01-01',
})
