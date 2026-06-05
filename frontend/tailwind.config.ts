import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Brand & Accent
        primary: {
          DEFAULT: "#FCD535",
          active: "#f0b90b",
          disabled: "#3a3a1f",
          foreground: "#181a20",
        },
        accent: {
          turquoise: "#2dbdb6",
        },
        // Surface Dark
        canvas: {
          dark: "#0b0e11",
        },
        "surface-card": {
          dark: "#1e2329",
        },
        "surface-elevated": {
          dark: "#2b3139",
        },
        // Surface Light
        "surface-soft": {
          light: "#fafafa",
        },
        "surface-strong": {
          light: "#f5f5f5",
        },
        // Borders
        hairline: {
          "on-light": "#eaecef",
          "on-dark": "#2b3139",
        },
        "border-strong": "#cdd1d6",
        // Text
        ink: "#181a20",
        body: "#eaecef",
        "body-on-light": "#181a20",
        muted: "#707a8a",
        "muted-strong": "#929aa5",
        "on-dark": "#ffffff",
        // Trading Semantics
        "trading-up": "#0ecb81",
        "trading-down": "#f6465d",
        // Info
        info: "#3b82f6",
        // Terminal Theme
        terminal: {
          bg: "#0c0c0c",
          surface: "#141414",
          border: "#2a2a2a",
          muted: "#5c5c5c",
          text: "#d4d4d4",
          accent: "#f0b429",
          green: "#4ade80",
          red: "#f87171",
          amber: "#fbbf24",
        },
      },
      fontFamily: {
        nova: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        plex: ["JetBrains Mono", "IBM Plex Sans", "monospace"],
        mono: ["JetBrains Mono", "Fira Code", "Consolas", "monospace"],
        display: ["Syne", "sans-serif"],
      },
      borderRadius: {
        xs: "2px",
        sm: "4px",
        md: "6px",
        lg: "8px",
        xl: "12px",
        pill: "9999px",
      },
      boxShadow: {
        "focus-ring": "0 0 0 2px rgba(59, 130, 246, 0.5)",
      },
    },
  },
  plugins: [],
};
export default config;
