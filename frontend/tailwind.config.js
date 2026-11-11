/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#070C1E',
          900: '#0A1128',
          800: '#001F54',
          700: '#034078',
          600: '#0A4C8A',
        },
        shark: {
          accent: '#006494',
          cyan: '#1282A2',
          light: '#EBF4F6',
        }
      }
    },
  },
  plugins: [],
}
