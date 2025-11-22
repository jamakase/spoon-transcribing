import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        slate: {
          850: '#151f32', // Custom intermediate shade
          950: '#020617',
        },
        'neon-yellow': '#ccff00',
      },
      fontFamily: {
        sans: ['var(--font-dm-sans)', 'sans-serif'],
        display: ['var(--font-unbounded)', 'sans-serif'],
        mono: ['monospace'], // Simple fallback for now or add a google font if needed
      },
      borderRadius: {
        none: '0',
        sm: '1px',
        DEFAULT: '2px',
        md: '4px',
        lg: '6px',
        xl: '8px',
      },
      boxShadow: {
        'hard': '4px 4px 0px 0px #000000',
        'hard-sm': '2px 2px 0px 0px #000000',
        'glow': '0 0 15px rgba(204, 255, 0, 0.3)',
      },
      backgroundImage: {
        'grid-pattern': "linear-gradient(to right, #1e293b 1px, transparent 1px), linear-gradient(to bottom, #1e293b 1px, transparent 1px)",
      }
    },
  },
  plugins: [],
};
export default config;
