<template>
    <section class="catalog-shell py-6 md:py-10">
        <div class="flex flex-wrap items-baseline justify-between gap-3 mb-5">
            <h1 class="page-title">{{ title }}</h1>
            <span class="text-sm text-surface-600 dark:text-surface-400" role="status" aria-live="polite">
                {{ loading ? "Загрузка книг…" : result && !loadError ? "Книг: " + result.totalCount : "" }}
            </span>
        </div>

        <SearchBookForm
            :filter-data="filters"
            @filtered="applyFilters"
            @compactView="(value: boolean) => (compactView = value)"
        />

        <p
            v-if="result?.totalCount && kind !== 'favorite' && !loading && !loadError"
            class="mt-4 text-sm text-surface-600 dark:text-surface-400"
        >
            {{ kind === "history" ? "Прочитано страниц в этой выборке:" : "Страниц в этой выборке:" }}
            {{ result.books.reduce((sum, book) => sum + (kind === "history" ? book.readPages || 0 : book.pages), 0) }}
        </p>

        <div class="mt-6" :class="compactView ? 'flex flex-wrap gap-4 sm:gap-6' : 'book-grid'" :aria-busy="loading">
            <template v-if="result && !loading && !loadError">
                <div
                    v-for="book in result.books"
                    :key="book.id"
                    :class="
                        kind === 'history' && !compactView
                            ? 'min-w-0 overflow-hidden rounded-lg border border-surface-200 dark:border-surface-700 bg-surface-0 dark:bg-surface-900'
                            : 'contents'
                    "
                >
                    <div
                        v-if="kind === 'history' && !compactView && book.readPages"
                        class="px-4 py-3 border-b border-surface-200 dark:border-surface-700"
                    >
                        <MeterGroup
                            class="text-xs sm:text-sm"
                            :value="[
                                {
                                    label: readingLabel(book),
                                    value: readingPercent(book),
                                    color: getReadPagesCountColor(readingPercent(book)),
                                    icon: 'pi pi-file',
                                },
                            ]"
                        />
                    </div>
                    <BookCard
                        :book="book"
                        :compact-view="compactView"
                        @select:publisher="selectPublisher"
                        @select:tag="selectTag"
                        :class="{ '!border-0': kind === 'history' && !compactView }"
                    />
                </div>
            </template>
            <Skeleton
                v-else-if="loading"
                v-for="i in 4"
                :key="i"
                :width="compactView ? '7rem' : '100%'"
                height="12rem"
                class="rounded-lg"
            />
        </div>

        <div v-if="loadError" role="alert" class="flex flex-col items-center gap-3 px-4 py-12 text-center">
            <p>{{ loadError }}</p>
            <Button label="Повторить" icon="pi pi-refresh" outlined @click="restoreFromUrl" />
        </div>
        <div
            v-else-if="result && !loading && !result.totalCount"
            role="status"
            class="flex flex-col items-center gap-3 py-10 text-center"
        >
            <h2 class="text-lg font-semibold">{{ filters.urlParams ? "Книги не найдены" : emptyMessage }}</h2>
            <template v-if="filters.urlParams">
                <p class="text-surface-600 dark:text-surface-400">Измените запрос или сбросьте ограничения поиска.</p>
                <Button label="Сбросить поиск и фильтры" outlined @click="clearFilters" />
            </template>
            <a v-else href="/" class="p-button p-button-outlined no-underline">Перейти в каталог</a>
        </div>

        <Paginator
            v-if="result?.totalCount && !loading && !loadError"
            :always-show="false"
            :first="(result.currentPage - 1) * result.perPage"
            :rows="result.perPage"
            :total-records="result.totalCount"
            :rows-per-page-options="[10, 25, 50]"
            @page="(event: any) => loadBooks(event.page + 1, true, event.rows)"
        />
    </section>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue";
import { mapState } from "vuex";
import TimeAgo from "javascript-time-ago";
import ru from "javascript-time-ago/locale/ru";
import BookCard from "@/components/BookCard.vue";
import SearchBookForm from "@/components/SearchBookForm.vue";
import { Book, BookWithReadPages, PaginatedBookResult } from "@/books";
import { createFilterBook, FilterBook } from "@/filters";
import { getReadPagesCountColor } from "@/formatter";
import api from "@/services/api";

