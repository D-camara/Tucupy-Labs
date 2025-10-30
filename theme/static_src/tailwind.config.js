export default {
  content: [
    '../templates/**/*.html',      // theme templates
    '../../templates/**/*.html',   // project templates
    '../../**/templates/**/*.html' // any app templates
  ],
  theme: {
    extend: {
      colors: {
        // Tucupi Labs Brand Colors - Verde + Preto
        'tucupi': {
          'black': '#0A0A0A',      // Preto principal
          'dark': '#1A1A1A',       // Preto suave
          'green': {
            50: '#ECFDF5',         // Verde muito claro
            100: '#D1FAE5',        // Verde claro
            200: '#A7F3D0',        
            300: '#6EE7B7',
            400: '#34D399',        // Verde médio
            500: '#10B981',        // Verde principal
            600: '#059669',        // Verde escuro
            700: '#047857',        
            800: '#065F46',        // Verde muito escuro
            900: '#064E3B',
          },
          'accent': '#00FF88',     // Verde neon para destaques
        }
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
        'display': ['Space Grotesk', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.6s ease-out',
        'slide-down': 'slideDown 0.6s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(16, 185, 129, 0.5), 0 0 10px rgba(16, 185, 129, 0.3)' },
          '100%': { boxShadow: '0 0 20px rgba(16, 185, 129, 0.8), 0 0 30px rgba(16, 185, 129, 0.5)' },
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'grid-pattern': 'linear-gradient(to right, rgba(16, 185, 129, 0.1) 1px, transparent 1px), linear-gradient(to bottom, rgba(16, 185, 129, 0.1) 1px, transparent 1px)',
      },
      boxShadow: {
        'glow-green': '0 0 15px rgba(16, 185, 129, 0.5)',
        'glow-green-lg': '0 0 30px rgba(16, 185, 129, 0.6)',
        'inner-glow': 'inset 0 0 20px rgba(16, 185, 129, 0.1)',
      },
    },
  },
}

