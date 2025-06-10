<template>

  <div
      class="flex md:flex-wrap border-gray-400 dark:border-gray-600 rounded-xl shadow-md hover:shadow-xl items-center relative"
      :class="{'w-full md:w-[45rem] border-1': !compactView}"
  >
    <div v-if="showImage" class="border-r-1 h-full flex items-center border-gray-400 dark:border-gray-600"
         :class="{ 'border-none': compactView}">
      <img @click="$emit('click:book', book.id)" :src="book.previewImage"
           class="max-h-[250px] max-w-[150px] sm:max-h-[300px] sm:max-w-[200px] md:max-h-[400px] md:max-w-[300px] w-[15.9rem] rounded-l-xl cursor-pointer"
           :class="{ 'rounded-xl border-1 hover:shadow-xl border-gray-400 dark:border-gray-600': compactView, ...imageClasses}"
           alt="book"/>
    </div>

    <div class="max-w-[28rem] w-full flex flex-col items-center p-2 text-sm" v-if="!compactView">
      <div class="text-sm sm:text-xl text-center">
        <a :href="'/book/'+book.id">{{ book.title }}</a>
        <Badge v-tooltip="'Данную книгу кроме вас никто не видит'"
               class="absolute top-[10px] right-[10px] cursor-pointer" v-if="book.private" severity="success"
               size="large">
          <i class="pi pi-lock" style="font-size: 1.25rem"/>
        </Badge>
      </div>

      <div class="items-center flex m-2 flex-wrap justify-center gap-1">
        <span v-if="!isMobile" class="mr-2">
          Издательство
        </span>
        <i class="pi pi-building mr-2"/>
        <span @click="$emit('select:publisher', book.publisher.name)"
              class="text-primary cursor-pointer text-center">
          {{ book.publisher.name }}
        </span>
        <span class="ml-2 text-xs sm:text-sm">{{ book.year }} г.</span>
      </div>

      <div class="flex items-center" :style="{'flex-direction': isMobile?'row':'column'}">

        <div v-if="isMobile">
          <i class="pi pi-tag" @click="toggleTagsOverlay"/>
          <Popover ref="tags">
            <div class="text-sm pb-2">Теги:</div>
            <div class="flex flex-wrap gap-1">
              <Badge v-for="(tag, index) in book.tags" :key="index"
                     @click="selectTag(tag.name)" class="cursor-pointer" style="font-size: 0.8rem;" icon="pi pi-tag">
                {{ tag.name }}
              </Badge>
            </div>
          </Popover>
        </div>

        <div class="m-2 flex flex-row items-center">
          <span v-if="!isMobile" class="mr-2">Язык книги: {{ book.language }}</span>
          <img :alt="book.language" :src="`https://flagcdn.com/${getLanguagePairByLabel(book.language).code}.svg`"
               class="border-1 border-gray-400 w-[22px]"/>
        </div>

      </div>

      <div v-if="!isMobile" class="flex flex-col items-center">

        <div class="m-2 text-center flex flex-row items-center">
          <i class="pi pi-users mr-2"/>
          <span>{{ book.authors }}</span>
        </div>

        <div class="m-2 text-center">
          <i class="pi pi-book mx-2"/>{{ book.pages }} стр. <i class="pi pi-file mx-2"/>{{ formatBytes(book.size) }}
        </div>
        <div class="flex items-center justify-center flex-wrap gap-1">
          <Badge v-for="(tag, index) in book.tags" :key="index"
                 @click="selectTag(tag.name)" class="cursor-pointer" style="font-size: 0.8rem;" icon="pi pi-tag">
            {{ tag.name }}
          </Badge>
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

export default defineComponent({
  name: "BookCard",
  components: {MarkFavorite},
  props: {
    book: {required: true, type: Object as PropType<Book>},
    compactView: {required: false, type: Boolean, default: false},
    showImage: {required: false, type: Boolean, default: true},
    imageClasses: {required: false, type: Object as PropType<{ [key: string]: boolean }>, default: {'': false}},
  },
  emits: ['select:tag', 'select:publisher', 'click:book'],
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
      return this.windowWidth <= 568;
    },
  },
  methods: {
    getLanguagePairByLabel,
    formatBytes,
    showBook() {

    },
    selectTag(tag: string) {
      this.$emit('select:tag', tag);
    },

    toggleTagsOverlay(event: Event) {
      (<any>this.$refs.tags).toggle(event);
    }

  }
})

</script>
