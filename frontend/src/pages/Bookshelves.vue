<template>
  <div class="flex items-center mx-auto gap-3 w-full p-2 md:p-6">
    <div class="sm:text-xl border-b-2 p-2"><i class="pi pi-book text-2xl mr-2"/>Книжные полки</div>
    <a href="/bookshelves/create" v-if="loggedIn && user?.isSuperuser">
      <Button icon="pi pi-plus" link outlined size="small" severity="success"/>
    </a>
  </div>

  <div id="search-block" class="flex justify-center p-2">
    <IconField class="max-w-[30rem] w-full" iconPosition="left">
      <InputIcon class="pi pi-search"/>
      <InputText class="w-full" @keydown.enter="getBookshelvesList(1)" v-model="search" placeholder="Поиск"/>
    </IconField>
    <Button icon="pi pi-search" @click="getBookshelvesList(1)"/>
  </div>


  <div class="flex flex-wrap justify-center content-center">
    <template v-if="results && !loadingBooks">
      <BookshelfRow v-for="bs in results?.bookshelves" :bookshelf="bs"/>
    </template>

    <template v-else-if="loadingBooks">
      <!--Заглушка-->
      <Skeleton v-for="i in [1,2]" :key="i" width="100%" height="20rem" class="m-4 rounded-2xl shadow-xl"/>
    </template>

  </div>

  <Paginator v-if="results"
             @page="(event: any) => getBookshelvesList(event.page+1)"
             @update:rows="(value: number) => results!.perPage = value"
             :pages="3"
             v-model="results.currentPage"
             :rows="results.perPage" :totalRecords="results.totalCount" :rowsPerPageOptions="[10, 25, 50]"/>

</template>

<script lang="ts">
import {defineComponent} from 'vue';
import SearchBookForm from "@/components/SearchBookForm.vue";
import bookshelvesService, {PaginatedBookshelvesResult} from "@/services/bookshelves.ts";
import BookshelfRow from "@/components/BookshelfRow.vue";
import {mapState} from "vuex";

export default defineComponent({
  name: "Bookshelves",
  components: {BookshelfRow, SearchBookForm},
  data() {
    return {
      search: this.$route.query.search?.toString() || "",
      windowWidth: window.innerWidth,
      results: null as PaginatedBookshelvesResult | null,
      loadingBooks: false,
    }
  },
  mounted() {
    this.getBookshelvesList(1);
    window.addEventListener('resize', () => this.windowWidth = window.innerWidth);
  },
  computed: {
    ...mapState({
      loggedIn: (state: any) => state.auth.status.loggedIn,
      user: (state: any) => state.auth.user,
    }),
    isMobile() {
      return this.windowWidth <= 768;
    },
  },

  methods: {
    getBookshelvesList(page: number): void {
      this.loadingBooks = true
      bookshelvesService.getBookshelvesList(page, this.search, this.results?.perPage).then(
          (value: PaginatedBookshelvesResult | null) => {
            if (value) this.results = value;
            this.loadingBooks = false;
          }
      ).catch(() => this.loadingBooks = false)
    },

  },

});
</script>
