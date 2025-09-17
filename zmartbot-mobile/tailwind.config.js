/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,jsx,ts,tsx}", "./src/**/*.{js,jsx,ts,tsx}"],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        // Binance Dark Theme Colors
        'binance': {
          'bg-primary': '#0B0E11',      // Deep black background
          'bg-secondary': '#1E2026',    // Dark gray secondary background
          'bg-tertiary': '#2B2F36',     // Lighter dark gray for cards
          'bg-elevated': '#363A45',     // Elevated card background
          'text-primary': '#EAECEF',    // High contrast white text
          'text-secondary': '#B7BDC6',  // Secondary text
          'text-tertiary': '#848E9C',   // Tertiary text
          'border': '#2A2D35',          // Border color
          'border-light': '#363A45',    // Lighter border
          'success': '#0ECB81',         // Green for positive
          'danger': '#F6465D',          // Red for negative
          'warning': '#F0B90B',         // Yellow for warnings
          'info': '#0ECB81',            // Blue for neutral actions
          'accent': '#F0B90B',          // Accent color
        },
        // Legacy colors for backward compatibility
        primary: "#0EA5E9",
        secondary: "#64748B", 
        success: "#10B981",
        warning: "#F59E0B",
        danger: "#EF4444",
        dark: "#1E293B",
        light: "#F8FAFC"
      },
      fontFamily: {
        'mono': ['SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', 'monospace'],
      },
      animation: {
        'slide-in-left': 'slideInLeft 0.6s ease-out',
        'slide-in-right': 'slideInRight 0.6s ease-out',
        'fade-in': 'fadeIn 0.5s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
      },
      keyframes: {
        slideInLeft: {
          '0%': { transform: 'translateX(-100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideInRight: {
          '0%': { transform: 'translateX(100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}

