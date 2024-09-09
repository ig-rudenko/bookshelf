<template>
  <Menu/>

  <div class="flex justify-content-center">
    <div class="flex align-items-center gap-3" style="width: 90vw;">
      <h1 class="border-bottom-3 w-fit p-2"><i class="pi pi-book text-2xl mr-2"/>Книжные полки</h1>
      <div v-if="loggedIn && user?.isSuperuser"><Button icon="pi pi-plus" outlined severity="success" label="Создать" /></div>
    </div>
  </div>

  <div id="search-block" class="flex justify-content-center p-2">
    <IconField class="max-w-30rem w-full" iconPosition="left">
      <InputIcon class="pi pi-search"/>
      <InputText class="w-full" v-model="search" placeholder="Поиск"/>
    </IconField>
    <Button icon="pi pi-search" @click="getBookshelvesList(1)"/>
  </div>


  <div class="flex flex-wrap justify-content-center align-content-center">
    <template v-if="results && !loadingBooks">
      <BookshelfRow v-for="bs in results?.bookshelves" :bookshelf="bs"/>
    </template>

    <template v-else-if="loadingBooks">
      <!--Заглушка-->
      <Skeleton v-for="i in [1,2]" :key="i" width="100%" height="20rem" class="m-4 border-round-2xl shadow-2"/>
    </template>

  </div>

  <Paginator v-if="results"
             @page="(event: any) => getBookshelvesList(event.page+1)"
             @update:rows="(value: number) => results!.perPage = value"
             :pages="3"
             v-model="results.currentPage"
             :rows="results.perPage" :totalRecords="results.totalCount" :rowsPerPageOptions="[10, 25, 50]"/>

  <Footer/>

</template>

<script lang="ts">
import {defineComponent} from 'vue';
import Footer from "@/components/Footer.vue";
import Menu from '@/components/Menu.vue';
import SearchBookForm from "@/components/SearchBookForm.vue";
import bookshelvesService, {PaginatedBookshelvesResult} from "@/services/bookshelves.ts";
import BookshelfRow from "@/components/BookshelfRow.vue";
import BookCard from "@/components/BookCard.vue";
import {mapState} from "vuex";

export default defineComponent({
  name: "Bookshelves",
  components: {BookCard, BookshelfRow, SearchBookForm, Footer, Menu},
  data() {
    return {
      search: "",
      compactView: false,
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
            this.results = value;
            this.loadingBooks = false;
          }
      ).catch(() => {
        this.loadingBooks = false
      })
    },

  },

});
</script>

<style scoped>

</style>