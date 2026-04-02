import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{html,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        ink: {
          50: '#f8f6f1',
          100: '#efe8dc',
          200: '#e1d3bf',
          300: '#c9b191',
          400: '#ad8a63',
          500: '#8c6641',
          600: '#6d4e33',
          700: '#523b28',
          800: '#38281b',
          900: '#1f1610'
        },
        moss: {
          50: '#eef6ef',
          100: '#d9eadc',
          200: '#b5d4bc',
          300: '#87b793',
          400: '#5f9568',
          500: '#44764d',
          600: '#355d3d',
          700: '#294831',
          800: '#1f3525',
          900: '#132018'
        }
      },
      boxShadow: {
        glow: '0 20px 60px rgba(31, 22, 16, 0.16)'
      },
      fontFamily: {
        body: ['Trebuchet MS', 'Gill Sans', 'Segoe UI', 'sans-serif'],
        display: ['Palatino Linotype', 'Book Antiqua', 'Palatino', 'serif'],
        mono: ['SFMono-Regular', 'Consolas', 'Liberation Mono', 'monospace']
      }
    }
  },
  plugins: []
};

export default config;
