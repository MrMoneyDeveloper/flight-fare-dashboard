/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./**/*.{html,js}",     // scan every HTML/JS file in ui/
  ],
  theme: {
    extend: {
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1.25rem' }],
      },
    },
  },
  plugins: [],
};
