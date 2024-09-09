<template>
  <div class="w-full">
    <div class="py-2 flex w-full justify-content-center">
      <Button :icon="compactView?'pi pi-stop':'pi pi-th-large'" text
              v-tooltip.bottom="compactView?'Полный вид':'Компактный вид'"
              @click="toggleCompactView" />
      <IconField class="max-w-30rem w-full" iconPosition="left">
        <InputIcon class="pi pi-search"/>
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
          <AutoComplete input-class="w-full" id="filter.authors" @keydown.enter="doFilter" v-model="filterData.publisher"
                        :suggestions="publishersList" @complete="searchPublishers" />
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
          <label for="book.language">Язык книги</label>
          <LanguageDropdown :language="filterData.language" @update="(l: string) => filterData.language=l" :showClear="true"/>
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
    </div>

    <div class="flex justify-content-center">
      <Chip v-if="filterData.authors" icon="pi pi-users" :label="'Авторы: '+filterData.authors" class="mr-1" removable>
        <template #removeicon><i @click="()=>{filterData.authors='';doFilter()}" class="pi pi-times cursor-pointer ml-2"/></template>
      </Chip>
      <Chip v-if="filterData.publisher" icon="pi pi-building" :label="'Издательство: '+filterData.publisher" class="mr-1" removable>
        <template #removeicon><i @click="()=>{filterData.publisher='';doFilter()}" class="pi pi-times cursor-pointer ml-2"/></template>
      </Chip>
      <Chip v-for="(tag, index) in filterData.tags" :key="index" :label="tag" icon="pi pi-tag" class="mr-1" removable>
        <template #removeicon><i @click="()=>{removeTag(index);doFilter()}" class="pi pi-times cursor-pointer ml-2"/></template>
      </Chip>
    </div>
  </div>

</template>

<script lang="ts">
import {defineComponent} from 'vue'
import OverlayPanel from "primevue/overlaypanel";
import {FilterBook} from "@/filters.ts";
import {AutoCompleteCompleteEvent} from "primevue/autocomplete";
import api from "@/services/api.ts";
import {AxiosResponse} from "axios";
import LanguageDropdown from "@/components/LanguageDropdown.vue";

export default defineComponent({
  name: "SearchBookForm",
  components: {LanguageDropdown},
  emits: ["filtered", "compactView"],
  props: {
    filterData: {required: true, type: FilterBook},
    initialCompactView: {required: false, type: Boolean, default: false},
  },
  data() {
      return {
        currentTag: "",
        compactView: this.initialCompactView,
        publishersList: [] as string[],
      }
  },
  methods: {
    toggleFilterBooks(event: Event) {
      (<OverlayPanel>this.$refs.filterBooks).toggle(event);
    },
    doFilter(): void {
      (<OverlayPanel>this.$refs.filterBooks).hide();
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
    toggleCompactView() {
      this.compactView = !this.compactView;
      this.$emit("compactView", this.compactView);
    },

    searchPublishers(event: AutoCompleteCompleteEvent) {
      api.get("/books/publishers?name="+event.query)
          .then(
              (value: AxiosResponse<string[]>) => {
                this.publishersList = value.data;
              }
          )
    },
  },
})
</script>

<style scoped>

</style>