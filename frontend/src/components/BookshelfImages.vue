<template>

  <div class="sticky text-right z-5">
    <Button v-if="maximize" @click="() => changeMaximize(false)" v-tooltip.left="'Свернуть'" class="!absolute"
            icon="pi pi-angle-double-up" style="right: 10px; top: 10px"/>
    <Button v-else @click="() => changeMaximize(true)" v-tooltip.left="'Развернуть'" class="!absolute"
            icon="pi pi-angle-double-down" style="right: 10px; top: 10px"/>
  </div>

  <!--Подсказка-->
  <div class="sticky z-1">
    <div v-if="!isMobile && maximize" class="absolute flex items-center left-0 p-4 text-400 text-xs top-0">
      <span class="pr-1">Листайте вправо с зажатым</span>
      <Button outlined style="padding: 2px; font-size: 12px">Shift</Button>
    </div>
  </div>

  <div v-if="books.length" class="p-5 my-4 bookshelf relative" :style="bookshelfStyle">

    <!--Обложки книг-->
    <div v-for="book in books" :key="book.id" class="inline-block relative book-block" :style="bookBlockStyle">
      <div class="absolute image-block flex flex-row" @mouseover="getBook(book.id)">
        <!--Картинка книги-->
        <div>
          <img @click="$emit('click:book', book)"
               :src="book.preview"
               class="book-image" :style="bookImageStyle" alt="book-preview"/>
        </div>

        <!--Описание книги-->
        <div v-if="currentBook" class="book-detail scale-[0.92]" :class="isMobile?'absolute':''">
          <BookCard :book="currentBook" :show-image="false"
                    class="bg-white dark:bg-surface-800 !shadow-none !max-w-[25rem] text-wrap"/>
        </div>
      </div>
    </div>

  </div>
</template>

<script lang="ts">
import {defineComponent, PropType} from 'vue'
import BookCard from "@/components/BookCard.vue";
import {Book} from "@/books.ts";
import api from "@/services/api";
import {AxiosResponse} from "axios";

export default defineComponent({
  name: "BookshelfImages",
  components: {BookCard},
  props: {
    books: {required: true, type: Object as PropType<{ id: number, preview: string }[]>},
  },
  emits: ["click:book", "maximize"],
  data() {
    return {
      bookImages: [] as { id: number, src: string }[],
      viewedBooks: new Map() as Map<number, Book>,
      currentBook: undefined as Book | undefined,
      windowWidth: window.innerWidth,
      maximize: false,
    }
  },

  mounted() {
    window.addEventListener('resize', () => this.windowWidth = window.innerWidth);
  },

  computed: {
    isMobile() {
      return this.windowWidth <= 768;
    },

    bookBlockStyle() {
      if (this.maximize) {
        return {
          padding: "1rem",
          width: "10rem !important",
          margin: "1rem !important",
        }
      }
      return {}
    },

    bookshelfStyle() {
      if (this.maximize) {
        return {
          "white-space": "pre-wrap !important",
          padding: "3rem !important",
        }
      }
      return {}
    },

    bookImageStyle() {
      if (this.maximize) {
        return {
          transform: "rotate3d(1, 1, 1, -1deg)"
        }
      }
      return {}
    }

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
    },

    changeMaximize(status: boolean) {
      this.maximize = status;
      this.$emit("maximize", this.maximize);
    }

  },
})
</script>


<style scoped>

.bookshelf {
  width: 90vw;
  overflow-x: auto;
  white-space: nowrap;
  overflow-y: auto;
  border: none;
  border-bottom: 5px solid var(--p-surface-700);
  box-shadow: 1px 1px 4px var(--p-surface-700);
  border-radius: 10px;
}

.book-block {
  min-height: 230px;
  width: 9rem !important;
}


.book-image {
  border-radius: .75rem !important;
  max-height: 230px;
  min-height: 230px;
  max-width: 250px;
  margin-top: 5px;
  box-shadow: -6px -2px 2px #959595;
  border-left: 1px solid #959595;
  border-bottom: 1px solid #959595;
  cursor: pointer;
}

/* При наведении на обложку поднимаем её на передний план */
.image-block:hover, .image-block:active {
  z-index: 2;
}

/* Увеличение книги при наведении на обложку */
.image-block:hover .book-image {
  transform: scale(1.15) !important;
  box-shadow: 0 0 5px #121212;
}


/* По умолчанию описание книги скрыто */
.book-detail {
  display: none;
}

/* При наведении на обложку показывает описание книги */
.image-block:hover .book-detail, .image-block:active .book-detail {
  display: block;
}


@media (width < 768px) {
  .bookshelf {
    width: 100vw;
    border-radius: 0;
  }

}
</style>
