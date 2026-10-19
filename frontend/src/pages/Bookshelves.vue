<template>
    <section class="page-shell py-6 md:py-10">
        <div class="flex flex-wrap items-center justify-between gap-3 mb-6">
            <h1 class="page-title">Книжные полки</h1>
            <a href="/bookshelves/create" v-if="loggedIn" class="p-button no-underline">
                <i class="pi pi-plus" aria-hidden="true" /> Создать полку
            </a>
        </div>

        <form id="search-block" class="flex flex-wrap items-end gap-3 mb-6" @submit.prevent="getBookshelvesList(1)">
            <div class="w-full sm:w-auto sm:flex-1 min-w-0">
                <label for="bookshelf-search" class="block text-sm mb-2">Название полки</label>
                <IconField class="w-full">
                    <InputIcon class="pi pi-search" />
                    <InputText
                        id="bookshelf-search"
                        class="w-full"
                        v-model="filter.search"
                        placeholder="Поиск по полкам"
                    />
                </IconField>
            </div>
            <div class="flex-1 sm:flex-none min-w-0">
                <label for="bookshelf-visibility" class="block text-sm mb-2">Видимость</label>
                <Select
                    inputId="bookshelf-visibility"
                    class="w-full sm:w-44"
                    v-model="filter.private_"
                    :options="[
                        { label: 'Все полки', value: null },
                        { label: 'Публичные', value: false },
                        { label: 'Приватные', value: true },
                    ]"
                    optionLabel="label"
                    optionValue="value"
                    placeholder="Все полки"
                    @change="getBookshelvesList(1)"
                />
            </div>
            <Button type="submit" icon="pi pi-search" label="Найти" />
        </form>

        <div class="flex flex-wrap justify-center content-center">
            <template v-if="results && !loadingBooks && !loadError">
                <BookshelfRow v-for="bs in results?.bookshelves" :bookshelf="bs" />
            </template>

            <template v-else-if="loadingBooks">
                <!--Заглушка-->
                <Skeleton v-for="i in [1, 2]" :key="i" width="100%" height="20rem" class="m-4 rounded-2xl shadow-xl" />
            </template>
        </div>

        <div v-if="loadError" role="alert" class="flex flex-col items-center gap-3 px-4 py-12 text-center">
            <p>{{ loadError }}</p>
            <Button
                label="Повторить"
                icon="pi pi-refresh"
                outlined
                @click="getBookshelvesList(results?.currentPage || 1)"
            />
        </div>
        <div
            v-else-if="results && !loadingBooks && !results.totalCount"
            role="status"
            class="flex flex-col items-center gap-3 px-4 py-12 text-center"
        >
            <h2 class="text-xl font-semibold">
                {{ hasFilters ? "Полки не найдены" : "Здесь пока нет книжных полок" }}
            </h2>
            <p class="max-w-lg text-surface-600 dark:text-surface-400">
                {{
                    hasFilters
                        ? "Измените запрос или сбросьте фильтры."
                        : "Собирайте книги по темам на своих полках и возвращайтесь к ним в удобное время."
                }}
            </p>
            <Button v-if="hasFilters" label="Сбросить фильтры" outlined @click="clearFilters" />
            <a v-else :href="loggedIn ? '/bookshelves/create' : '/login'" class="p-button no-underline">
                {{ loggedIn ? "Создать полку" : "Войти и создать полку" }}
            </a>
        </div>

        <Paginator
            v-if="results?.totalCount && !loadingBooks && !loadError"
            :always-show="false"
            @page="(event: any) => getBookshelvesList(event.page + 1)"
            @update:rows="(value: number) => (results!.perPage = value)"
            :pages="3"
            :first="(results.currentPage - 1) * results.perPage"
            :rows="results.perPage"
            :totalRecords="results.totalCount"
            :rowsPerPageOptions="[10, 25, 50]"
        />
    </section>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import SearchBookForm from "@/components/SearchBookForm.vue";
import bookshelvesService, { PaginatedBookshelvesResult } from "@/services/bookshelves.ts";
import BookshelfRow from "@/components/BookshelfRow.vue";
import { mapState } from "vuex";
import { createFilterBookshelf, FilterBookshelf } from "@/filters.ts";

export default defineComponent({
    name: "Bookshelves",
    components: { BookshelfRow, SearchBookForm },
    data() {
        return {
            search: this.$route.query.search?.toString() || "",
            windowWidth: window.innerWidth,
            results: null as PaginatedBookshelvesResult | null,
            loadingBooks: false,
            loadError: "",
            filter: new FilterBookshelf(),
        };
    },
    mounted() {
        this.filter = createFilterBookshelf(this.$route.query);
        this.getBookshelvesList(1);
        window.addEventListener("resize", () => (this.windowWidth = window.innerWidth));
    },
    computed: {
        ...mapState({
            loggedIn: (state: any) => state.auth.status.loggedIn,
            user: (state: any) => state.auth.user,
        }),
        isMobile() {
            return this.windowWidth <= 768;
        },
        hasFilters() {
            return Boolean(this.filter.search || this.filter.private_ !== null);
        },
    },

    methods: {
        async getBookshelvesList(page: number) {
            this.loadingBooks = true;
            this.loadError = "";
            try {
                const value = await bookshelvesService.getBookshelvesList(page, this.filter, this.results?.perPage);
                if (value) this.results = value;
            } catch {
                this.loadError = "Не удалось загрузить полки. Проверьте соединение и попробуйте ещё раз.";
            } finally {
                this.loadingBooks = false;
            }
        },
        clearFilters() {
            this.filter.clear();
            this.getBookshelvesList(1);
        },
    },
});
</script>
