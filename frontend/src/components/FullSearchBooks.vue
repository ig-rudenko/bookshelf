<template>
    <div id="search-block" class="w-full scroll-mt-6">
        <SearchBookForm
            :initialCompactView="initialCompactView"
            @compactView="(v: boolean) => (compactView = v)"
            :filterData="filters"
            @filtered="
                (f: any) => {
                    filters = f;
                    getBooksList(1, f);
                }
            "
        />
    </div>

    <slot name="after-search" />

    <div class="flex flex-wrap items-center justify-between gap-3 mt-6 mb-4">
        <h2 class="text-lg font-semibold">Каталог</h2>
        <span class="text-sm text-surface-600 dark:text-surface-400" role="status" aria-live="polite">
            {{ loadingBooks ? "Загрузка книг…" : loadError ? "" : results ? "Найдено: " + results.totalCount : "" }}
        </span>
    </div>

    <div :aria-busy="loadingBooks" :class="compactView ? 'flex flex-wrap gap-4 sm:gap-6' : 'book-grid'">
        <template v-if="results && !loadingBooks && !loadError">
            <BookCard
                @click:book="(book, event: MouseEvent) => $emit('click:book', book, event)"
                @select:tag="selectTag"
                @select:publisher="selectPublisher"
                v-for="(book, index) in results.books"
                :key="index"
                :compactView="compactView"
                :book="book"
            />
        </template>

        <template v-else-if="loadingBooks">
            <!--Заглушка-->
            <Skeleton
                v-for="i in [1, 2, 3, 4]"
                :key="i"
                :width="compactView ? '7rem' : '100%'"
                height="12rem"
                class="rounded-xl"
            ></Skeleton>
        </template>
    </div>

    <Paginator
        v-if="results?.totalCount && !loadingBooks && !loadError"
        class="text-xs md:text-base"
        @page="(event: any) => getBooksList(event.page + 1, filters)"
        @update:rows="(value: number) => (results!.perPage = value)"
        :pages="3"
        :always-show="false"
        :first="(results.currentPage - 1) * results.perPage"
        :rows="results.perPage"
        :totalRecords="results.totalCount"
        :rowsPerPageOptions="[10, 25, 50]"
    />

    <div v-else-if="loadError" role="alert" class="flex flex-col items-center gap-3 px-4 py-12 text-center">
        <p>{{ loadError }}</p>
        <Button label="Повторить" icon="pi pi-refresh" outlined @click="restoreFromUrl" />
    </div>
    <div
        v-else-if="results && !loadingBooks && !results.totalCount"
        role="status"
        class="flex flex-col items-center gap-3 px-4 py-12 text-center"
    >
        <h2 class="text-xl font-semibold">Книги не найдены</h2>
        <p class="text-surface-600 dark:text-surface-400">Измените запрос или сбросьте ограничения поиска.</p>
        <Button label="Сбросить поиск и фильтры" icon="pi pi-filter-slash" outlined @click="clearSearch" />
    </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { PaginatedBookResult } from "@/books.ts";
import { createFilterBook, FilterBook } from "@/filters.ts";
import bookService from "@/services/books.ts";
import SearchBookForm from "@/components/SearchBookForm.vue";
import BookCard from "@/components/BookCard.vue";

export default defineComponent({
    name: "FullSearchBooks",
    components: { BookCard, SearchBookForm },
    props: {
        initialPerPage: { required: false, type: Number, default: 25 },
        initialCompactView: { required: false, type: Boolean, default: false },
        authScrollToSearchBlock: { required: false, type: Boolean, default: true },
    },
    emits: ["click:book"],

    data() {
        return {
            results: null as PaginatedBookResult | null,
            lastUrlParams: "",
            filters: new FilterBook(),
            compactView: this.initialCompactView,
            windowWidth: window.innerWidth,
            loadingBooks: false,
            loadError: "",
            requestId: 0,
        };
    },
    mounted() {
        this.restoreFromUrl();
        window.addEventListener("popstate", this.restoreFromUrl);
        window.addEventListener("resize", () => (this.windowWidth = window.innerWidth));
    },
    beforeUnmount() {
        window.removeEventListener("popstate", this.restoreFromUrl);
        this.requestId++;
    },
    computed: {
        isMobile() {
            return this.windowWidth <= 768;
        },
    },
    methods: {
        restoreFromUrl() {
            const params = new URLSearchParams(window.location.search);
            this.filters = createFilterBook({ ...Object.fromEntries(params), tags: params.getAll("tags") });
            return this.getBooksList(
                Number(params.get("page")) || 1,
                this.filters,
                Number(params.get("per-page")) || this.initialPerPage,
                false
            );
        },
        async getBooksList(page: number, filter: null | FilterBook = null, perPage?: number, updateHistory = true) {
            perPage ??= this.results?.perPage || this.initialPerPage;
            const requestId = ++this.requestId;
            this.loadingBooks = true;
            this.loadError = "";
            if (this.authScrollToSearchBlock && this.results)
                document.getElementById("search-block")?.scrollIntoView({ block: "start" });
            try {
                const value = await bookService.getBooksList(page, filter, perPage, updateHistory);
                if (requestId === this.requestId && value) this.results = this.replaceThumb(value);
            } catch {
                if (requestId === this.requestId)
                    this.loadError = "Не удалось загрузить книги. Проверьте соединение и попробуйте ещё раз.";
            } finally {
                if (requestId === this.requestId) this.loadingBooks = false;
            }
        },
        clearSearch() {
            this.filters.clear();
            this.getBooksList(1, this.filters);
        },

        replaceThumb(data: PaginatedBookResult): PaginatedBookResult {
            if (this.isMobile) {
                for (const book of data.books) {
                    book.previewImage = book.previewImage.replace(".png", "_thumb_small.png");
                    console.log(book.previewImage);
                }
            }
            return data;
        },

        selectTag(tag: string) {
            if (!this.filters.tags.includes(tag)) {
                this.filters.tags.push(tag);
                this.getBooksList(1, this.filters);
            }
        },

        selectPublisher(publisherName: string) {
            this.filters.publisher = publisherName;
            this.getBooksList(1, this.filters);
        },
    },
});
</script>
