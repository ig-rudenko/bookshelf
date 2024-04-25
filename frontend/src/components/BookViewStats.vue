<script lang="ts">
import {defineComponent, PropType} from 'vue'
import {AxiosResponse} from "axios";

import api from "@/services/api";
import {BookDetail} from "@/books.ts";

export default defineComponent({
  name: "BookViewStats",
  props: {
    book: {required: true, type: Object as PropType<BookDetail>},
  },
  data() {
      return {
        bookHistory: null as any|null,
      }
  },
  mounted() {
      this.getBookHistory();
  },
  computed: {
    currentPage() {
      if (this.bookHistory) {
        if (this.bookHistory.files?.length > 0) {
          return this.bookHistory.files[0].page;
        }
      }
      return 0;
    },
    percents() {
      return this.currentPage/this.book.pages*100
    },
    verboseValue() {
      return `Прочитано страниц: ${this.currentPage}/${this.book.pages}`;
    }
  },
  methods: {
    getBookHistory() {
      api.get(`/user-data/book/${this.book.id}/pdf-history`).then(
          (res: AxiosResponse<{pdfHistory: string}>) => {
            if (res.status == 200) this.bookHistory = JSON.parse(res.data.pdfHistory);
          },
      )
    }
  }
})
</script>

<template>
  <MeterGroup v-if="currentPage" :value="[{label: verboseValue, value: percents, color: 'primary', icon: '' }]"/>
</template>

<style scoped>

</style>