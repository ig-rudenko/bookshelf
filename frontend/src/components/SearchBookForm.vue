<template>

  <IconField class="max-w-24rem w-full" iconPosition="left">
    <InputIcon class="pi pi-search"> </InputIcon>
    <InputText class="w-full" v-model="filterData.search" placeholder="Search" />
  </IconField>

  <Button icon="pi pi-filter" @click="toggleFilterBooks"/>
  <OverlayPanel ref="filterBooks">
    <div class="flex flex-column gap-2 pb-2 w-25rem w-full">
      <label for="filter.title">Название книги</label>
      <InputText id="filter.title" class="w-full" v-model="filterData.title"/>
    </div>
    <div class="flex flex-column gap-2 pb-2">
      <label for="filter.authors">Авторы</label>
      <InputText class="w-full" id="filter.authors" v-model="filterData.authors" />
    </div>
    <div class="flex flex-column gap-2 pb-2">
      <label for="filter.publisher">Издательство</label>
      <InputText input-class="w-full" id="filter.authors" v-model="filterData.publisher" />
    </div>
    <div class="flex flex-column gap-2 pb-2">
      <label for="filter.year">Год издания</label>
      <InputNumber input-class="w-6rem" id="filter.year" v-model="filterData.year" suffix=" г." :useGrouping="false"/>
    </div>
    <div class="flex flex-column gap-2 pb-2">
      <label for="filter.tags">Теги</label>
      <InputGroup>
        <InputText @keydown.enter="addTag" id="filter.tags" v-cloak v-model="currentTag" separator="," aria-describedby="book.tags-help" />
        <Button icon="pi pi-plus" severity="success" @click="addTag" />
      </InputGroup>
    </div>
    <div class="flex flex-wrap lg:max-w-20rem">
      <Chip v-for="(tag, index) in filterData.tags" :key="index" :label="tag" icon="pi pi-tag" class="m-1" removable >
        <template #removeicon>
          <i @click="removeTag(index)" class="pi pi-times cursor-pointer ml-2" />
        </template>
      </Chip>
    </div>

    <Button class="mt-2" icon="pi pi-search" @click="doFilter"/>
  </OverlayPanel>

</template>

<script lang="ts">
import {defineComponent} from 'vue'
import OverlayPanel from "primevue/overlaypanel";
import {FilterBook} from "@/filters.ts";

export default defineComponent({
  name: "SearchBookForm",
  emits: ["filtered"],
  props: {
    filterData: {required: true, type: FilterBook},
  },
  data() {
      return {
        currentTag: ""
      }
  },
  methods: {
    toggleFilterBooks(event: Event) {
      (<OverlayPanel>this.$refs.filterBooks).toggle(event);
    },
    doFilter(event: Event): void {
      this.toggleFilterBooks(event);
      this.$emit("filtered", this.filterData);
    },
    addTag() {
      if (this.currentTag.length > 0 && !this.filterData.tags.includes(this.currentTag)) {
        this.filterData.tags.push(this.currentTag);
        this.currentTag = "";
      }
    },
    removeTag(index: number) {
      this.filterData.tags.splice(index, 1);
    },
  },
})
</script>

<style scoped>

</style>