<template>
    <section v-if="book" class="page-shell py-6 md:py-10">
        <a
            href="/"
            class="inline-flex items-center gap-2 mb-6 text-sm text-surface-600 dark:text-surface-400 hover:text-primary"
        >
            <i class="pi pi-arrow-left" aria-hidden="true" /> К каталогу
        </a>
        <div
            class="grid grid-cols-1 sm:grid-cols-[14rem_minmax(0,1fr)] lg:grid-cols-[24rem_minmax(0,1fr)] gap-x-4 gap-y-6 sm:gap-x-8"
        >
            <a
                :href="'/book/' + book.id + '/show'"
                target="_blank"
                :aria-label="'Читать: ' + book.title"
                class="w-full max-w-sm mx-auto sm:max-w-none self-start rounded-lg lg:row-span-3 lg:sticky lg:top-6"
            >
                <img class="w-full rounded-lg" :alt="book.title" :src="book.previewImage" />
            </a>

            <div class="min-w-0">
                <h1 class="page-title">{{ book.title }}</h1>
                <p class="mt-3 text-surface-700 dark:text-surface-300">{{ book.authors }}</p>
            </div>

            <div class="min-w-0 sm:col-span-2 lg:col-start-2 lg:col-span-1">
                <div class="flex flex-wrap gap-3 mb-5">
                    <Button
                        as="a"
                        :href="'/book/' + book.id + '/show'"
                        target="_blank"
                        icon="pi pi-book"
                        label="Читать"
                        class="no-underline"
                    />
                    <Button
                        as="a"
                        :href="'/api/v1/books/' + book.id + '/download?as-file=true'"
                        icon="pi pi-download"
                        :label="'Скачать · ' + formatBytes(book.size)"
                        outlined
                        class="no-underline whitespace-normal! text-left"
                    />
                </div>

                <div v-if="loggedIn && user" class="mb-4 flex flex-wrap items-center gap-x-6 gap-y-3">
                    <Bookmarks
                        type="favorite"
                        :bookId="book.id"
                        :mark="book.favorite"
                        @updated="(v: boolean) => (book!.favorite = v)"
                    />
                    <Bookmarks
                        type="read"
                        :bookId="book.id"
                        :mark="book.read"
                        @updated="(v: boolean) => (book!.read = v)"
                    />
                </div>
                <div v-if="loggedIn && user?.id == book.userId" class="mb-5 flex flex-wrap items-center gap-2">
                    <span class="mr-1 text-sm text-surface-600 dark:text-surface-400">Управление книгой</span>
                    <Button
                        @click="showEditBook"
                        v-tooltip.bottom="'Редактировать'"
                        icon="pi pi-pencil"
                        text
                        rounded
                        aria-label="Редактировать книгу"
                        severity="secondary"
                    />
                    <Button
                        @click="displayDeleteBookDialog = true"
                        v-tooltip.bottom="'Удалить'"
                        icon="pi pi-trash"
                        text
                        rounded
                        aria-label="Удалить книгу"
                        severity="danger"
                    />
                    <span v-if="book.private" class="text-sm text-surface-600 dark:text-surface-400"
                        ><i class="pi pi-lock mr-1" /> Личная книга</span
                    >
                </div>

                <dl class="flex flex-wrap gap-x-8 gap-y-3 text-sm">
                    <div>
                        <dt class="text-surface-600 dark:text-surface-400">Издательство</dt>
                        <dd>
                            <a
                                :href="'/?publisher=' + encodeURIComponent(book.publisher.name)"
                                class="text-primary hover:underline"
                                >{{ book.publisher.name }}</a
                            >
                        </dd>
                    </div>
                    <div>
                        <dt class="text-surface-600 dark:text-surface-400">Год</dt>
                        <dd>{{ book.year }}</dd>
                    </div>
                    <div>
                        <dt class="text-surface-600 dark:text-surface-400">Язык</dt>
                        <dd>{{ book.language }}</dd>
                    </div>
                    <div>
                        <dt class="text-surface-600 dark:text-surface-400">Объём</dt>
                        <dd>{{ book.pages }} стр.</dd>
                    </div>
                </dl>
                <div class="flex flex-wrap gap-2 mt-5">
                    <a
                        :href="'/?tags=' + encodeURIComponent(tag.name)"
                        v-for="tag in book.tags"
                        :key="tag.id"
                        class="rounded-md bg-primary/10 px-2 py-1 text-sm text-primary hover:bg-primary/20"
                        >{{ tag.name }}</a
                    >
                </div>
                <div v-if="book.bookshelves?.length" class="mt-5">
                    <h2 class="text-sm text-surface-600 dark:text-surface-400 mb-2">На книжных полках</h2>
                    <div class="flex flex-wrap gap-2">
                        <a
                            :href="'/bookshelves?search=' + encodeURIComponent(bookshelf.name)"
                            v-for="bookshelf in book.bookshelves"
                            :key="bookshelf.id"
                            class="inline-flex items-center gap-2 rounded-md border border-surface-300 dark:border-surface-700 px-3 py-2 text-sm hover:text-primary"
                        >
                            <i v-if="bookshelf.private" class="pi pi-lock" aria-hidden="true" />{{ bookshelf.name }}
                        </a>
                    </div>
                </div>
                <BookViewStats v-if="loggedIn" :book="book" class="mt-5" />
            </div>

            <section
                class="sm:col-span-2 lg:col-start-2 lg:col-span-1 border-t border-surface-200 dark:border-surface-800 pt-6"
            >
                <h2 class="text-lg font-semibold mb-3">О книге</h2>
                <div class="book-description" v-html="textToHtml(wrapLinks(book.description))"></div>
            </section>
        </div>
    </section>
    <div v-else-if="loadError" role="alert" class="flex flex-col items-center gap-3 px-4 py-12 text-center">
        <p>{{ loadError }}</p>
        <Button label="Повторить" icon="pi pi-refresh" outlined @click="getBook" />
    </div>
    <div v-else class="page-shell py-6" role="status" aria-label="Загрузка книги">
        <Skeleton width="100%" height="24rem" />
    </div>

    <div v-if="book?.id && canCreateComment" class="flex justify-center">
        <CreateComment @created="getComments(1)" :book-id="book.id" />
    </div>
    <div class="flex flex-wrap flex-col items-center pt-4 p-2 gap-3" v-if="results">
        <Comment
            @comment:delete="getComments(1)"
            @comment:update="getComments(1)"
            v-for="(comment, index) in results.comments"
            :key="index"
            :comment="comment"
        />
        <Paginator
            class="w-full"
            :always-show="false"
            @page="(event: any) => getComments(event.page + 1)"
            @update:rows="(value: number) => (results!.perPage = value)"
            v-model="results.currentPage"
            :rows="results.perPage"
            :totalRecords="results.totalCount"
            :rowsPerPageOptions="[10, 25, 50]"
        />
    </div>
    <Dialog v-model:visible="displayDeleteBookDialog" :show-header="false" modal>
        <div class="text-xl flex items-center gap-4 py-5">
            <i class="pi pi-exclamation-circle text-red-500 !text-3xl" />
            Вы уверены, что хотите удалить эту книгу?
        </div>
        <div class="flex justify-center sm:justify-end gap-2">
            <Button
                type="button"
                severity="success"
                icon="pi pi-times"
                label="Не удалять"
                autofocus
                @click="displayDeleteBookDialog = false"
            />
            <Button type="button" icon="pi pi-trash" severity="danger" label="Удалить" @click="deleteBook" />
        </div>
    </Dialog>
