<template>
  <div class="align-center flex flex-col flex-wrap justify-center items-center mx-auto p-2 w-full">
    <div class="text-center text-3xl px-2 py-5 w-full">{{ actionVerbosePrefix }} книжной полки</div>

    <Message class="mb-3" v-if="formError" @click="formError=''">{{ formError }}</Message>

    <div v-if="formIsValid" class="flex justify-center">
      <Button @click="editBookshelfID?updateBookshelf():createBookshelf()" :label="editBookshelfID?'Обновить':'Создать'"
              severity="success" icon="pi pi-check"/>
    </div>

    <div class="flex flex-col justify-center max-w-5xl w-full">
      <div>
        <div class="flex flex-col gap-2 pb-2">
          <label for="book.title">Название книжной полки</label>
          <InputText id="book.title" class="w-full" v-model="form.name"/>
        </div>

        <div class="flex flex-col gap-2 pb-2">
          <label for="book.description">Описание</label>
          <Textarea id="book.description" v-model="form.description" auto-resize rows="3"/>
        </div>
      </div>

    </div>
  </div>

  <div class="relative mx-auto" v-if="form.books.length">
    <BookshelfImages :booksID="form.books" @click:book="bookID => removeElement(form.books, bookID)"/>
  </div>

  <div>
    <FullSearchBooks @click:book="bookID => addElement(form.books, bookID)" :initial-per-page="10"
                     :auth-scroll-to-search-block="false"
                     :initial-compact-view="true"/>
  </div>

</template>

<script lang="ts">
import {defineComponent} from 'vue';
import {mapState} from "vuex";
import bookshelvesService, {EditBookshelf} from "@/services/bookshelves.ts";
import SearchBookForm from "@/components/SearchBookForm.vue";
import {FilterBook} from "@/filters.ts";
import bookService from "@/services/books.ts";
import {PaginatedBookResult} from "@/books.ts";
import FullSearchBooks from "@/components/FullSearchBooks.vue";
import BookshelfRow from "@/components/BookshelfRow.vue";
import BookshelfImages from "@/components/BookshelfImages.vue";
import {AxiosError} from "axios";
import getVerboseAxiosError from "@/errorFmt.ts";

export default defineComponent({
  name: "CreateBookshelf",
  components: {BookshelfImages, BookshelfRow, FullSearchBooks, SearchBookForm},
  data() {
    return {
      windowWidth: window.innerWidth,
      filters: new FilterBook(),
      results: null as PaginatedBookResult | null,
      loadingBooks: false,
      editBookshelfID: this.$route.params.id as string | undefined,
      form: {
        name: "",
        description: "",
        books: []
      } as EditBookshelf,
      formError: "",
    }
  },
  mounted() {
    if (!this.loggedIn || !this.user) this.$router.push("/login");
    this.getBookshelfToEdit();
    document.title = this.actionVerbosePrefix;
    window.addEventListener('resize', () => this.windowWidth = window.innerWidth);
  },

  computed: {
    ...mapState({
      loggedIn: (state: any) => state.auth.status.loggedIn,
      user: (state: any) => state.auth.user,
    }),
    isMobile() {
      return this.windowWidth <= 1024;
    },

    formIsValid() {
      return this.form.name.length > 3 && this.form.books.length > 0
    },

    actionVerbosePrefix() {
      return this.editBookshelfID ? 'Обновление' : 'Создание'
    }
  },

  methods: {
    getBookshelfToEdit() {
      if (this.editBookshelfID && this.user) {
        bookshelvesService.getBookshelf(this.editBookshelfID).then(
            data => {
              if (data.userId !== this.user.id) {
                this.formError = "У вас нет прав радактировать данную книжную полку"
              } else {
                this.form = data;
              }
            }
        ).catch(
            (reason: AxiosError<any>) => {
              this.formError = getVerboseAxiosError(reason);
            }
        );
      }
    },

    createBookshelf() {
      this.formError = ''
      bookshelvesService.createBookshelf(this.form)
          .then(data => location.href = "/bookshelves?search=" + data.name)
          .catch(
              (reason: AxiosError<any>) => {
                this.formError = getVerboseAxiosError(reason)
              }
          );
    },

    updateBookshelf() {
      this.formError = ''
      if (!this.editBookshelfID) {
        this.formError = 'Не найдет ID для обновления книжной полки'
        return
      }
      bookshelvesService.updateBookshelf(this.editBookshelfID, this.form)
          .then(data => location.href = "/bookshelves?search=" + data.name)
          .catch(
              (reason: AxiosError<any>) => {
                this.formError = getVerboseAxiosError(reason)
              }
          );
    },

    getBooksList(page: number, filter: null | FilterBook = null) {
      this.loadingBooks = true
      location.hash = "#search-block";
      bookService.getBooksList(page, filter, this.results?.perPage).then(
          (value: PaginatedBookResult | null) => {
            if (value) this.results = this.replaceThumb(value);
            this.loadingBooks = false;
          }
      ).catch(() => {
        this.loadingBooks = false
      })
    },

    replaceThumb(data: PaginatedBookResult): PaginatedBookResult {
      if (this.isMobile) {
        for (const book of data.books) {
          book.previewImage = book.previewImage.replace("medium.png", "small.png")
        }
      }
      return data
    },

    addElement<T>(array: T[], element: T) {
      const index = array.indexOf(element)
      if (index == -1) array.push(element)
    },

    removeElement<T>(array: T[], element: T) {
      const index = array.indexOf(element)
      if (index > -1) array.splice(index, 1)
    }

  }
})
</script>
