<template>
  <div class="my-2">
    <h2 class="bookshelf-name flex align-items-center">
      <span class="mr-3">{{ bookshelf.name }}</span>
      <Button v-if="user?.id == bookshelf.userId" @click="goToEditBookshelfPage" icon="pi pi-pencil" size="small" outlined severity="warning"/>
      <Button v-if="user?.id == bookshelf.userId" @click="showDeleteDialog=true" icon="pi pi-trash" size="small" outlined severity="danger"/>
    </h2>
    <div class="bookshelf-desc">{{ bookshelf.description }}</div>

    <div class="flex flex-row">
      <BookshelfImages @click:book="showBookPage" :booksID="bookshelf.books" />
    </div>

  </div>


  <Dialog v-model:visible="showDeleteDialog" modal header="Вы уверены, что хотите удалить книжную полку" :style="{ width: '25rem' }">
    <div class="flex justify-content-end gap-2">
      <Button type="button" label="Нет" severity="secondary" @click="showDeleteDialog = false"></Button>
      <Button type="button" label="Удалить" severity="danger" @click="deleteBookshelf"></Button>
    </div>
  </Dialog>

</template>

<script lang="ts">
import {defineComponent, PropType} from 'vue';
import bookshelvesService, {Bookshelf} from "@/services/bookshelves.ts";
import BookCard from "@/components/BookCard.vue";
import BookshelfImages from "@/components/BookshelfImages.vue";
import {mapState} from "vuex";

export default defineComponent({
  name: "BookshelfRow",
  components: {BookshelfImages, BookCard},
  props: {
    bookshelf: {required: true, type: Object as PropType<Bookshelf>},
  },
  data() {
    return {
      showDeleteDialog: false,
    }
  },
  computed: {
    ...mapState({
      loggedIn: (state: any) => state.auth.status.loggedIn,
      user: (state: any) => state.auth.user,
    }),
  },
  methods: {
    showBookPage(bookID: number): void {
      location.href = "/book/" + bookID
    },
    goToEditBookshelfPage() {
      location.href = '/bookshelves/'+this.bookshelf.id+'/edit'
    },
    deleteBookshelf() {
      bookshelvesService.deleteBookshelf(this.bookshelf.id).then(
          () => location.href = '/bookshelves/'
      ).catch(
          () => location.href = '/bookshelves/'
      )
      this.showDeleteDialog = false;
    },
  }

});
</script>

<style scoped>
@media (width < 768px) {
  .bookshelf-name {
    padding: 0 1rem;
  }
  .bookshelf-desc {
    padding: 0 1rem;
  }
}

</style>