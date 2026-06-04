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
        mono: ["JetBrains Mono", "Fira Code", "Consolas", "monospace"],
        display: ["Syne", "sans-serif"],
      },
    },
  },
  plugins: [],
};
export default config;
