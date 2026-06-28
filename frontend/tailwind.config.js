/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // --- Matchnight design system ---
        pitch: "#0a1a14",
        turf: "#102a1e",
        turf2: "#0c2117",
        chalk: "#ecf4ed",
        "chalk-dim": "rgba(236,244,237,0.6)",
        "chalk-faint": "rgba(236,244,237,0.1)",
        line: "rgba(236,244,237,0.14)",
        gold: "#f4c430",
        sky: "#6ec2ff",
        coral: "#ff6b5a",
        // --- Retained legacy tokens still referenced elsewhere ---
        grass: "#16A34A",
        stadium: "#07111F",
        ink: "#17201d",
        sand: "#f6f2e8"
      },
      fontFamily: {
        display: ['"Saira Condensed"', "system-ui", "sans-serif"],
        body: ['"Saira"', "system-ui", "sans-serif"],
        mono: ['"JetBrains Mono"', "ui-monospace", "monospace"]
      },
      boxShadow: {
        broadcast: "0 18px 50px rgba(0, 0, 0, 0.35)",
        gold: "0 0 0 8px rgba(244, 196, 48, 0.12), 0 14px 40px rgba(244, 196, 48, 0.3)"
      }
    }
  },
  plugins: []
};
