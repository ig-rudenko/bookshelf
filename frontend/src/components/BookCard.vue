<template>

  <div class="card-plate" :style="cardStyle">
    <div class="flex">
      <img @click="showBook" :src="book.previewImage" class="book-image cursor-pointer" alt="book"/>
    </div>

    <div class="book-about px-2" v-if="!compactView" style="font-size: 0.83rem;">
      <h2 class="book-title">
        <a class="no-underline text-900" :href="'/book/'+book.id">{{book.title}}</a>
      </h2>
      <div class="align-items-end flex m-2" :style="{'font-size': isMobile?'0.7rem':'1rem'}">
        <span v-if="!isMobile" class="mr-2">Издательство</span><i class="pi pi-building mr-2"/>
        <span @click="$emit('select:publisher', book.publisher.name)" class="text-primary cursor-pointer">{{book.publisher.name}}</span>
        <span class="ml-2">{{book.year}} г.</span>
      </div>

      <div class="flex align-items-center" :style="{'flex-direction': isMobile?'row':'column'}">

        <div v-if="isMobile" class="chips">
          <i class="pi pi-tag" @click="toggleTagsOverlay"/>
          <OverlayPanel ref="tags">
            <Chip v-for="(tag, index) in book.tags" :key="index" :label="tag.name" @click="selectTag(tag)" class="m-1 cursor-pointer" style="font-size: 0.7rem;" icon="pi pi-tag" />
          </OverlayPanel>
        </div>

        <div class="m-2 flex flex-row align-items-center">
          <span v-if="!isMobile" class="mr-2">Язык книги: {{book.language}}</span>
          <img :alt="book.language" :src="`https://flagcdn.com/${getLanguagePairByLabel(book.language).code}.svg`" class="border-1 border-500" style="width: 24px" />
        </div>

      </div>

      <div v-if="!isMobile" class="flex flex-column align-items-center">

        <div class="m-2 text-center flex flex-row align-items-center">
          <i class="pi pi-users mr-2"/>
          <span>{{book.authors}}</span>
        </div>

        <div class="m-2 text-center">
          <i class="pi pi-book mx-2"/>{{book.pages}} стр. <i class="pi pi-file mx-2"/>{{formatBytes(book.size)}}
        </div>
        <div class="m-2 chips">
          <Chip v-for="(tag, index) in book.tags" :key="index" :label="tag.name" @click="selectTag(tag)" class="m-1 cursor-pointer" style="font-size: 0.8rem;" icon="pi pi-tag" />
        </div>
      </div>

    </div>
  </div>

</template>

<script lang="ts">
import {defineComponent, PropType} from 'vue';

import {Book} from "@/books";
import {formatBytes} from "../formatter";
import {getLanguagePairByLabel} from "@/languages";
import MarkFavorite from "@/components/Bookmarks.vue";
import OverlayPanel from "primevue/overlaypanel";

export default defineComponent({
  name: "BookCard",
  components: {MarkFavorite},
  props: {
    book: {required: true, type: Object as PropType<Book>},
    compactView: {required: false, type: Boolean, default: false},
  },
  emits: ['select:tag', 'select:publisher'],
  data() {
      return {
        windowWidth: window.innerWidth,
        showTagsOverlay: false
      }
  },
  mounted() {
    window.addEventListener('resize', () => this.windowWidth = window.innerWidth);
  },
  computed: {
    isMobile() {
      return this.windowWidth <= 768;
    },
    cardStyle() {
      const style = {
        width: this.compactView?'16rem':'45rem'
      }
      if (this.compactView && this.isMobile) {
        style.width = '6rem'
      }
      return style;
    }
  },
  methods: {
    getLanguagePairByLabel,
    formatBytes,
    showBook() {
      document.location.href = `/book/${this.book.id}`;
    },
    selectTag(tag: {id: number, name: string}) {
      this.$emit('select:tag', tag);
    },

    toggleTagsOverlay(event: Event) {
      (<OverlayPanel>this.$refs.tags).toggle(event);
    }

  }
})

</script>

<style scoped>
.card-plate {
  width: 45rem;
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
  font-size: 1.4rem;
  padding: 1.5rem 0;
  cursor: pointer!important;
  margin-bottom: 0.5rem!important;
  display: -webkit-box!important;
  display: -ms-flexbox!important;
  display: flex!important;
  -webkit-box-pack: center!important;
  -ms-flex-pack: center!important;
  justify-content: center!important;
  text-align: center!important;
}

.book-about {
  max-width: 28rem;
  width: 100%;
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

.book-image {
  border-radius:.75rem!important;
  max-height: 400px;
  max-width: 300px;
  width: 15.9rem;
}

@media (width < 768px) {
  .card-plate {
    padding-left: 0.5rem;
    flex-wrap: nowrap!important;
    border: none!important;
    box-shadow: none!important;
    flex-direction: row;
  }

  .book-title {
    font-size: 0.8rem;
    margin: 0!important;
    padding: 0!important;
  }

  .book-about {
    font-size: 0.7rem;
    max-width: none;
    flex-wrap: wrap;
  }

  .book-image {
    border-radius: 0!important;
    max-height: 150px;
    max-width: 95px;
  }

}
</style>