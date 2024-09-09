<template>
  <div v-if="booksID.length" class="p-5 my-4 bookshelf">

    <div v-for="id in booksID" :key="id" class="w-10rem inline-block relative" style="min-height: 300px;">
      <div class="absolute image-block flex flex-row" @mouseover="getBook(id)">
        <img @click="$emit('click:book', id)" :src="`/media/previews/${id}/preview_thumb_medium.png`" class="book-image" alt="book-preview"/>
        <ScrollPanel v-if="currentBook" class="book-detail shadow-1 p-0" style="width: 28.5rem; height: 300px"
                     :pt="{
                              wrapper: {
                                  style: { 'border-right': '10px solid var(--surface-ground)' }
                              },
                              bary: 'hover:bg-primary-400 bg-primary-300 opacity-100'
                          }"
                     :class="isMobile?'absolute':''">
          <BookCard :book="currentBook" :show-image="false" style="background-color: var(--primary-color-text)"/>
        </ScrollPanel>
      </div>
    </div>

  </div>
</template>

<script lang="ts">
import {defineComponent, PropType} from 'vue'
import BookCard from "@/components/BookCard.vue";
import {Book} from "@/books.ts";
import api from "@/services/api.ts";
import {AxiosResponse} from "axios";

export default defineComponent({
  name: "BookshelfImages",
  components: {BookCard},
  props: {
    booksID: {required: true, type: Object as PropType<number[]>},
  },
  emits: ["click:book"],
  data() {
    return {
      bookImages: [] as { id: number, src: string }[],
      viewedBooks: new Map() as Map<number, Book>,
      currentBook: undefined as Book | undefined,
      windowWidth: window.innerWidth,
    }
  },

  mounted() {
    window.addEventListener('resize', () => this.windowWidth = window.innerWidth);
  },

  computed: {
    isMobile() {
      return this.windowWidth <= 768;
    },
  },

  methods: {
    getBook(bookID: number): void {
      this.currentBook = this.viewedBooks.get(bookID)
      if (!this.currentBook) {
        api.get(`/books/${bookID}`).then(
            (value: AxiosResponse<Book>) => {
              this.viewedBooks.set(bookID, value.data);
              this.currentBook = value.data
            }
        ).catch(
            reason => console.log(reason)
        )
      }
    }
  },
})
</script>


<style scoped>

.bookshelf {
  width: 90vw;
  overflow-x: auto;
  white-space: nowrap;
  overflow-y: hidden;
  border: none;
  border-bottom: 10px solid var(--surface-700);
  box-shadow: 1px 1px 5px var(--surface-700);
  border-radius: 10px;
}


.book-image {
  border-radius: .75rem !important;
  max-height: 300px;
  min-height: 300px;
  max-width: 300px;
  margin-top: 5px;
  margin-right: 6px;
  box-shadow: -10px -2px 2px #959595;
  border-left: 1px solid #959595;
  border-bottom: 1px solid #959595;
  cursor: pointer;
  transform: rotate3d(1, 1, 1, -5deg);
}

.book-detail {
  display: none;
}

.image-block:hover, .image-block:active {
  z-index: 999;
}

.image-block:hover .book-detail, .image-block:active .book-detail {
  display: block;
}

.image-block:hover .book-image {
  transform: scale(1.15);
  box-shadow: 0 0 10px #121212;
}


@media (width < 768px) {
  .bookshelf {
    width: 100vw;
    border-radius: 0;
  }

}
</style>