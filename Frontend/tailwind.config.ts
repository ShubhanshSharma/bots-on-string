import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./TRIBE/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./TRIBE/components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};

export default config;
