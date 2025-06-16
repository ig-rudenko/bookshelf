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
        <div for="bookshelf.private" class="flex justify-end items-center gap-2 pb-2 cursor-pointer select-none">
          <div v-if="user.isSuperuser">
            <Button @click="form.private=!form.private" v-if="form.private" label="Приватная книжная полка"
                    icon="pi pi-lock" severity="secondary"/>
            <Button @click="form.private=!form.private" v-else label="Публичная книжная полка" icon="pi pi-lock-open"
                    severity="primary"/>
          </div>
          <div v-else v-tooltip.left="'Недоступно для редактирования'">
            <Button
                label="Приватная книжная полка"
                icon="pi pi-lock" severity="secondary"/>
          </div>
        </div>

        <div class="flex flex-col gap-2 pb-2">
          <label for="bookshelf.title">Название книжной полки</label>
          <InputText id="bookshelf.title" class="w-full" v-model="form.name"/>
        </div>

        <div class="flex flex-col gap-2 pb-2">
          <label for="bookshelf.description">Описание</label>
          <Textarea id="bookshelf.description" v-model="form.description" auto-resize rows="3"/>
        </div>
      </div>

    </div>
  </div>

  <div class="relative mx-auto" v-if="form.books.length">
    <BookshelfImages :books="form.books" @click:book="book => removeBookByID(book.id)"/>
  </div>

  <div>
    <FullSearchBooks @click:book="book => addElement(form.books, {id: book.id, preview: book.previewImage})"
                     :initial-per-page="10"
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
        private: true,
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
                console.log(data.books.map(b => b.id))
                this.form = data;
                console.log(this.form)
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

    removeBookByID(book_id: number) {
      this.form.books.splice(this.form.books.findIndex(b => b.id === book_id), 1)
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
