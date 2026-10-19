<template>
    <div class="w-full">
        <form class="flex flex-wrap items-center gap-2 sm:gap-3" @submit.prevent="searchBooks">
            <IconField class="w-full sm:w-auto sm:flex-1 min-w-0">
                <InputIcon class="pi pi-search" />
                <InputText
                    id="book-search"
                    class="w-full"
                    v-model="filterData.search"
                    placeholder="Название, автор или тема"
                    aria-label="Поиск книг"
                />
            </IconField>
            <Button type="submit" label="Найти" class="sm:!px-7" />
            <Button
                type="button"
                icon="pi pi-filter"
                label="Фильтры"
                severity="secondary"
                outlined
                :aria-expanded="filtersVisible"
                aria-controls="book-filters"
                @click="toggleFilterBooks"
            />
            <Button
                type="button"
                :icon="compactView ? 'pi pi-list' : 'pi pi-th-large'"
                text
                class="ml-auto sm:ml-0"
                :aria-label="compactView ? 'Полный вид' : 'Компактный вид'"
                :aria-pressed="compactView"
                v-tooltip.bottom="compactView ? 'Полный вид' : 'Компактный вид'"
                @click="toggleCompactView"
            />
        </form>

        <Popover
            ref="filterBooks"
            id="book-filters"
            class="search-filters w-[min(24rem,calc(100vw-2rem))] max-h-[75vh] overflow-y-auto"
            @show="filtersVisible = true"
            @hide="filtersVisible = false"
        >
            <h2 class="text-base font-semibold mb-3 sm:mb-4">Фильтры поиска</h2>
            <div class="flex flex-col gap-1.5 sm:gap-2 mb-3 sm:mb-4">
                <label for="filter.authors">Автор</label>
                <AutoComplete
                    input-class="w-full"
                    class="w-full"
                    inputId="filter.authors"
                    @keydown.enter="doFilter"
                    v-model="draftFilter.authors"
                    :suggestions="authorsList"
                    @complete="searchAuthors"
                />
            </div>
            <div class="flex flex-col gap-1.5 sm:gap-2 mb-3 sm:mb-4">
                <label for="filter.publisher">Издательство</label>
                <AutoComplete
                    input-class="w-full"
                    class="w-full"
                    inputId="filter.publisher"
                    @keydown.enter="doFilter"
                    v-model="draftFilter.publisher"
                    :suggestions="publishersList"
                    @complete="searchPublishers"
                />
            </div>
            <fieldset class="mb-3 sm:mb-4">
                <legend class="mb-2">Количество страниц</legend>
                <div class="grid grid-cols-2 gap-3">
                    <div class="min-w-0 flex flex-col gap-1">
                        <label for="filter.pagesGt" class="text-sm text-surface-600 dark:text-surface-400">От</label>
                        <InputNumber
                            input-class="w-full min-w-0"
                            class="w-full"
                            inputId="filter.pagesGt"
                            @keydown.enter="doFilter"
                            :min="0"
                            :max="draftFilter.pagesLt ?? undefined"
                            v-model="draftFilter.pagesGt"
                        />
                    </div>
                    <div class="min-w-0 flex flex-col gap-1">
                        <label for="filter.pagesLt" class="text-sm text-surface-600 dark:text-surface-400">До</label>
                        <InputNumber
                            input-class="w-full min-w-0"
                            class="w-full"
                            inputId="filter.pagesLt"
                            @keydown.enter="doFilter"
                            :min="draftFilter.pagesGt ?? 0"
                            v-model="draftFilter.pagesLt"
                        />
                    </div>
                </div>
            </fieldset>
            <div class="flex flex-col gap-1.5 sm:gap-2 mb-3 sm:mb-4">
                <label for="filter.language">Язык книги</label>
                <LanguageDropdown
                    input-id="filter.language"
                    :language="draftFilter.language"
                    @update="(language: string | null) => (draftFilter.language = language)"
                    :showClear="true"
                />
            </div>
            <div class="flex flex-col gap-1.5 sm:gap-2 mb-3">
                <label for="filter.tags">Темы</label>
                <InputGroup>
                    <InputText
                        @keydown.enter.prevent="addTag"
                        id="filter.tags"
                        v-model="currentTag"
                        placeholder="Например, Python"
                    />
                    <Button type="button" icon="pi pi-plus" aria-label="Добавить тему" @click="addTag" />
                </InputGroup>
            </div>
            <div class="flex flex-wrap gap-2 mb-4">
                <Chip v-for="(tag, index) in draftFilter.tags" :key="tag" :label="tag" removable>
                    <template #removeicon
                        ><button
                            type="button"
                            @click="removeTag(index)"
                            :aria-label="'Убрать тему ' + tag"
                            class="cursor-pointer p-1"
                        >
                            <i class="pi pi-times" aria-hidden="true" /></button
                    ></template>
                </Chip>
            </div>
            <div class="flex gap-2 pt-3 border-t border-surface-200 dark:border-surface-700">
                <Button label="Применить" @click="doFilter" />
                <Button label="Сбросить" severity="secondary" outlined @click="clearFilter" />
            </div>
        </Popover>

        <div
            v-if="activeFilters.length || filterData.tags.length"
            class="flex flex-wrap items-center gap-2 mt-3 text-sm"
        >
            <Chip v-for="filter in activeFilters" :key="filter.key" :label="filter.label" removable>
                <template #removeicon
                    ><button
                        type="button"
                        @click="removeFilter(filter.key)"
                        :aria-label="'Убрать фильтр: ' + filter.label"
                        class="cursor-pointer p-1"
                    >
                        <i class="pi pi-times" aria-hidden="true" /></button
                ></template>
            </Chip>
            <Chip v-for="(tag, index) in filterData.tags" :key="'tag:' + tag" :label="tag" removable>
                <template #removeicon
                    ><button
                        type="button"
                        @click="
                            filterData.tags.splice(index, 1);
                            searchBooks();
                        "
                        :aria-label="'Убрать тему ' + tag"
                        class="cursor-pointer p-1"
                    >
                        <i class="pi pi-times" aria-hidden="true" /></button
                ></template>
            </Chip>
            <Button label="Сбросить всё" text size="small" @click="clearFilter" />
        </div>
    </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { FilterBook } from "@/filters.ts";
