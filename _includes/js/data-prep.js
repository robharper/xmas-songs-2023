const pageData = {{ page.data | jsonify }};
window.pageData = pageData;

pageData.artist.forEach((s, idx) => {
  s.simpleRank = idx + 1;
});

pageData.today_version.forEach((s, idx) => {
  s.simpleRank = idx + 1;
});
