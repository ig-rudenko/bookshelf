<template>

  <IconField class="max-w-24rem w-full" iconPosition="left">
    <InputIcon class="pi pi-search"> </InputIcon>
    <InputText class="w-full" v-model="search" placeholder="Search" />
  </IconField>

  <Button icon="pi pi-filter" @click="toggleFilterBooks"/>
  <OverlayPanel ref="filterBooks">
    <div class="flex flex-column gap-2 pb-2 w-25rem w-full">
      <label for="filter.title">Название книги</label>
      <InputText id="filter.title" class="w-full" v-model="title"/>
    </div>
    <div class="flex flex-column gap-2 pb-2">
      <label for="filter.authors">Авторы</label>
      <InputText class="w-full" id="filter.authors" v-model="authors" />
    </div>
    <div class="flex flex-column gap-2 pb-2">
      <label for="filter.publisher">Издательство</label>
      <InputText input-class="w-full" id="filter.authors" v-model="publisher" />
    </div>
    <div class="flex flex-column gap-2 pb-2">
      <label for="filter.year">Год издания</label>
      <InputNumber input-class="w-6rem" id="filter.year" v-model="year" suffix=" г." :useGrouping="false"/>
    </div>
  </OverlayPanel>

</template>

<script lang="ts">
import {defineComponent} from 'vue'
import OverlayPanel from "primevue/overlaypanel";

export default defineComponent({
  name: "SearchBookForm",
  data() {
      return {
        search: "",
        title: "",
        authors: "",
        publisher: "",
        year: "",
      }
  },
  methods: {
    toggleFilterBooks(event: Event) {
      (<OverlayPanel>this.$refs.filterBooks).toggle(event);
    }
  },
})
</script>

<style scoped>

</style>