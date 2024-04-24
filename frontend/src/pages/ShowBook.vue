<script>
import {defineComponent} from 'vue';
import Vue3PdfApp from "vue3-pdf-app";
import "vue3-pdf-app/dist/icons/main.css";
import api from "@/services/api.ts";
// import "@/assets/pdf-viewer/main.css"

export default defineComponent({
  name: "ShowBook",
  components: {Vue3PdfApp},
  data() {
    return {
      page: 2,
      pdf: null,
    };
  },
  beforeMount() {
    document.title = "Загрузка книги..."
  },
  mounted() {
    api.get(`/books/${this.bookId}`).then(value => document.title = value.data.title)
  },
  computed: {
    bookId() {
      return this.$route.params.id
    }
  },
  methods: {
    async openHandler(pdfApp) {
      this.pdf = pdfApp
      this.page = await pdfApp.pdfDocument.getPage()
    },
  }
})
</script>

<template>
<Vue3PdfApp @pages-rendered="openHandler" style="height: 100vh" :pdf="'/api/v1/books/'+bookId+'/download'" />
</template>

<style scoped>

</style>