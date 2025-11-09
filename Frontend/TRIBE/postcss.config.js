/** @type {import('postcss-load-config').Config} */
module.exports = {
  plugins: {
    "@tailwindcss/postcss": {}, // ✅ Correct plugin reference for Tailwind v4+
    autoprefixer: {},
  },
};
