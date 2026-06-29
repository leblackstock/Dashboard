/** @type {import('tailwindcss').Config} */
const withAlpha = (variable, fallbackOpacity = "1") => {
  return ({ opacityValue }) => {
    return `rgb(var(${variable}) / ${opacityValue ?? fallbackOpacity})`;
  };
};

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: withAlpha("--bg-rgb"),
        surface: withAlpha("--surface-rgb", "0.82"),
        panel: withAlpha("--surface-hover-rgb", "0.9"),
        line: withAlpha("--border-rgb", "0.28"),
        ink: withAlpha("--text-rgb"),
        muted: withAlpha("--text-muted-rgb"),
        cobalt: withAlpha("--accent-primary-rgb"),
        violet: withAlpha("--accent-secondary-rgb"),
        secondary: withAlpha("--accent-secondary-rgb"),
        warm: withAlpha("--accent-warm-rgb"),
        mint: withAlpha("--success-rgb"),
        amber: withAlpha("--warning-rgb"),
        danger: withAlpha("--danger-rgb")
      }
    }
  },
  plugins: []
};
