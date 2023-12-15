const colors = require('tailwindcss/colors');

module.exports = {
  content: [
    './_includes/**/*.html',
    './_layouts/**/*.html',
    './_posts/*.md',
    './*.md',
    './*.html',
  ],
  theme: {
    colors: {
      stone: colors.stone,
      jolly: {
        50: '#fef2f2',
        100: '#fee3e2',
        200: '#fecbca',
        300: '#fca7a5',
        400: '#f97470',
        500: '#f04843',
        600: '#dd2a25',
        700: '#cc231e',
        800: '#9a1e1a',
        900: '#7f201d',
        950: '#450c0a'
      },
      holly: {
        50: '#edfcf4',
        100: '#d4f7e4',
        200: '#aceecd',
        300: '#77deb1',
        400: '#3fc891',
        500: '#1cad77',
        600: '#0f8a5f',
        700: '#0c704f',
        800: '#0c5940',
        900: '#0b4937',
        950: '#05291f'
      },
      snow: {
        50: '#eefcfd',
        100: '#d5f6f8',
        200: '#b0ebf1',
        300: '#79dce7',
        400: '#3cc2d4',
        500: '#20a6ba',
        600: '#1d869d',
        700: '#1e6d80',
        800: '#235e6f',
        900: '#204b59',
        950: '#10313c'
      }
    }
  },
  plugins: []
}