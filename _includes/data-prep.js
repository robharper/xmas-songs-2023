const pageData = {{ page.data | jsonify }};
window.pageData = pageData;

pageData.today.forEach((s, idx) => {
  s.simpleRank = idx + 1;
});
pageData.artist.forEach((s, idx) => {
  s.simpleRank = idx + 1;
});

pageData.today_version.forEach((song, idx) => {
  const todaySong = pageData.today.find(s => s.song_id === song.song_id);
  if (todaySong) {
    song.comparisonNumber = `${Math.round(song.plays / todaySong.plays * 100)}%`;
  } else {
    song.comparisonNumber = `New!`;
  }
  song.simpleRank = idx + 1;
});
