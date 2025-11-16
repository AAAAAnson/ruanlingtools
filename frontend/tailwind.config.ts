import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#FF6B6B',
        secondary: '#4ECDC4',
        accent: '#FFE66D',
        success: '#51CF66',
        danger: '#FF6B6B',
        dark: '#1A1A2E',
      },
      fontFamily: {
        pixel: ['"Press Start 2P"', 'monospace'],
        body: ['"Roboto"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
export default config
