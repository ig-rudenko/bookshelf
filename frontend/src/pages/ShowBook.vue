<script>
import {defineComponent} from 'vue';
import Vue3PdfApp from "vue3-pdf-app";
import "vue3-pdf-app/dist/icons/main.css";

import api from "@/services/api.ts";
import {PdfHistory} from "@/services/userData.ts";
import {mapState} from "vuex";
import {useRoute} from "vue-router";

export default defineComponent({
  name: "ShowBook",
  components: {Vue3PdfApp},
  data() {
    return {
      pdf: null,
      pdfHistoryService: null,
      loadHistory: false,
    };
  },
  async beforeMount() {
    document.title = "Загрузка книги...";
    if (this.loggedIn) {
      this.pdfHistoryService = new PdfHistory(this.bookId);
      await this.pdfHistoryService.getFromRemote();
    }
    this.loadHistory = true;
  },
  mounted() {
    api.get(`/books/${this.bookId}`).then(value => document.title = value.data.title)
  },

  computed: {
    ...mapState({
      loggedIn: (state) => state.auth.status.loggedIn,
    }),
    route() {return useRoute()},
    bookId() {
      return this.route.params.id
    }
  },
  methods: {
    checkLocalChanges() {
      this.pdfHistoryService.checkLocalChanges()
      setTimeout(this.checkLocalChanges, 1000);
    },
    async openHandler(pdfApp) {
      this.pdf = pdfApp
      // this.page = await pdfApp.pdfDocument.getPage()
      if (this.loggedIn) {
        this.checkLocalChanges()
      }
    },
  }
})
</script>

<template>
<Vue3PdfApp v-if="loadHistory" @pages-rendered="openHandler" style="height: 100vh" :pdf="'/api/v1/books/'+bookId+'/download'" />
</template>

<style scoped>

</style>