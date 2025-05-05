<template>
  <RecentBooks/>
  <FullSearchBooks @click:book="showBook"/>
</template>

<script lang="ts">
import {defineComponent} from 'vue';

import RecentBooks from "@/components/RecentBooks.vue";
import FullSearchBooks from "@/components/FullSearchBooks.vue";


export default defineComponent({
  name: "Home",
  components: {FullSearchBooks, RecentBooks},
  methods: {
    showBook(bookID: number) {
      document.location.href = `/book/${bookID}`;
    }
  }
})
</script>
