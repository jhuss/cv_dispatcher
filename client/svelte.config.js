import sveltePreprocess from 'svelte-preprocess'
import postcssMinify from 'postcss-minify'

export default {
  // Consult https://github.com/sveltejs/svelte-preprocess
  // for more information about preprocessors
  preprocess: [
    sveltePreprocess({
      includePaths: [
        'node_modules',
        'src'
      ],
      postcss: {
        plugins: [
          postcssMinify
        ]
      }
    })
  ]
}
