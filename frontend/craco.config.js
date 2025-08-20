// Load configuration from environment or config file
const path = require('path');

// Environment variable overrides
const config = {
  disableHotReload: process.env.DISABLE_HOT_RELOAD === 'true',
};

module.exports = {
  webpack: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
    configure: (webpackConfig) => {
      
      // Disable hot reload completely if environment variable is set
      if (config.disableHotReload) {
        // Remove hot reload related plugins
        webpackConfig.plugins = webpackConfig.plugins.filter(plugin => {
          return !(plugin.constructor.name === 'HotModuleReplacementPlugin');
        });
        
        // Disable watch mode
        webpackConfig.watch = false;
        webpackConfig.watchOptions = {
          ignored: /.*/, // Ignore all files
        };
      } else {
        // Add ignored patterns to reduce watched directories
        webpackConfig.watchOptions = {
          ...webpackConfig.watchOptions,
          ignored: [
            '**/node_modules/**',
            '**/.git/**',
            '**/build/**',
            '**/dist/**',
            '**/coverage/**',
            '**/public/**',
          ],
        };
      }
      
      // SOLUTION DÉFINITIVE ELEVATOR BUG: Désactiver complètement le cache
      webpackConfig.cache = false;
      
      // Force un nouveau build complet en ignorant tous les caches
      webpackConfig.optimization = {
        ...webpackConfig.optimization,
        moduleIds: 'named',
        chunkIds: 'named',
      };
      
      // Désactive le cache persistent 
      if (webpackConfig.cache) {
        delete webpackConfig.cache;
      }
      
      return webpackConfig;
    },
  },
};