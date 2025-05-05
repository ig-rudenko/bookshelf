<script lang="ts">
import {defineComponent, PropType} from 'vue'

import api from "@/services/api";
import {BookDetail} from "@/books.ts";
import TimeAgo from "javascript-time-ago";
import ru from "javascript-time-ago/locale/ru";
import {getReadPagesCountColor} from "@/formatter.ts";

interface BookHistory {
  id: number;
  pdfHistoryUpdatedAt: string;
  pdfHistory: string
}

export default defineComponent({
  name: "BookViewStats",
  props: {
    book: {required: true, type: Object as PropType<BookDetail>},
  },
  data() {
    return {
      bookHistory: null as any | null,
      pdfHistoryUpdatedAt: null as Date | null,
    }
  },
  mounted() {
    TimeAgo.addDefaultLocale(ru)
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
      return this.currentPage / this.book.pages * 100
    },
    verboseValue() {
      const timeAgo = new TimeAgo('ru-RU');
      const lastRead = this.pdfHistoryUpdatedAt ? timeAgo.format(this.pdfHistoryUpdatedAt) : "";
      return `Прочитано страниц: ${this.currentPage}/${this.book.pages} | ${lastRead}`;
    }
  },
  methods: {
    getReadPagesCountColor,
    getBookHistory() {
      api.get<BookHistory>(`/user-data/book/${this.book.id}/pdf-history`).then(
          res => {
            if (res.status == 200) {
              this.bookHistory = JSON.parse(res.data.pdfHistory);
              this.pdfHistoryUpdatedAt = new Date(res.data.pdfHistoryUpdatedAt)
            }
          },
      )
    }
  }
})
</script>

<template>
  <div v-if="currentPage" class="p-2 pb-4">
    <MeterGroup :value="[{label: verboseValue, value: percents, color: getReadPagesCountColor(percents), icon: '' }]"/>
  </div>
</template>
