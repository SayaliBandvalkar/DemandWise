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
          950: '#040B14',
          900: '#07101E',
          800: '#0A192F',
          700: '#0F2744',
          600: '#17375E',
          500: '#204A7D',
        },
        cyan: {
          DEFAULT: '#00E5FF',
          accent: '#00B4D8',
          glow: 'rgba(0, 229, 255, 0.25)',
        },
      },
    },
  },
  plugins: [],
}
