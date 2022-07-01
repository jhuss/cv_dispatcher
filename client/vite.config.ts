import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import { replaceCodePlugin } from 'vite-plugin-replace'
import { createHtmlPlugin } from 'vite-plugin-html'
import { appConfig, useSSL } from './vite_utils'

const config = appConfig()
let server_url = `${(config.url.https) ? 'https' : 'http'}://${config.url.base}`
const viteConfig = {}

if (config.dev) {
  viteConfig['server'] = {
    host: config.dev.front.server.name,
    port: config.dev.front.server.port,
    strictPort: true,
    https: useSSL(config.dev.front.server.ssl),
    proxy: {
      '/backend': {
        target: server_url,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/backend/, '')
      }
    }
  }

  server_url = `${(config.dev.front.server.ssl.enable) ? 'https' : 'http'}://${config.dev.front.server.name}:${config.dev.front.server.port}/backend`
}

viteConfig['plugins'] = [
  svelte(),
  createHtmlPlugin({
    template: 'index.html',
    inject: {
      data: {
        title: config.page.title,
      }
    }
  }),
  replaceCodePlugin({
    replacements: [
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
        to: server_url,
      },
    ]
  }),
]

// https://vitejs.dev/config/
export default defineConfig(viteConfig)