</template>

<script lang="ts">
import { AxiosResponse } from "axios";
import { defineComponent } from "vue";
import { mapState } from "vuex";

import CreateComment from "@/components/CreateComment.vue";
import Bookmarks from "@/components/Bookmarks.vue";
import Comment from "@/components/Comment.vue";

import api from "@/services/api";
import { BookDetail } from "@/books";
import { CommentResult } from "@/comment";
import { formatBytes, textToHtml, wrapLinks } from "../formatter";
import BookViewStats from "@/components/BookViewStats.vue";

export default defineComponent({
    name: "BookPage",
    components: { BookViewStats, Bookmarks, Comment, CreateComment },
    data() {
        return {
            book: null as BookDetail | null,
            results: null as CommentResult | null,
            displayDeleteBookDialog: false,
            loadError: "",
        };
    },
    mounted() {
        this.getBook();
        this.getComments(1);
    },
    computed: {
        ...mapState({
            loggedIn: (state: any) => state.auth.status.loggedIn,
            user: (state: any) => state.auth.user,
        }),

        canCreateComment() {
            return this.loggedIn && this.user?.isStaff;
        },
        bookIdParam() {
            return this.$route.params.id;
        },
    },
    methods: {
        wrapLinks,
        textToHtml,
        formatBytes,
        async getBook() {
            if (this.book) return;
            this.loadError = "";
            try {
                const value = await api.get<BookDetail>(`/books/${this.bookIdParam}`);
                this.book = value.data;
                document.title = this.book.title;
            } catch {
                this.loadError = "Не удалось открыть книгу. Проверьте соединение и попробуйте ещё раз.";
            }
        },
        getComments(page: number) {
            let url = `/comments/book/${this.bookIdParam}?page=${page}`;
            if (this.results?.perPage) url += `&per-page=${this.results.perPage}`;
            api.get(url).then((value: AxiosResponse<CommentResult>) => (this.results = value.data));
        },

        showEditBook() {
            document.location.href = `/book/${this.bookIdParam}/edit`;
        },

        deleteBook() {
            api.delete(`/books/${this.bookIdParam}`).then((value: AxiosResponse) => {
                if (value.status == 204) document.location.href = "/";
            });
        },
    },
});
</script>
