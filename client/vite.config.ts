import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import { replaceCodePlugin } from 'vite-plugin-replace'
import { appConfig, useSSL } from './vite_utils'

const config = appConfig()

// https://vitejs.dev/config/
export default defineConfig({
  server: {
    host: config.dev.front.server.name,
    port: config.dev.front.server.port,
    strictPort: true,
    https: useSSL(config.dev.front.server.ssl)
  },
  plugins: [
    svelte(),
    replaceCodePlugin({
      replacements: [
        {
          from: /__TITLE__/gm,
          to: config.page.title,
        },
        {
          from: /__HEADER__/gm,
          to: config.page.header,
        },
        {
          from: /__DESCRIPTION__/gm,
          to: config.page.description,
        },
        {
          from: /__SERVER__/gm,
          to: `${(config.url.https) ? 'https' : 'http'}://${config.url.base}`,
        },
      ]
    }),
  ]
})
