import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        spotify: {
          green: "#1DB954",
          "green-light": "#1ed760",
          black: "#000000",
          "dark-base": "#121212",
          "dark-elevated": "#1A1A1A",
          "dark-highlight": "#282828",
          "dark-press": "#000000",
          white: "#FFFFFF",
          "subdued": "#A7A7A7",
          "text": "#B3B3B3",
        },
      },
      fontFamily: {
        sans: ["Circular", "Helvetica Neue", "Helvetica", "Arial", "sans-serif"],
      },
      borderRadius: {
        spotify: "500px",
      },
      animation: {
        "pulse-green": "pulse-green 2s infinite",
        "typing": "typing 1.2s steps(3) infinite",
        "fade-in": "fade-in 0.3s ease-in-out",
        "slide-up": "slide-up 0.3s ease-out",
      },
      keyframes: {
        "pulse-green": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.4" },
        },
        "typing": {
          "0%": { content: '"."' },
          "33%": { content: '".."' },
          "66%": { content: '"..."' },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "slide-up": {
          "0%": { transform: "translateY(10px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
      },
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [],
};

export default config;
