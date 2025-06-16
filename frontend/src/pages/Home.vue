<template>
  <RecentBooks/>
  <FullSearchBooks @click:book="showBook"/>
</template>

<script lang="ts">
import {defineComponent} from 'vue';

import RecentBooks from "@/components/RecentBooks.vue";
import FullSearchBooks from "@/components/FullSearchBooks.vue";
import {Book} from "@/books.ts";


export default defineComponent({
  name: "Home",
  components: {FullSearchBooks, RecentBooks},
  methods: {
    showBook(book: Book) {
      document.location.href = `/book/${book.id}`;
    }
  }
})
</script>
