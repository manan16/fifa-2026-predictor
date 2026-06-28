/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        pitch: "#064E3B",
        grass: "#16A34A",
        stadium: "#07111F",
        line: "#F8FAFC",
        ink: "#17201d",
        sand: "#f6f2e8",
        coral: "#F97316",
        gold: "#FACC15"
      },
      boxShadow: {
        broadcast: "0 18px 50px rgba(6, 78, 59, 0.28)",
        gold: "0 0 32px rgba(250, 204, 21, 0.24)"
      }
    }
  },
  plugins: []
};
