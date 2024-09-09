<template>
  <div class="my-2">
    <h2 class="bookshelf-name flex align-items-center">
      <span class="mr-3">{{ bookshelf.name }}</span>
      <Button v-if="user?.id == bookshelf.userId" @click="$router.push('/bookshelves/'+bookshelf.id+'/edit')" icon="pi pi-pencil" size="small" outlined severity="warning"/>
    </h2>
    <div class="bookshelf-desc">{{ bookshelf.description }}</div>

    <div class="flex flex-row">
      <BookshelfImages @click:book="showBookPage" :booksID="bookshelf.books" />
    </div>

  </div>
</template>

<script lang="ts">
import {defineComponent, PropType} from 'vue';
import {Bookshelf} from "@/services/bookshelves.ts";
import BookCard from "@/components/BookCard.vue";
import BookshelfImages from "@/components/BookshelfImages.vue";
import {mapState} from "vuex";

export default defineComponent({
  name: "BookshelfRow",
  components: {BookshelfImages, BookCard},
  props: {
    bookshelf: {required: true, type: Object as PropType<Bookshelf>},
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
    }
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