import { AutoCompleteCompleteEvent } from "primevue/autocomplete";
import api from "@/services/api";
import { AxiosResponse } from "axios";
import LanguageDropdown from "@/components/LanguageDropdown.vue";

export default defineComponent({
    name: "SearchBookForm",
    components: { LanguageDropdown },
    emits: ["filtered", "compactView"],
    props: {
        filterData: { required: true, type: FilterBook },
        initialCompactView: { required: false, type: Boolean, default: false },
    },
    data() {
        return {
            currentTag: "",
            draftFilter: new FilterBook(),
            compactView: this.initialCompactView,
            filtersVisible: false,
            publishersList: [] as string[],
            authorsList: [] as string[],
        };
    },
    computed: {
        activeFilters() {
            const filter = this.filterData;
            return [
                { key: "authors", label: "Автор: " + filter.authors, active: Boolean(filter.authors) },
                { key: "publisher", label: "Издательство: " + filter.publisher, active: Boolean(filter.publisher) },
                { key: "language", label: "Язык: " + filter.language, active: Boolean(filter.language) },
                { key: "pagesGt", label: "Страниц от: " + filter.pagesGt, active: filter.pagesGt !== null },
                { key: "pagesLt", label: "Страниц до: " + filter.pagesLt, active: filter.pagesLt !== null },
            ].filter((item) => item.active);
        },
    },
    methods: {
        toggleFilterBooks(event: Event) {
            if (!this.filtersVisible) {
                this.draftFilter = Object.assign(new FilterBook(), this.filterData, {
                    tags: [...this.filterData.tags],
                });
                this.currentTag = "";
            }
            (<any>this.$refs.filterBooks).toggle(event);
        },
        doFilter(): void {
            this.addTag();
            this.draftFilter.search = this.filterData.search;
            (<any>this.$refs.filterBooks).hide();
            this.$emit("filtered", this.draftFilter);
        },
        searchBooks() {
            (<any>this.$refs.filterBooks).hide();
            this.$emit("filtered", this.filterData);
        },
        clearFilter() {
            this.filterData.clear();
            this.currentTag = "";
            this.draftFilter = new FilterBook();
            this.searchBooks();
        },
        removeFilter(key: string) {
            if (key === "authors" || key === "publisher") this.filterData[key] = "";
            if (key === "language" || key === "pagesGt" || key === "pagesLt") this.filterData[key] = null;
            this.searchBooks();
        },
        addTag() {
            const tag = this.currentTag.trim();
            if (tag && !this.draftFilter.tags.includes(tag)) this.draftFilter.tags.push(tag);
            this.currentTag = "";
        },
        removeTag(index: number) {
            this.draftFilter.tags.splice(index, 1);
        },
        toggleCompactView() {
            this.compactView = !this.compactView;
            this.$emit("compactView", this.compactView);
        },

        searchPublishers(event: AutoCompleteCompleteEvent) {
            api.get("/books/publishers?name=" + event.query).then((value: AxiosResponse<string[]>) => {
                this.publishersList = value.data;
            });
        },

        searchAuthors(event: AutoCompleteCompleteEvent) {
            api.get("/books/authors?name=" + event.query).then((value: AxiosResponse<string[]>) => {
                this.authorsList = value.data;
            });
        },
    },
});
</script>