type LibraryBook = Book & Partial<Pick<BookWithReadPages, "readPages" | "lastTimeRead">>;
interface LibraryResult extends PaginatedBookResult {
    books: LibraryBook[];
}

TimeAgo.addDefaultLocale(ru);

export default defineComponent({
    name: "LibraryBooks",
    components: { BookCard, SearchBookForm },
    props: {
        kind: { type: String as PropType<"favorite" | "read" | "history">, required: true },
        userID: { type: Number, default: 0 },
    },
    data() {
        return {
            result: null as LibraryResult | null,
            filters: new FilterBook(),
            compactView: false,
            loading: false,
            loadError: "",
            page: 1,
            perPage: 25,
            requestId: 0,
        };
    },
    computed: {
        ...mapState({ loggedIn: (state: any) => state.auth.status.loggedIn }),
        title() {
            return { favorite: "Избранное", read: "Прочитанное", history: "Недавно просмотренные" }[this.kind];
        },
        emptyMessage() {
            return {
                favorite: "Нет избранных книг",
                read: "Пока нет прочитанных книг",
                history: "Нет недавно просмотренных книг",
            }[this.kind];
        },
        endpoint() {
            const suffix = this.kind === "history" ? "last-viewed" : this.kind;
            return this.userID
                ? `/admin/users/${this.userID}/${suffix}`
                : this.kind === "history"
                  ? "/books/last-viewed"
                  : `/bookmarks/${suffix}`;
        },
    },
    watch: {
        userID() {
            this.filters = new FilterBook();
            this.loadBooks(1, false, 25);
        },
    },
    mounted() {
        if (!this.loggedIn) {
            this.$router.push("/login");
            return;
        }
        if (!this.userID) {
            document.title = this.title;
            window.addEventListener("popstate", this.restoreFromUrl);
        }
        this.restoreFromUrl();
    },
    beforeUnmount() {
        window.removeEventListener("popstate", this.restoreFromUrl);
        this.requestId++;
    },
    methods: {
        getReadPagesCountColor,
        restoreFromUrl() {
            if (this.userID) return this.loadBooks(this.page, false);
            const params = new URLSearchParams(window.location.search);
            this.filters = createFilterBook({ ...Object.fromEntries(params), tags: params.getAll("tags") });
            return this.loadBooks(Number(params.get("page")) || 1, false, Number(params.get("per-page")) || 25);
        },
        async loadBooks(page: number, updateHistory = true, perPage?: number) {
            perPage ??= this.perPage;
            const requestId = ++this.requestId;
            this.page = page;
            this.perPage = perPage;
            this.loading = true;
            this.loadError = "";
            const params = new URLSearchParams(`page=${page}&per-page=${perPage}`);
            for (const [key, value] of new URLSearchParams(this.filters.urlParams)) params.append(key, value);
            if (!this.userID && updateHistory) {
                const url = window.location.pathname + "?" + params;
                if (window.location.pathname + window.location.search !== url)
                    history.pushState(history.state, "", url);
            }
            try {
                const { data } = await api.get<LibraryResult>(this.endpoint + "?" + params);
                if (requestId === this.requestId) this.result = data;
            } catch {
                if (requestId === this.requestId)
                    this.loadError = "Не удалось загрузить книги. Проверьте соединение и попробуйте ещё раз.";
            } finally {
                if (requestId === this.requestId) this.loading = false;
            }
        },
        applyFilters(filters: FilterBook) {
            this.filters = filters;
            return this.loadBooks(1);
        },
        clearFilters() {
            this.filters.clear();
            return this.loadBooks(1);
        },
        selectTag(tag: string) {
            if (!this.filters.tags.includes(tag)) {
                this.filters.tags.push(tag);
                return this.loadBooks(1);
            }
        },
        selectPublisher(publisher: string) {
            this.filters.publisher = publisher;
            return this.loadBooks(1);
        },
        readingPercent(book: LibraryBook) {
            return ((book.readPages || 0) / book.pages) * 100;
        },
        readingLabel(book: LibraryBook) {
            const time = book.lastTimeRead ? new TimeAgo("ru-RU").format(new Date(book.lastTimeRead)) : "";
            return `Прочитано страниц: ${book.readPages}/${book.pages}` + (time ? " | " + time : "");
        },
    },
});
</script>
