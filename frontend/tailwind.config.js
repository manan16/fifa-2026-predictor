/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        pitch: "#0f6b4b",
        ink: "#17201d",
        sand: "#f6f2e8",
        coral: "#d45b4c",
        gold: "#d7a642"
      }
    }
  },
  plugins: []
};

