module.exports = {
  webpack: {
    configure: (webpackConfig, { env }) => {
      // Désactiver complètement le cache pour éviter les problèmes de corruption
      webpackConfig.cache = false;
      
      return webpackConfig;
    },
  },
};