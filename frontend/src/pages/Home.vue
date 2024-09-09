<template>
  <Menu/>

  <div class="mt-4">
    <RecentBooks/>
  </div>

  <FullSearchBooks @click:book="showBook" />
  <Footer/>

</template>

<script lang="ts">
import {defineComponent} from 'vue';

import Menu from "@/components/Menu.vue";
import Footer from "@/components/Footer.vue";

import RecentBooks from "@/components/RecentBooks.vue";
import FullSearchBooks from "@/components/FullSearchBooks.vue";


export default defineComponent({
  name: "Home",
  components: {FullSearchBooks, RecentBooks, Footer, Menu},
  methods: {
    showBook(bookID: number) {
      document.location.href = `/book/${bookID}`;
    }
  }
})
</script>

<style scoped>

</style>