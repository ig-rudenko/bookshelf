<template>
  <div class="my-2">
    <div class="flex items-center">
      <div :id="'bookshelf-name-'+bookshelf.id" class="flex items-center text-xl pl-5">
        {{ bookshelf.name }}
      </div>

      <div class="flex items-center relative">
        <Button icon="pi pi-share-alt" size="small" @click="copyClipboard" outlined text/>
        <Badge v-if="copyClipboardText" class="text-xs absolute" style="top: -25px">{{ copyClipboardText }}</Badge>
      </div>

      <div v-if="user?.id == bookshelf.userId">
        <Button @click="goToEditBookshelfPage" icon="pi pi-pencil" size="small" rounded
                outlined severity="warning"/>
        <Button @click="showDeleteDialog=true" icon="pi pi-trash" size="small" rounded
                outlined severity="danger"/>
      </div>
    </div>

    <div class="pl-5">{{ bookshelf.description }}</div>

    <div :id="'bookshelf-'+bookshelf.id">
      <BookshelfImages @maximize="processMaximizeChange" @click:book="showBookPage" :books="bookshelf.books"/>
    </div>

  </div>

  <Dialog v-model:visible="showDeleteDialog" modal header="Вы уверены, что хотите удалить книжную полку"
          :style="{ width: '25rem' }">
    <div class="flex justify-end gap-2">
      <Button type="button" label="Нет" autofocus severity="secondary" @click="showDeleteDialog = false"></Button>
      <Button type="button" label="Удалить" severity="danger" @click="deleteBookshelf"></Button>
    </div>
  </Dialog>

</template>

<script lang="ts">
import {defineComponent, PropType} from 'vue';
import bookshelvesService, {Bookshelf} from "@/services/bookshelves.ts";
import BookshelfImages from "@/components/BookshelfImages.vue";
import {mapState} from "vuex";
import {Book} from "@/books.ts";

export default defineComponent({
  name: "BookshelfRow",
  components: {BookshelfImages},
  props: {
    bookshelf: {required: true, type: Object as PropType<Bookshelf>},
  },
  data() {
    return {
      showDeleteDialog: false,
      copyClipboardText: "",
    }
  },
  computed: {
    ...mapState({
      loggedIn: (state: any) => state.auth.status.loggedIn,
      user: (state: any) => state.auth.user,
    }),
  },
  methods: {
    showBookPage(book: Book): void {
      location.href = '/book/' + book.id
    },
    goToEditBookshelfPage() {
      location.href = '/bookshelves/' + this.bookshelf.id + '/edit'
    },
    deleteBookshelf() {
      bookshelvesService.deleteBookshelf(this.bookshelf.id).then(
          () => location.href = '/bookshelves/'
      ).catch(
          () => location.href = '/bookshelves/'
      )
      this.showDeleteDialog = false;
    },

    processMaximizeChange(status: string) {
      location.hash = "";
      if (status) {
        location.hash = 'bookshelf-' + this.bookshelf.id;
      } else {
        location.hash = 'bookshelf-name-' + this.bookshelf.id;
      }
    },

    copyClipboard() {
      navigator.clipboard.writeText(location.origin + "/bookshelves?search=" + this.bookshelf.name)
          .then(
              () => this.copyClipboardText = 'Скопировано!'
          ).catch(
          () => this.copyClipboardText = 'Не удалось скопировать!'
      )
      setTimeout(() => this.copyClipboardText = "", 700);
    }
  }

});
</script>
