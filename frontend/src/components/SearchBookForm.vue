<template>

  <IconField class="max-w-24rem w-full" iconPosition="left">
    <InputIcon class="pi pi-search"> </InputIcon>
    <InputText class="w-full" v-model="filterData.search" placeholder="Поиск" @keydown.enter="$emit('filtered', filterData)"/>
  </IconField>

  <Button icon="pi pi-filter" :outlined="!filterData.urlParams" @click="toggleFilterBooks"/>
  <OverlayPanel ref="filterBooks">

    <Button class="mr-1" icon="pi pi-search" @click="doFilter" label="Фильтровать" />
    <Button icon="pi pi-filter-slash" severity="contrast" @click="clearFilter" label="Сбросить" />

    <div class="flex flex-column gap-2 py-2">
      <label for="filter.authors">Авторы</label>
      <InputText class="w-full" id="filter.authors" @keydown.enter="doFilter" v-model="filterData.authors" />
    </div>
    <div class="flex flex-column gap-2 pb-2">
      <label for="filter.publisher">Издательство</label>
      <InputText input-class="w-full" id="filter.authors" @keydown.enter="doFilter" v-model="filterData.publisher" />
    </div>
    <div class="flex flex-column gap-2 pb-2">
      <label for="filter.year">Кол-во страниц</label>
      <div class="flex flex-row gap-1 align-items-center">
        <span>от</span>
        <InputNumber input-class="w-8rem" id="filter.pagesGt" @keydown.enter="doFilter" v-model="filterData.pagesGt" />
        <span>до</span>
        <InputNumber input-class="w-8rem" id="filter.pagesLt" @keydown.enter="doFilter" v-model="filterData.pagesLt" />
      </div>
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
    clearFilter(event: Event) {
      this.filterData.clear()
      this.$emit("filtered", this.filterData);
      this.toggleFilterBooks(event);
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