document.addEventListener('alpine:init', () => {
  Alpine.data('filterlist', (list) => ({
    userShowAll: false,

    filterText: '',

    filteredList: list,

    filter(val) {
      const searched = val.toLowerCase().trim();
      this.filterText = searched;
      if (searched == '') {
        this.filteredList = this.list;
      } else {
        this.filteredList = this.list.filter(entry =>
          (entry.artist != null && entry.artist.toLowerCase().indexOf(searched) >= 0) ||
          (entry.title != null && entry.title.toLowerCase().indexOf(searched) >= 0)
        );
      }
    },

    clear() {
      this.$refs.search.value = '';
      this.filter('');
    },

    toggle() {
      this.userShowAll = !this.userShowAll;
    },

    get showShowAll() {
      return this.list.length > 5 && this.filterText == '';
    },

    get showAll() {
      return this.userShowAll || this.filterText != '';
    }
  }));
});
