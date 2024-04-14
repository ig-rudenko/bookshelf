<template>
  <Menu/>

  <div class="m-2 flex justify-content-center">
    <div v-if="book" class="flex flex-wrap justify-content-center" style="max-width: 1280px">
      <a :href="'/api/v1/books/'+book.id+'/show'" target="_blank" class="flex flex-column">
        <img style="width: 100%" class="border-round-xl" alt="book" :src="book.previewImage"/>
      </a>
      <div class="flex flex-column m-3 w-full" style="max-width: 40rem;">
        <h2 class="p-2">{{book.title}}</h2>
        <div class="m-2">
          <span>Издательство <i class="pi pi-building mr-2"/></span>
          <a :href="`/?publisher=${book.publisher.name}`" class="text-primary">{{book.publisher.name}}</a>
          <span class="ml-2">{{book.year}} г.</span>
        </div>
        <div class="m-2">
          <i class="pi pi-users"/>
          {{book.authors}}
        </div>
        <div class="m-2">
          <i class="pi pi-book"/> {{book.pages}} стр. <i class="pi pi-file mx-2"/>{{formatBytes(book.size)}}
        </div>
        <div class="m-2 chips">
          <Chip class="m-1" style="font-size: 0.9rem;" v-for="(tag, index) in book.tags" icon="pi pi-tag" :key="index" :label="tag.name" />
        </div>
        <div class="p-3" v-html="book.description" ></div>
      </div>
    </div>
  </div>

  <div v-if="book?.id && canCreateComment" class="flex justify-content-center">
    <CreateComment @created="getComments" :book-id="book.id"/>
  </div>

  <div class="flex flex-wrap flex-column align-items-center" v-if="results">
    <Comment @comment:delete="getComments(1)" @comment:update="getComments(1)" v-for="(comment, index) in results.comments" :key="index" :comment="comment" />
    <Paginator class="w-full" v-if="results"
               :always-show="false"
               @page="(event: any) => getComments(event.page+1)"
               @update:rows="(value: number) => results!.perPage = value"
               v-model="results.currentPage"
               :rows="results.perPage" :totalRecords="results.totalCount" :rowsPerPageOptions="[10, 25, 50]" />
  </div>

</template>

<script lang="ts">
import {defineComponent} from 'vue'
import Menu from "@/components/Menu.vue";
import {Book} from "@/books.ts";
import api from "@/services/api.ts";
import {AxiosResponse} from "axios";
import {formatBytes} from "../formatter.ts";
import CreateComment from "@/components/CreateComment.vue";
import {mapState} from "vuex";
import Comment from "@/components/Comment.vue";
import {CommentResult} from "@/comment"

export default defineComponent({
  name: "BookPage",
  components: {Comment, CreateComment, Menu,},
  data() {
      return {
        book: null as Book|null,
        results: null as CommentResult|null,
      }
  },
  mounted() {
      this.getBook();
      this.getComments(1);
  },
  computed: {
    ...mapState({
      loggedIn: (state: any) => state.auth.status.loggedIn,
      user: (state: any) => state.auth.user,
    }),
    canCreateComment() {
      return this.loggedIn && this.user?.isStaff;
    },
    bookIdParam() {
      return this.$route.params.id
    }
  },
  methods: {
    formatBytes,
    getBook() {
      if (this.book) return;
      api.get(`/books/${this.bookIdParam}`)
          .then(
              (value: AxiosResponse<Book>) => {
                this.book = value.data;
                document.title = this.book.title;
              }
          )
    },
    getComments(page: number) {
      let url = `/comments/book/${this.bookIdParam}?page=${page}`
      if (this.results) url += `&per-page=${this.results.perPage}`
      api.get(url).then(
              (value: AxiosResponse<CommentResult>) => this.results = value.data
          )
    }
  }
})
</script>

<style scoped>

</style>