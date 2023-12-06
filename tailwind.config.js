module.exports = {
  content: [
    './_includes/**/*.html',
    './_layouts/**/*.html',
    './_posts/*.md',
    './*.md',
    './*.html',
  ],
  theme: {
    theme: {
      extend: {
        gridTemplateRows: {
          '9': '200px minmax(900px, 1fr) 100px',
        }
      },
    },
  },
  plugins: []
}