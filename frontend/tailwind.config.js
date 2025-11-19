/** @type {import('tailwindcss').Config} */

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",]
  ,
  theme: {
    extend: {
      fontFamily: {
        title: ["Fredoka", "sans-serif"],
        subtitle: ["Bubblegum Sans", "sans-serif"],
        
      },
      backgroundImage: {
        "lang-bg": "url('./src/assets/background.png')",
        "pink": "#f5224c",
      },
      colors: {
        "pink": "#f5224c",
        "orange": "#fd5600",
        "purple": "#7d42fd"
      }

    },
  },
  plugins: [],
}

