/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: "#111827",
        panel: "#172033",
        line: "#2b3347",
        ink: "#eef2ff",
        muted: "#9ca3af",
        cobalt: "#4f8cff",
        mint: "#42d392",
        amber: "#f6c453"
      }
    }
  },
  plugins: []
};
