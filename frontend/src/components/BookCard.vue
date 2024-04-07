<template>

  <div class="card-plate">
    <div class="flex mr-2">
      <img @click="showBook" style="height: 350px" class="border-round-xl cursor-pointer" alt="book" :src="book.previewImage"/>
    </div>

    <div class="book-about px-2">
      <h2 @click="showBook" class="book-title">
        <span><i class="pi pi-book"/> {{book.title}}</span>
      </h2>
      <div class="m-2">
        Издательство <i class="pi pi-building mr-2"/>
        <a :href="`/publisher/${book.publisher.id}`" class="text-primary">{{book.publisher.name}}</a>
      </div>
      <div class="m-2 chips">
        <Chip class="m-1 cursor-pointer" v-for="(tag, index) in book.tags" icon="pi pi-tag" :key="index" :label="tag.name" />
      </div>
    </div>
  </div>

</template>

<script lang="ts">
import {defineComponent} from 'vue'
import {Book} from "@/books.ts";

export default defineComponent({
  name: "BookCard",
  props: {
    book: {required: true, type: Book},
  },
  data() {
      return {
        windowWidth: window.innerWidth,
      }
  },
  mounted() {
    window.addEventListener('resize', () => {
      this.windowWidth = window.innerWidth
    })
  },
  computed: {
    isMobile() {
      return this.windowWidth <= 768
    },
  },
  methods: {
    showBook() {
      this.$router.push(`/book/${this.book.id}`)
    },
  }
})
// flex flex-wrap border-1 shadow-2 border-100 border-round-xl justify-content-center align-items-center

</script>

<style scoped>
.card-plate {
  display: -webkit-box!important;
  display: -ms-flexbox!important;
  display: flex!important;
  flex-wrap: wrap!important;
  border-width: 1px!important;
  border-style: solid;
  border-radius: 0.75rem!important;
  -webkit-box-shadow: 0 4px 10px rgba(0,0,0,.03),0 0 2px rgba(0,0,0,.06),0 2px 6px rgba(0,0,0,.12)!important;
  box-shadow: 0 4px 10px rgba(0,0,0,.03),0 0 2px rgba(0,0,0,.06),0 2px 6px rgba(0,0,0,.12)!important;
  border-color: var(--surface-100)!important;
  -webkit-box-align: center!important;
  -ms-flex-align: center!important;
  align-items: center!important;
  -webkit-box-pack: center!important;
  -ms-flex-pack: center!important;
  justify-content: center!important;
}

.chips {
  display: -webkit-box!important;
  display: -ms-flexbox!important;
  display: flex!important;
  flex-wrap: wrap!important;
  -webkit-box-pack: center!important;
  -ms-flex-pack: center!important;
  justify-content: center!important;
}

.book-title {
  cursor: pointer!important;
  margin-bottom: 1rem!important;
  display: -webkit-box!important;
  display: -ms-flexbox!important;
  display: flex!important;
  -webkit-box-pack: center!important;
  -ms-flex-pack: center!important;
  justify-content: center!important;
  text-align: center!important;
}

.book-about {
  max-width: 24rem;
  display: -webkit-box!important;
  display: -ms-flexbox!important;
  display: flex!important;
  -webkit-box-direction: normal!important;
  -ms-flex-direction: column!important;
  flex-direction: column!important;
  -webkit-box-orient: vertical!important;
  -webkit-box-align: center!important;
  -ms-flex-align: center!important;
  align-items: center!important;
}

@media (width < 600px) {
  .card-plate {
    border: none!important;
    padding-bottom: 2rem!important;
    box-shadow: none!important;
  }

  .book-about {
    max-width: none;
  }

}
</style>